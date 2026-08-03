"""Local transcription adapter for Argmax WhisperKit + SpeakerKit CLI.

The native JSON/RTTM output is preserved and also converted into the stable
``raw_transcription.json`` shape already consumed by ``normalize_transcript``.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional


DEFAULT_MODEL = "large-v3-v20240930_626MB"
CLI_CANDIDATES = ("whisperkit-cli", "argmax-cli")


class WhisperKitError(RuntimeError):
    """Local WhisperKit transcription failed with an actionable message."""


_CJK_CHARACTER = r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"


def _normalize_rttm_text(value: str) -> str:
    text = re.sub(r"\s+", " ", value).strip()
    text = re.sub(rf"(?<={_CJK_CHARACTER}) ", "", text)
    return re.sub(rf" (?={_CJK_CHARACTER})", "", text)


def find_whisperkit_cli(explicit: Optional[str] = None) -> Optional[str]:
    """Find the Homebrew CLI or an explicitly configured executable."""
    configured = explicit or os.environ.get("WHISPERKIT_CLI", "").strip()
    if configured:
        candidate = shutil.which(configured)
        if candidate:
            return candidate
        path = Path(configured).expanduser()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path.resolve())
        return None
    for name in CLI_CANDIDATES:
        candidate = shutil.which(name)
        if candidate:
            return candidate
    return None


def build_whisperkit_command(
    executable: str,
    audio_path: Path,
    report_dir: Path,
    *,
    model: str = DEFAULT_MODEL,
    model_path: Optional[Path] = None,
    language: Optional[str] = "zh",
    diarization: bool = True,
    speaker_count: int = 0,
    diarization_model_path: Optional[Path] = None,
) -> list[str]:
    """Build the long-audio-safe Argmax CLI command."""
    command = [
        str(executable),
        "transcribe",
        "--audio-path",
        str(Path(audio_path)),
    ]
    if model_path is not None:
        command.extend(["--model-path", str(Path(model_path))])
    else:
        command.extend(["--model", model])
    command.extend([
        "--word-timestamps",
        "--report",
        "--report-path",
        str(Path(report_dir)),
        "--incremental-loading",
        "--chunking-strategy",
        "vad",
    ])
    if language:
        command.extend(["--language", language])
    if diarization:
        command.append("--diarization")
        if speaker_count > 0:
            command.extend(["--diarization-num-speakers", str(speaker_count)])
        if diarization_model_path is not None:
            command.extend(
                ["--diarization-model-path", str(Path(diarization_model_path))]
            )
    return command


def parse_rttm_output(output: str) -> list[dict[str, Any]]:
    """Parse SpeakerKit RTTM lines, including multi-word orthography fields."""
    segments: list[dict[str, Any]] = []
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line.startswith("SPEAKER "):
            continue
        fields = line.split()
        # SpeakerKit adds four trailing fields after a variable-width text field:
        # <NA> <speaker> <NA> <NA>.
        if len(fields) < 10:
            continue
        try:
            start = float(fields[3])
            duration = float(fields[4])
        except (TypeError, ValueError):
            continue
        text = _normalize_rttm_text(" ".join(fields[5:-4]))
        speaker = fields[-3]
        if not text or text == "<NA>":
            continue
        end = start + duration
        if duration < 0:
            # SpeakerKit can emit a negative duration for a short turn between
            # two adjacent segments. Its computed end is still usable; anchor
            # the repaired start to the preceding turn instead of preserving
            # an impossible end-before-start interval.
            previous_end = segments[-1]["end"] if segments else end
            start = min(previous_end, end)
        segments.append(
            {
                "start": start,
                "end": max(start, end),
                "text": text,
                "speaker": speaker,
            }
        )
    return sorted(segments, key=lambda item: (item["start"], item["end"]))


def _milliseconds(value: Any) -> int:
    try:
        return max(0, round(float(value) * 1000))
    except (TypeError, ValueError):
        return 0


def _native_end_seconds(native: dict[str, Any]) -> float:
    ends: list[float] = []
    for segment in native.get("segments") or []:
        if not isinstance(segment, dict):
            continue
        try:
            ends.append(float(segment.get("end", 0)))
        except (TypeError, ValueError):
            pass
        for word in segment.get("words") or []:
            if not isinstance(word, dict):
                continue
            try:
                ends.append(float(word.get("end", 0)))
            except (TypeError, ValueError):
                pass
    return max(ends, default=0.0)


def canonicalize_whisperkit_result(
    native: dict[str, Any],
    diarized_segments: list[dict[str, Any]],
) -> dict[str, Any]:
    """Convert WhisperKit JSON plus optional RTTM into the ingest contract."""
    if not isinstance(native, dict):
        raise WhisperKitError("WhisperKit JSON 顶层不是对象。")

    paragraphs: list[dict[str, Any]] = []
    if diarized_segments:
        for item in diarized_segments:
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            start = _milliseconds(item.get("start", 0))
            end = _milliseconds(item.get("end", item.get("start", 0)))
            paragraphs.append(
                {
                    "SpeakerId": str(item.get("speaker", "")),
                    "Words": [{"Start": start, "End": end, "Text": text}],
                }
            )
    else:
        for segment in native.get("segments") or []:
            if not isinstance(segment, dict):
                continue
            canonical_words: list[dict[str, Any]] = []
            for word in segment.get("words") or []:
                if not isinstance(word, dict):
                    continue
                text = str(word.get("word", ""))
                if not text:
                    continue
                canonical_words.append(
                    {
                        "Start": _milliseconds(word.get("start", segment.get("start", 0))),
                        "End": _milliseconds(word.get("end", segment.get("end", 0))),
                        "Text": text,
                    }
                )
            if not canonical_words:
                text = str(segment.get("text", "")).strip()
                if text:
                    canonical_words.append(
                        {
                            "Start": _milliseconds(segment.get("start", 0)),
                            "End": _milliseconds(segment.get("end", 0)),
                            "Text": text,
                        }
                    )
            if canonical_words:
                paragraphs.append({"Words": canonical_words})

    if not paragraphs:
        raise WhisperKitError("WhisperKit 结果中没有可读的 segments/words。")

    diarized_end = max(
        (float(item.get("end", 0)) for item in diarized_segments), default=0.0
    )
    duration_ms = _milliseconds(max(_native_end_seconds(native), diarized_end))
    return {
        "Provider": "whisperkit",
        "Transcription": {
            "AudioInfo": {
                "Duration": duration_ms,
                "Language": native.get("language") or "unknown",
            },
            "Paragraphs": paragraphs,
            "Text": native.get("text", ""),
        },
    }


def write_canonical_transcription(
    native: dict[str, Any],
    diarized_segments: list[dict[str, Any]],
    destination: Path,
) -> Path:
    """Write canonical ``raw_transcription.json`` and return its path."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canonical = canonicalize_whisperkit_result(native, diarized_segments)
    destination.write_text(
        json.dumps(canonical, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return destination


def transcribe_with_whisperkit(
    audio_path: Path,
    out_dir: Path,
    *,
    executable: str,
    model: str = DEFAULT_MODEL,
    model_path: Optional[Path] = None,
    language: Optional[str] = "zh",
    diarization: bool = True,
    speaker_count: int = 0,
    diarization_model_path: Optional[Path] = None,
) -> dict[str, Path]:
    """Run WhisperKit, preserve native artifacts, and write canonical JSON."""
    audio_path = Path(audio_path).resolve()
    out_dir = Path(out_dir).resolve()
    native_dir = out_dir / "whisperkit_native"
    native_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "whisperkit.log"
    command = build_whisperkit_command(
        executable,
        audio_path,
        native_dir,
        model=model,
        model_path=model_path,
        language=language,
        diarization=diarization,
        speaker_count=speaker_count,
        diarization_model_path=diarization_model_path,
    )

    output_chunks: list[str] = []
    with log_path.open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(command) + "\n\n")
        log.flush()
        try:
            process = subprocess.Popen(
                command,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
            )
        except OSError as exc:
            raise WhisperKitError(f"无法启动 WhisperKit CLI：{exc}") from exc

        assert process.stdout is not None
        with process.stdout:
            for chunk in process.stdout:
                output_chunks.append(chunk)
                log.write(chunk)
                log.flush()
                sys.stdout.write(chunk)
                sys.stdout.flush()
        return_code = process.wait()

    combined_output = "".join(output_chunks)
    if return_code != 0:
        tail = "\n".join(combined_output.splitlines()[-20:])
        raise WhisperKitError(
            f"WhisperKit CLI 退出码 {return_code}。\n"
            f"日志：{log_path}\n{tail}"
        )

    native_json_path = native_dir / f"{audio_path.stem}.json"
    native_srt_path = native_dir / f"{audio_path.stem}.srt"
    if not native_json_path.exists():
        raise WhisperKitError(
            f"WhisperKit 执行成功但没有生成 JSON 报告：{native_json_path}\n"
            f"日志：{log_path}"
        )
    try:
        native = json.loads(native_json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WhisperKitError(f"WhisperKit JSON 报告无法解析：{exc}") from exc

    diarized_segments = parse_rttm_output(combined_output) if diarization else []
    if diarization and not diarized_segments:
        raise WhisperKitError(
            "已请求说话人分离，但 CLI 没有生成任何 RTTM 结果。\n"
            f"日志：{log_path}"
        )
    canonical_path = write_canonical_transcription(
        native, diarized_segments, out_dir / "raw_transcription.json"
    )
    artifacts = {
        "raw": canonical_path,
        "native_json": native_json_path,
        "log": log_path,
    }
    if native_srt_path.exists():
        artifacts["srt"] = native_srt_path
    return artifacts
