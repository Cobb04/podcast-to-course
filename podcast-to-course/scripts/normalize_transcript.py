#!/usr/bin/env python3
"""把 provider 无关的 raw_transcription.json 标准化为可读的 transcript.md。

兼容本地 WhisperKit 适配结果与通义听悟返回的不同 JSON 层级：
    Transcription
      ├── AudioInfo      (Duration / SampleRate / Language)
      ├── Paragraphs[]   ← 首选：每段含 SpeakerId + Words[](Start/End/Text，单位毫秒)
      └── AudioSegments[] ← 次选：Paragraphs 缺失时回退

用法：
    python scripts/normalize_transcript.py \
        --raw outputs/smoke_test/raw_transcription.json \
        --out outputs/smoke_test/transcript.md
    python scripts/normalize_transcript.py --help

被 ingest_podcast.py 复用（调用 normalize_to_markdown() / write_transcript()）。
解析失败不静默：打印 raw JSON 顶层字段和 Transcription 下字段，并抛出错误。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class NormalizeError(RuntimeError):
    """标准化失败，message 面向使用者。"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _ms_to_timestamp(ms: Any) -> str:
    """毫秒 -> HH:MM:SS.mmm。非法输入降级为 00:00:00.000。"""
    try:
        ms = int(ms)
    except (TypeError, ValueError):
        return "00:00:00.000"
    if ms < 0:
        ms = 0
    hours, rem = divmod(ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"


def _get_transcription(raw: dict) -> dict:
    """定位 Transcription 节点，兼容顶层直接就是 Transcription 内容的情况。"""
    if not isinstance(raw, dict):
        raise NormalizeError(
            f"raw JSON 顶层不是对象，而是 {type(raw).__name__}，无法标准化。"
        )
    if "Transcription" in raw and isinstance(raw["Transcription"], dict):
        return raw["Transcription"]
    # 有些情况下顶层直接是 Transcription 的内容
    if "Paragraphs" in raw or "AudioSegments" in raw:
        return raw
    # 结构不匹配：打印诊断信息（要求：不静默失败）
    _dump_structure(raw)
    raise NormalizeError(
        "raw JSON 中找不到 Transcription / Paragraphs / AudioSegments，结构不匹配。\n"
        "上方已打印顶层字段供排查。normalization failed。"
    )


def _dump_structure(raw: dict) -> None:
    """打印 raw JSON 顶层字段和 Transcription 下字段，便于诊断。"""
    print("=" * 60, file=sys.stderr)
    print("[normalization 诊断] raw JSON 结构：", file=sys.stderr)
    if isinstance(raw, dict):
        print(f"  顶层字段: {list(raw.keys())}", file=sys.stderr)
        tr = raw.get("Transcription")
        if isinstance(tr, dict):
            print(f"  Transcription 下字段: {list(tr.keys())}", file=sys.stderr)
    else:
        print(f"  顶层类型: {type(raw).__name__}", file=sys.stderr)
    print("=" * 60, file=sys.stderr)


def _paragraph_lines(transcription: dict) -> Optional[list[str]]:
    """从 Paragraphs[] 生成行；无有效段落返回 None。"""
    paragraphs = transcription.get("Paragraphs")
    if not isinstance(paragraphs, list) or not paragraphs:
        return None

    lines: list[str] = []
    for para in paragraphs:
        if not isinstance(para, dict):
            continue
        words = para.get("Words")
        if not isinstance(words, list) or not words:
            continue

        # 合并该段所有 Words 的文本
        text = "".join(
            str(w.get("Text", "")) for w in words if isinstance(w, dict)
        ).strip()
        if not text:
            continue

        # 时间戳取段内第一个 Word 的 Start
        first = next((w for w in words if isinstance(w, dict)), {})
        ts = _ms_to_timestamp(first.get("Start", 0))

        speaker_id = para.get("SpeakerId")
        speaker = f"Speaker {speaker_id}: " if speaker_id not in (None, "") else ""

        lines.append(f"[{ts}] {speaker}{text}")

    return lines or None


def _segment_lines(transcription: dict) -> Optional[list[str]]:
    """Paragraphs 缺失时，从 AudioSegments[] 回退生成行。"""
    segments = transcription.get("AudioSegments")
    if not isinstance(segments, list) or not segments:
        return None

    lines: list[str] = []

    def emit(seg: dict) -> None:
        text = str(seg.get("Text", "")).strip()
        if not text:
            return
        ts = _ms_to_timestamp(seg.get("Start", seg.get("BeginTime", 0)))
        speaker_id = seg.get("SpeakerId")
        speaker = f"Speaker {speaker_id}: " if speaker_id not in (None, "") else ""
        lines.append(f"[{ts}] {speaker}{text}")

    for seg in segments:
        if isinstance(seg, dict):
            emit(seg)
        elif isinstance(seg, list):
            # AudioSegments 可能是嵌套数组
            for inner in seg:
                if isinstance(inner, dict):
                    emit(inner)

    return lines or None


def normalize_to_markdown(raw: dict, *, source_meta: Optional[dict] = None) -> str:
    """把 raw_transcription dict 转成 transcript.md 文本。

    source_meta 可选，用于补充 Title / Podcast（来自 episode.json）。
    失败抛 NormalizeError（并已打印诊断）。此函数供 ingest 复用。
    """
    transcription = _get_transcription(raw)
    audio_info = transcription.get("AudioInfo") or {}

    # 优先 Paragraphs，回退 AudioSegments
    lines = _paragraph_lines(transcription)
    if lines is None:
        lines = _segment_lines(transcription)
    if lines is None:
        _dump_structure(raw)
        raise NormalizeError(
            "Paragraphs 与 AudioSegments 都无法解析出可读文本。normalization failed。"
        )

    duration = audio_info.get("Duration")
    duration_str = (
        _ms_to_timestamp(duration) if isinstance(duration, (int, float)) else "unknown"
    )
    language = audio_info.get("Language", "unknown")

    header = ["# Podcast Transcript", ""]
    if source_meta:
        if source_meta.get("episode_url"):
            header.append(f"Source URL: {source_meta['episode_url']}")
        if source_meta.get("title"):
            header.append(f"Title: {source_meta['title']}")
        if source_meta.get("podcast_name"):
            header.append(f"Podcast: {source_meta['podcast_name']}")
    provider = str(raw.get("Provider", "tingwu")).lower()
    provider_label = (
        "WhisperKit (local)" if provider == "whisperkit" else "Alibaba Tingwu"
    )
    header.append(f"Transcribed by: {provider_label}")
    header.append(f"Duration: {duration_str}")
    header.append(f"Language: {language}")
    header.append(f"Generated at: {_now_iso()}")
    header.append("")
    header.append("## Transcript")
    header.append("")

    return "\n".join(header + lines) + "\n"


def write_transcript(
    raw_path, out_path, *, source_meta: Optional[dict] = None
) -> Path:
    """读取 raw JSON -> 写 transcript.md，返回输出路径。供 ingest 复用。"""
    raw_path = Path(raw_path)
    out_path = Path(out_path)

    if not raw_path.exists():
        raise NormalizeError(f"找不到 raw 文件：{raw_path}")

    try:
        raw = json.loads(raw_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise NormalizeError(f"raw 文件不是合法 JSON：{raw_path}\n  {exc}") from exc

    md = normalize_to_markdown(raw, source_meta=source_meta)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    return out_path


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="把通义听悟 raw_transcription.json 标准化为 transcript.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--raw", type=Path, required=True, help="通义听悟 raw_transcription.json 路径"
    )
    parser.add_argument(
        "--out", type=Path, required=True, help="输出 transcript.md 路径"
    )
    parser.add_argument(
        "--episode",
        type=Path,
        default=None,
        help="可选：episode.json 路径，用于补充 Title / Podcast 元数据",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖已存在的 transcript.md（默认不覆盖）",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)

    if args.out.exists() and not args.force:
        print(f"[跳过] {args.out} 已存在。如需覆盖请加 --force。", file=sys.stderr)
        return 1

    source_meta = None
    if args.episode and args.episode.exists():
        try:
            source_meta = json.loads(args.episode.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"[警告] episode.json 解析失败，忽略元数据：{args.episode}", file=sys.stderr)

    try:
        out = write_transcript(args.raw, args.out, source_meta=source_meta)
    except NormalizeError as exc:
        print(f"\n[标准化失败]\n{exc}", file=sys.stderr)
        return 2

    print(f"transcript.md 已生成：{out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
