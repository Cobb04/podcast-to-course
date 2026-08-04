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
    prompt: Optional[str] = None,
    concurrent_worker_count: int = 4,
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
    if prompt and prompt.strip():
        command.extend(["--prompt", prompt.strip()])
    command.extend(["--concurrent-worker-count", str(concurrent_worker_count)])
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


def _physical_duration_seconds(native: dict[str, Any]) -> float:
    timings = native.get("timings") or {}
    try:
        duration = float(timings.get("inputAudioSeconds", 0))
    except (TypeError, ValueError):
        duration = 0.0
    return duration if duration > 0 else _native_end_seconds(native)


def _flatten_native_words(native: dict[str, Any]) -> list[dict[str, Any]]:
    words: list[dict[str, Any]] = []
    for segment in native.get("segments") or []:
        if not isinstance(segment, dict):
            continue
        for word in segment.get("words") or []:
            if not isinstance(word, dict):
                continue
            text = str(word.get("word", ""))
            if not text:
                continue
            try:
                start = float(word.get("start", segment.get("start", 0)))
                end = float(word.get("end", segment.get("end", start)))
            except (TypeError, ValueError):
                continue
            words.append(
                {"start": max(0.0, start), "end": max(start, end), "text": text}
            )
    return sorted(words, key=lambda item: (item["start"], item["end"]))


def _native_word_paragraphs(
    native: dict[str, Any], diarized_segments: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Keep WhisperKit words verbatim and use RTTM only for speaker labels."""
    words = _flatten_native_words(native)
    if not words or not diarized_segments:
        return []

    physical_duration = _physical_duration_seconds(native)
    diarization_end = max(
        (float(item.get("end", 0)) for item in diarized_segments), default=0.0
    )
    supported_end = max(physical_duration, diarization_end)
    paragraphs: list[dict[str, Any]] = []
    active: list[tuple[int, dict[str, Any]]] = []
    next_segment = 0
    previous_speaker = ""

    for word in words:
        start = word["start"]
        end = word["end"]
        if supported_end > 0 and start > supported_end:
            continue

        active = [
            pair for pair in active if float(pair[1].get("end", 0)) >= start
        ]
        while next_segment < len(diarized_segments):
            segment = diarized_segments[next_segment]
            if float(segment.get("start", 0)) > end:
                break
            active.append((next_segment, segment))
            next_segment += 1

        best: Optional[tuple[float, int, str]] = None
        for index, segment in active:
            overlap = max(
                0.0,
                min(end, float(segment.get("end", 0)))
                - max(start, float(segment.get("start", 0))),
            )
            if overlap <= 0:
                continue
            candidate = (overlap, -index, str(segment.get("speaker", "")))
            if best is None or candidate[:2] > best[:2]:
                best = candidate

        speaker = best[2] if best else previous_speaker
        if not speaker:
            speaker = str(diarized_segments[0].get("speaker", ""))
        previous_speaker = speaker

        output_start = min(start, physical_duration) if physical_duration else start
        output_end = min(end, physical_duration) if physical_duration else end
        canonical_word = {
            "Start": _milliseconds(output_start),
            "End": _milliseconds(max(output_start, output_end)),
            "Text": word["text"],
        }
        if not paragraphs or paragraphs[-1].get("SpeakerId") != speaker:
            paragraphs.append({"SpeakerId": speaker, "Words": []})
        paragraphs[-1]["Words"].append(canonical_word)

    return paragraphs


def build_transcription_metrics(
    native: dict[str, Any],
    diarized_segments: list[dict[str, Any]],
    paragraphs: list[dict[str, Any]],
) -> dict[str, Any]:
    native_words = _flatten_native_words(native)
    canonical_words = [
        word
        for paragraph in paragraphs
        for word in (paragraph.get("Words") or [])
        if isinstance(word, dict)
    ]
    physical_duration = _physical_duration_seconds(native)
    native_end = _native_end_seconds(native)
    timings = native.get("timings") or {}
    try:
        pipeline_seconds = float(timings.get("fullPipeline", 0))
    except (TypeError, ValueError):
        pipeline_seconds = 0.0
    speakers = {
        str(paragraph.get("SpeakerId"))
        for paragraph in paragraphs
        if paragraph.get("SpeakerId") not in (None, "")
    }
    native_timestamp_order_violations = 0
    negative_duration_count = 0
    previous_start: Optional[float] = None
    for segment in native.get("segments") or []:
        if not isinstance(segment, dict):
            continue
        for word in segment.get("words") or []:
            if not isinstance(word, dict):
                continue
            try:
                start = float(word.get("start", segment.get("start", 0)))
                end = float(word.get("end", segment.get("end", start)))
            except (TypeError, ValueError):
                continue
            if previous_start is not None and start < previous_start:
                native_timestamp_order_violations += 1
            if end < start:
                negative_duration_count += 1
            previous_start = start

    canonical_timestamp_order_violations = 0
    previous_canonical_start: Optional[int] = None
    for word in canonical_words:
        start = int(word.get("Start", 0))
        if previous_canonical_start is not None and start < previous_canonical_start:
            canonical_timestamp_order_violations += 1
        previous_canonical_start = start

    canonical_end_ms = max(
        (int(word.get("End", 0)) for word in canonical_words), default=0
    )
    coverage_ratio = (
        min(1.0, canonical_end_ms / (physical_duration * 1000))
        if physical_duration > 0
        else None
    )
    dropped_word_count = max(0, len(native_words) - len(canonical_words))
    warnings: list[str] = []
    drift_warning_threshold = max(0.5, physical_duration * 0.002)
    if physical_duration > 0 and native_end - physical_duration > drift_warning_threshold:
        warnings.append("native timestamps exceed physical audio duration")
    if dropped_word_count:
        warnings.append(f"{dropped_word_count} unsupported trailing word(s) dropped")
    if native_timestamp_order_violations:
        warnings.append(
            f"{native_timestamp_order_violations} native timestamp order violation(s)"
        )
    if canonical_timestamp_order_violations:
        warnings.append(
            f"{canonical_timestamp_order_violations} canonical timestamp order violation(s)"
        )
    if negative_duration_count:
        warnings.append(f"{negative_duration_count} negative word duration(s)")
    return {
        "audio_duration_seconds": physical_duration,
        "native_last_timestamp_seconds": native_end,
        "timestamp_drift_seconds": native_end - physical_duration,
        "native_segment_count": len(native.get("segments") or []),
        "native_word_count": len(native_words),
        "canonical_word_count": len(canonical_words),
        "dropped_word_count": dropped_word_count,
        "canonical_paragraph_count": len(paragraphs),
        "diarization_turn_count": len(diarized_segments),
        "speaker_count": len(speakers),
        "native_timestamp_order_violations": native_timestamp_order_violations,
        "canonical_timestamp_order_violations": canonical_timestamp_order_violations,
        "negative_duration_count": negative_duration_count,
        "coverage_ratio": coverage_ratio,
        "pipeline_seconds": pipeline_seconds,
        "speed_factor": (
            physical_duration / pipeline_seconds
            if physical_duration > 0 and pipeline_seconds > 0
            else None
        ),
        "warnings": warnings,
    }


def canonicalize_whisperkit_result(
    native: dict[str, Any],
    diarized_segments: list[dict[str, Any]],
) -> dict[str, Any]:
    """Convert WhisperKit JSON plus optional RTTM into the ingest contract."""
    if not isinstance(native, dict):
        raise WhisperKitError("WhisperKit JSON 顶层不是对象。")

    paragraphs: list[dict[str, Any]] = []
    if diarized_segments:
        paragraphs = _native_word_paragraphs(native, diarized_segments)
        if not paragraphs:
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
        physical_duration = _physical_duration_seconds(native)
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
                try:
                    start = float(word.get("start", segment.get("start", 0)))
                    end = float(word.get("end", segment.get("end", start)))
                except (TypeError, ValueError):
                    continue
                if physical_duration > 0 and start > physical_duration:
                    continue
                output_start = (
                    min(start, physical_duration) if physical_duration else start
                )
                output_end = min(end, physical_duration) if physical_duration else end
                canonical_words.append(
                    {
                        "Start": _milliseconds(output_start),
                        "End": _milliseconds(max(output_start, output_end)),
                        "Text": text,
                    }
                )
            if not canonical_words:
                text = str(segment.get("text", "")).strip()
                try:
                    segment_start = float(segment.get("start", 0))
                    segment_end = float(segment.get("end", segment_start))
                except (TypeError, ValueError):
                    segment_start = segment_end = 0.0
                if text and not (
                    physical_duration > 0 and segment_start > physical_duration
                ):
                    output_start = (
                        min(segment_start, physical_duration)
                        if physical_duration
                        else segment_start
                    )
                    output_end = (
                        min(segment_end, physical_duration)
                        if physical_duration
                        else segment_end
                    )
                    canonical_words.append(
                        {
                            "Start": _milliseconds(output_start),
                            "End": _milliseconds(max(output_start, output_end)),
                            "Text": text,
                        }
                    )
            if canonical_words:
                paragraphs.append({"Words": canonical_words})

    if not paragraphs:
        raise WhisperKitError("WhisperKit 结果中没有可读的 segments/words。")

    duration_ms = _milliseconds(_physical_duration_seconds(native))
    canonical_text = "".join(
        str(word.get("Text", ""))
        for paragraph in paragraphs
        for word in (paragraph.get("Words") or [])
        if isinstance(word, dict)
    )
    canonical = {
        "Provider": "whisperkit",
        "Transcription": {
            "AudioInfo": {
                "Duration": duration_ms,
                "Language": native.get("language") or "unknown",
            },
            "Paragraphs": paragraphs,
            "Text": canonical_text,
        },
    }
    canonical["Metrics"] = build_transcription_metrics(
        native, diarized_segments, paragraphs
    )
    return canonical


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
    prompt: Optional[str] = None,
    concurrent_worker_count: int = 4,
) -> dict[str, Path]:
    """Run WhisperKit, preserve native artifacts, and write canonical JSON."""
    audio_path = Path(audio_path).resolve()
    out_dir = Path(out_dir).resolve()
    if model_path is not None and not Path(model_path).expanduser().is_dir():
        raise WhisperKitError(f"WhisperKit 模型目录不存在：{model_path}")
    if (
        diarization
        and diarization_model_path is not None
        and not Path(diarization_model_path).expanduser().is_dir()
    ):
        raise WhisperKitError(f"SpeakerKit 模型目录不存在：{diarization_model_path}")
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
        prompt=prompt,
        concurrent_worker_count=concurrent_worker_count,
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
    rttm_path = native_dir / f"{audio_path.stem}.rttm"
    rttm_lines = [
        line.strip()
        for line in combined_output.splitlines()
        if line.strip().startswith("SPEAKER ")
    ]
    rttm_path.write_text(
        "\n".join(rttm_lines) + ("\n" if rttm_lines else ""),
        encoding="utf-8",
    )
    canonical = json.loads(canonical_path.read_text(encoding="utf-8"))
    metrics_path = out_dir / "transcription_metrics.json"
    metrics_path.write_text(
        json.dumps(canonical.get("Metrics", {}), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    artifacts = {
        "raw": canonical_path,
        "native_json": native_json_path,
        "log": log_path,
        "rttm": rttm_path,
        "metrics": metrics_path,
    }
    if native_srt_path.exists():
        artifacts["srt"] = native_srt_path
    return artifacts
