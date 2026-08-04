#!/usr/bin/env python3
"""统一 ingest CLI：把三种输入统一转成 transcript.md，交给课程生成逻辑。

三种互斥输入：
    --url        小宇宙公开单集链接 → 解析 audio_url → 本地/云端转写 → 标准化
    --audio-url  公网音频 URL       → 本地/云端转写 → 标准化
    --transcript 已有本地转写稿      → 直接标准化/复制（不调用 ASR）

统一输出目录结构：
    outputs/demo/
      ├── episode.json           (url / audio-url 模式)
      ├── raw_transcription.json (调用通义听悟时)
      ├── transcript.md          (总是产出，除非在此之前失败)
      └── ingest_report.md       (总是产出，记录全过程与错误)

ingest 层只负责产出 transcript.md，不与课程生成逻辑耦合。
默认 provider=auto：优先使用免费的本地 WhisperKit，未安装时回退到已配置的听悟。

用法：
    python scripts/ingest_podcast.py --url "<小宇宙链接>" --out outputs/demo
    python scripts/ingest_podcast.py --audio-url "<音频URL>" --provider whisperkit --out outputs/demo
    python scripts/ingest_podcast.py --transcript path/to/transcript.md --out outputs/demo
    python scripts/ingest_podcast.py --help
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# 允许从仓库根目录或任意位置运行时导入同目录模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tingwu_client import (  # noqa: E402
    TingwuCredentials,
    TingwuError,
    TranscriptionTask,
    create_offline_task,
    download_transcription,
    poll_until_done,
)
from extract_xiaoyuzhou_audio import ExtractError, extract_episode  # noqa: E402
from normalize_transcript import NormalizeError, write_transcript  # noqa: E402
from audio_download import AudioDownloadError, download_public_audio  # noqa: E402
from whisperkit_client import (  # noqa: E402
    DEFAULT_MODEL,
    WhisperKitError,
    find_whisperkit_cli,
    transcribe_with_whisperkit,
)

SUPPORTED_PROVIDERS = ("auto", "whisperkit", "tingwu")


class ProviderError(RuntimeError):
    """No usable transcription provider is available."""


def select_provider(
    requested: str,
    *,
    whisperkit_available: bool,
    tingwu_available: bool,
) -> str:
    """Resolve a provider without performing network or transcription work."""
    if requested not in SUPPORTED_PROVIDERS:
        raise ProviderError(
            f"不支持的 provider: {requested}。可选：{', '.join(SUPPORTED_PROVIDERS)}"
        )
    if requested == "whisperkit":
        if not whisperkit_available:
            raise ProviderError(
                "找不到 WhisperKit CLI。Apple Silicon Mac 可运行："
                "brew install whisperkit-cli"
            )
        return "whisperkit"
    if requested == "tingwu":
        if not tingwu_available:
            raise ProviderError(
                "听悟凭据未配置完整：需要 ALIBABA_CLOUD_ACCESS_KEY_ID、"
                "ALIBABA_CLOUD_ACCESS_KEY_SECRET、TINGWU_APP_KEY。"
            )
        return "tingwu"
    if whisperkit_available:
        return "whisperkit"
    if tingwu_available:
        return "tingwu"
    raise ProviderError(
        "没有可用的转写 provider。免费本地方案：brew install whisperkit-cli；"
        "或配置听悟的三个环境变量。"
    )


def _tingwu_credentials_available() -> bool:
    try:
        TingwuCredentials.from_env()
    except TingwuError:
        return False
    return True


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


class Report:
    """累积式 ingest 报告，无论成功失败都会写出 ingest_report.md。"""

    def __init__(self, mode: str, input_value: str, provider: str, out_dir: Path):
        self.mode = mode
        self.input_value = input_value
        self.provider = provider
        self.selected_provider = ""
        self.out_dir = out_dir
        self.started_at = _now_iso()
        self.finished_at = ""
        self.status = "FAILED"  # 默认失败，成功时显式置 SUCCESS

        # Episode 段
        self.source = ""
        self.title = ""
        self.podcast = ""
        self.duration = ""
        self.audio_url_extracted = "no"
        self.audio_content_type = "not checked"

        # Transcription 段
        self.tingwu_called = "no"
        self.whisperkit_called = "no"
        self.whisperkit_cli = ""
        self.model = ""
        self.prompt = ""
        self.concurrent_worker_count = ""
        self.diarization = ""
        self.diarization_model_path = ""
        self.local_audio_path = ""
        self.native_json_path = ""
        self.srt_path = ""
        self.log_path = ""
        self.rttm_path = ""
        self.metrics_path = ""
        self.task_id = ""
        self.final_status = ""
        self.raw_path = ""
        self.transcript_path = ""

        # 错误
        self.errors: list[str] = []

    def add_error(self, stage: str, message: str, suggestion: str = "") -> None:
        block = f"**[{stage}]** {message}"
        if suggestion:
            block += f"\n  - 建议：{suggestion}"
        self.errors.append(block)

    def render(self) -> str:
        errors = "None" if not self.errors else "\n\n".join(
            f"- {e}" for e in self.errors
        )
        return f"""# Ingest Report

- Input mode: {self.mode}
- Input value: {self.input_value}
- Requested provider: {self.provider}
- Selected provider: {self.selected_provider}
- Output directory: {self.out_dir}
- Started at: {self.started_at}
- Finished at: {self.finished_at}
- Status: {self.status}

## Episode

- Source: {self.source}
- Title: {self.title}
- Podcast: {self.podcast}
- Duration: {self.duration}
- Audio URL extracted: {self.audio_url_extracted}
- Audio URL content type if checked: {self.audio_content_type}

## Transcription

- Tingwu called: {self.tingwu_called}
- WhisperKit called: {self.whisperkit_called}
- WhisperKit CLI: {self.whisperkit_cli}
- Model: {self.model}
- ASR prompt: {self.prompt}
- Concurrent worker count: {self.concurrent_worker_count}
- Diarization: {self.diarization}
- Diarization model path: {self.diarization_model_path}
- Cached audio: {self.local_audio_path}
- Native WhisperKit JSON: {self.native_json_path}
- SRT: {self.srt_path}
- WhisperKit log: {self.log_path}
- Speaker RTTM: {self.rttm_path}
- Transcription metrics: {self.metrics_path}
- TaskId: {self.task_id}
- Final TaskStatus: {self.final_status}
- raw_transcription.json: {self.raw_path}
- transcript.md: {self.transcript_path}

## Errors

{errors}
"""

    def write(self) -> Path:
        self.finished_at = _now_iso()
        self.out_dir.mkdir(parents=True, exist_ok=True)
        dest = self.out_dir / "ingest_report.md"
        dest.write_text(self.render(), encoding="utf-8")
        return dest


def _check_content_type(url: str) -> str:
    """HEAD 请求确认音频链接可访问，返回 Content-Type（失败返回描述字符串）。"""
    try:
        import requests

        resp = requests.head(url, timeout=15, allow_redirects=True)
        if resp.status_code >= 400:
            return f"HTTP {resp.status_code}"
        return resp.headers.get("Content-Type", "unknown")
    except Exception as exc:  # noqa: BLE001
        return f"check failed: {exc}"


def _run_tingwu(
    audio_url: str,
    out_dir: Path,
    report: Report,
    *,
    source_meta: Optional[dict],
    poll_interval: int,
    poll_max_minutes: int,
) -> Optional[Path]:
    """提交通义听悟转写 → 下载 raw → 标准化。返回 transcript.md 路径或 None。

    每一步的失败都记入 report，不抛出（由调用方根据返回值判断）。
    """
    # 凭据
    try:
        creds = TingwuCredentials.from_env()
    except TingwuError as exc:
        report.add_error(
            "凭据",
            str(exc),
            "配置 ALIBABA_CLOUD_ACCESS_KEY_ID / _SECRET / TINGWU_APP_KEY 后重试。",
        )
        return None

    report.tingwu_called = "yes"

    # CreateTask
    try:
        task: TranscriptionTask = create_offline_task(
            creds, audio_url, task_key="ingest"
        )
    except TingwuError as exc:
        report.add_error(
            "通义听悟 CreateTask",
            str(exc),
            "检查 AccessKey / AppKey / 项目状态，以及音频 URL 是否公网可访问。",
        )
        return None

    report.task_id = task.task_id
    report.final_status = task.status

    # 轮询
    try:
        task = poll_until_done(
            creds,
            task.task_id,
            interval_seconds=poll_interval,
            max_minutes=poll_max_minutes,
        )
    except TingwuError as exc:
        report.final_status = task.status
        report.add_error(
            "通义听悟 轮询/GetTaskInfo",
            str(exc),
            "确认音频时长与可访问性；可稍后凭 TaskId 重新查询。",
        )
        return None

    report.final_status = task.status

    # 下载 raw
    raw_path = out_dir / "raw_transcription.json"
    try:
        download_transcription(task.transcription_url, raw_path)
    except TingwuError as exc:
        report.add_error(
            "通义听悟 结果下载",
            str(exc),
            "预签名 URL 可能过期，可重新调用 GetTaskInfo 获取新链接。",
        )
        return None

    report.raw_path = str(raw_path)

    # 标准化（失败时保留 raw，不生成空 transcript）
    transcript_path = out_dir / "transcript.md"
    try:
        write_transcript(raw_path, transcript_path, source_meta=source_meta)
    except NormalizeError as exc:
        report.add_error(
            "标准化 normalization",
            str(exc),
            "raw_transcription.json 已保留，请检查其结构；诊断信息见上方终端输出。",
        )
        return None

    report.transcript_path = str(transcript_path)
    return transcript_path


def build_asr_prompt(
    source_meta: Optional[dict], explicit_prompt: Optional[str]
) -> Optional[str]:
    """Build a short ASR vocabulary hint; metadata never becomes transcript text."""
    if explicit_prompt and explicit_prompt.strip():
        return explicit_prompt.strip()[:500]
    if not source_meta:
        return None
    values = [
        str(source_meta.get(key, "")).strip()
        for key in ("title", "podcast_name")
    ]
    prompt = "，".join(value for value in values if value)
    return prompt[:500] or None


def _run_whisperkit(
    audio_url: str,
    out_dir: Path,
    report: Report,
    *,
    source_meta: Optional[dict],
    executable: str,
    model: str,
    model_path: Optional[Path],
    language: str,
    diarization: bool,
    speaker_count: int,
    diarization_model_path: Optional[Path],
    download_timeout: int,
    prompt: Optional[str],
    concurrent_worker_count: int,
) -> Optional[Path]:
    """Download public audio, transcribe locally, and normalize the result."""
    report.whisperkit_called = "yes"
    report.whisperkit_cli = executable
    report.model = str(model_path) if model_path else model
    resolved_prompt = build_asr_prompt(source_meta, prompt)
    report.prompt = resolved_prompt or ""
    report.concurrent_worker_count = str(concurrent_worker_count)
    report.diarization = "enabled" if diarization else "disabled"
    report.diarization_model_path = str(diarization_model_path or "")
    report.log_path = str(out_dir / "whisperkit.log")

    try:
        audio_path = download_public_audio(
            audio_url,
            out_dir,
            timeout_seconds=download_timeout,
            content_type_hint=report.audio_content_type,
        )
    except AudioDownloadError as exc:
        report.add_error(
            "音频下载",
            str(exc),
            "确认链接是公开的音频直链；失败的 .part 文件会保留供下次断点续传。",
        )
        return None

    report.local_audio_path = str(audio_path)
    print(f"[ingest] 音频缓存完成：{audio_path}")
    print("[ingest] 开始本地转写；首次运行会下载模型，长音频需要较长时间。")
    try:
        artifacts = transcribe_with_whisperkit(
            audio_path,
            out_dir,
            executable=executable,
            model=model,
            model_path=model_path,
            language=language or None,
            diarization=diarization,
            speaker_count=speaker_count,
            diarization_model_path=diarization_model_path,
            prompt=resolved_prompt,
            concurrent_worker_count=concurrent_worker_count,
        )
    except WhisperKitError as exc:
        report.add_error(
            "WhisperKit 本地转写",
            str(exc),
            "查看 whisperkit.log；首次运行还会下载模型，请确认磁盘与网络可用。",
        )
        return None

    raw_path = artifacts["raw"]
    report.raw_path = str(raw_path)
    report.native_json_path = str(artifacts["native_json"])
    report.srt_path = str(artifacts.get("srt", ""))
    report.log_path = str(artifacts["log"])
    report.rttm_path = str(artifacts.get("rttm", ""))
    report.metrics_path = str(artifacts.get("metrics", ""))

    transcript_path = out_dir / "transcript.md"
    try:
        write_transcript(raw_path, transcript_path, source_meta=source_meta)
    except NormalizeError as exc:
        report.add_error(
            "标准化 normalization",
            str(exc),
            "WhisperKit 原生 JSON 与 raw_transcription.json 已保留，请检查结构。",
        )
        return None
    report.transcript_path = str(transcript_path)
    return transcript_path


def _run_provider(
    audio_url: str,
    out_dir: Path,
    report: Report,
    args,
    *,
    source_meta: Optional[dict],
) -> Optional[Path]:
    if args.resolved_provider == "whisperkit":
        return _run_whisperkit(
            audio_url,
            out_dir,
            report,
            source_meta=source_meta,
            executable=args.resolved_whisperkit_cli,
            model=args.model,
            model_path=args.model_path,
            language=args.language,
            diarization=not args.no_diarization,
            speaker_count=args.speaker_count,
            diarization_model_path=args.diarization_model_path,
            download_timeout=args.download_timeout,
            prompt=args.prompt,
            concurrent_worker_count=args.concurrent_worker_count,
        )
    return _run_tingwu(
        audio_url,
        out_dir,
        report,
        source_meta=source_meta,
        poll_interval=args.interval,
        poll_max_minutes=args.max_minutes,
    )


def _mode_url(args, out_dir: Path, report: Report) -> bool:
    """小宇宙链接模式。返回是否成功。"""
    # 解析单集
    try:
        episode = extract_episode(args.url)
    except ExtractError as exc:
        report.add_error(
            "小宇宙解析 audio_url extraction failed",
            str(exc),
            "换一个公开单集链接 / 改用 --audio-url 提供公网音频 / 改用 --transcript 提供转写稿。",
        )
        return False

    # 写 episode.json
    episode_path = out_dir / "episode.json"
    episode_path.write_text(
        json.dumps(episode, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report.source = episode.get("source", "xiaoyuzhou")
    report.title = episode.get("title", "")
    report.podcast = episode.get("podcast_name", "")
    report.duration = str(episode.get("duration", ""))
    report.audio_url_extracted = "yes"

    audio_url = episode["audio_url"]
    report.audio_content_type = _check_content_type(audio_url)

    transcript = _run_provider(
        audio_url,
        out_dir,
        report,
        args,
        source_meta=episode,
    )
    return transcript is not None


def _mode_audio_url(args, out_dir: Path, report: Report) -> bool:
    """公网音频 URL 模式。返回是否成功。"""
    # 最小 episode.json
    episode = {
        "source": "audio_url",
        "episode_url": "",
        "title": "",
        "podcast_name": "",
        "published_at": "",
        "duration": "",
        "audio_url": args.audio_url,
        "extracted_at": _now_iso(),
    }
    (out_dir / "episode.json").write_text(
        json.dumps(episode, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    report.source = "audio_url"
    report.audio_url_extracted = "yes"
    report.audio_content_type = _check_content_type(args.audio_url)

    transcript = _run_provider(
        args.audio_url,
        out_dir,
        report,
        args,
        source_meta=None,
    )
    return transcript is not None


def _mode_transcript(args, out_dir: Path, report: Report) -> bool:
    """已有转写稿模式：不调用通义听悟，只复制/标准化到 transcript.md。"""
    src = Path(args.transcript)
    if not src.exists():
        report.add_error(
            "转写稿输入",
            f"找不到文件：{src}",
            "确认路径是否正确。",
        )
        return False

    report.source = "transcript"
    report.tingwu_called = "no"

    dest = out_dir / "transcript.md"
    try:
        if src.suffix.lower() == ".json":
            # 若用户误传了通义听悟 raw JSON，也能标准化
            write_transcript(src, dest)
        else:
            shutil.copyfile(src, dest)
    except (NormalizeError, OSError) as exc:
        report.add_error("转写稿处理", str(exc), "确认文件内容是否为有效转写稿。")
        return False

    report.transcript_path = str(dest)
    return True


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="统一 ingest CLI：小宇宙链接 / 公网音频 URL / 已有转写稿 → transcript.md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="三种输入互斥，只能选其一。",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="小宇宙公开单集链接")
    group.add_argument("--audio-url", dest="audio_url", help="公网可访问音频 URL")
    group.add_argument("--transcript", help="已有本地转写稿路径（.md/.txt/.json）")

    parser.add_argument(
        "--provider",
        choices=SUPPORTED_PROVIDERS,
        default="auto",
        help="转写 provider：auto 优先免费本地 WhisperKit，再回退听悟（默认 auto）",
    )
    parser.add_argument(
        "--out",
        type=Path,
        required=True,
        help="输出目录（如 outputs/demo）",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖输出目录中已存在的关键文件（默认不覆盖）",
    )
    parser.add_argument("--interval", type=int, default=30, help="通义听悟轮询间隔秒（默认30）")
    parser.add_argument(
        "--max-minutes", type=int, default=30, help="通义听悟最长等待分钟（默认30）"
    )
    parser.add_argument(
        "--whisperkit-cli",
        default=None,
        help="WhisperKit/Argmax CLI 路径（默认从 PATH 或 WHISPERKIT_CLI 查找）",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"WhisperKit 模型（默认 {DEFAULT_MODEL}）",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=None,
        help="已下载的 WhisperKit 模型目录；设置后不再在线下载 --model",
    )
    parser.add_argument(
        "--language",
        default="zh",
        help="WhisperKit 语言代码；传空字符串可自动检测（默认 zh）",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="WhisperKit 专有名词/术语提示；小宇宙模式默认使用标题与节目名",
    )
    parser.add_argument(
        "--concurrent-worker-count",
        type=int,
        default=4,
        help="WhisperKit VAD 分块并发数；0 表示不限制（默认 4）",
    )
    parser.add_argument(
        "--no-diarization",
        action="store_true",
        help="关闭本地说话人分离（更省内存，但 transcript 不标注说话人）",
    )
    parser.add_argument(
        "--speaker-count",
        type=int,
        default=0,
        help="已知说话人数；0 表示自动判断（默认 0）",
    )
    parser.add_argument(
        "--diarization-model-path",
        type=Path,
        default=None,
        help="已下载的 SpeakerKit 模型目录；设置后不再在线下载说话人模型",
    )
    parser.add_argument(
        "--download-timeout",
        type=int,
        default=60,
        help="音频下载单次读取超时秒数（默认 60）",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)
    out_dir = Path(args.out)

    # 判定模式
    if args.url:
        mode, input_value = "xiaoyuzhou_url", args.url
    elif args.audio_url:
        mode, input_value = "audio_url", args.audio_url
    else:
        mode, input_value = "transcript", args.transcript

    # 覆盖保护
    transcript_target = out_dir / "transcript.md"
    if transcript_target.exists() and not args.force:
        print(
            f"[跳过] {transcript_target} 已存在。如需覆盖请加 --force。",
            file=sys.stderr,
        )
        return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    report = Report(mode, input_value, args.provider, out_dir)

    # transcript 模式不需要 ASR；其他模式在开始下载前解析实际 provider。
    if mode in ("xiaoyuzhou_url", "audio_url"):
        args.resolved_whisperkit_cli = find_whisperkit_cli(args.whisperkit_cli)
        try:
            args.resolved_provider = select_provider(
                args.provider,
                whisperkit_available=bool(args.resolved_whisperkit_cli),
                tingwu_available=_tingwu_credentials_available(),
            )
        except ProviderError as exc:
            report.add_error("Provider 选择", str(exc))
            report.write()
            print(f"[错误] {exc}", file=sys.stderr)
            return 2
        report.selected_provider = args.resolved_provider
    else:
        args.resolved_provider = "none"
        args.resolved_whisperkit_cli = ""
        report.selected_provider = "none (transcript input)"

    print(
        f"[ingest] 模式={mode} provider={args.resolved_provider} 输出={out_dir}"
    )

    try:
        if mode == "xiaoyuzhou_url":
            ok = _mode_url(args, out_dir, report)
        elif mode == "audio_url":
            ok = _mode_audio_url(args, out_dir, report)
        else:
            ok = _mode_transcript(args, out_dir, report)
        report.status = "SUCCESS" if ok else "FAILED"
    except Exception as exc:  # noqa: BLE001 — 兜底，任何异常都写进 report
        report.add_error("未预期异常", repr(exc), "请把 ingest_report.md 反馈给维护者。")
        report.status = "FAILED"
        ok = False

    report_path = report.write()

    print("-" * 60)
    print(f"状态: {report.status}")
    print(f"报告: {report_path}")
    if report.transcript_path:
        print(f"transcript.md: {report.transcript_path}")
    if report.status != "SUCCESS":
        print("（详情与建议见 ingest_report.md 的 Errors 段）", file=sys.stderr)

    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
