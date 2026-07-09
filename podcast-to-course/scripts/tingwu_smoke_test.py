#!/usr/bin/env python3
"""通义听悟离线转写 API 冒烟测试。

验证整条链路是否打通：读取环境变量 → CreateTask → 轮询 GetTaskInfo →
下载 Result.Transcription → 保存到 outputs/smoke_test/raw_transcription.json。

用法：
    python scripts/tingwu_smoke_test.py
    python scripts/tingwu_smoke_test.py --audio-url "https://.../your.wav"
    python scripts/tingwu_smoke_test.py --help

不需要任何人工复制网页结果。任何一步失败都会打印明确原因。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 允许以 `python scripts/tingwu_smoke_test.py` 直接运行时导入同目录模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

from tingwu_client import (  # noqa: E402
    DEFAULT_TEST_AUDIO_URL,
    POLL_INTERVAL_SECONDS,
    POLL_MAX_MINUTES,
    TingwuCredentials,
    TingwuError,
    TranscriptionTask,
    create_offline_task,
    download_transcription,
    poll_until_done,
)

# 相对 skill 根目录（scripts/ 的上一级）定位输出
SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = SKILL_ROOT / "outputs" / "smoke_test" / "raw_transcription.json"


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="通义听悟离线转写 API 冒烟测试（CreateTask → 轮询 → 下载结果）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--audio-url",
        default=DEFAULT_TEST_AUDIO_URL,
        help=f"用于测试的公网音频 URL（默认使用官方示例音频）。\n默认：{DEFAULT_TEST_AUDIO_URL}",
    )
    parser.add_argument(
        "--source-language",
        default="cn",
        help="转写语言模型：cn/en/fspk/ja/yue（默认 cn）",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"结果保存路径（默认 {DEFAULT_OUTPUT}）",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=POLL_INTERVAL_SECONDS,
        help=f"轮询间隔秒数（默认 {POLL_INTERVAL_SECONDS}）",
    )
    parser.add_argument(
        "--max-minutes",
        type=int,
        default=POLL_MAX_MINUTES,
        help=f"最长等待分钟数（默认 {POLL_MAX_MINUTES}）",
    )
    return parser.parse_args(argv)


def _print_poll(task: TranscriptionTask, elapsed: int) -> None:
    mins, secs = divmod(elapsed, 60)
    print(f"  [{mins:02d}:{secs:02d}] TaskStatus = {task.status}")


def main(argv=None) -> int:
    args = _parse_args(argv)

    print("=" * 60)
    print("通义听悟离线转写 · 冒烟测试")
    print("=" * 60)

    # 1) 读取凭据（缺失时给出明确提示）
    try:
        creds = TingwuCredentials.from_env()
    except TingwuError as exc:
        print(f"\n[环境变量错误]\n{exc}", file=sys.stderr)
        return 2

    print(f"区域        : {creds.region}")
    print(f"测试音频 URL: {args.audio_url}")
    print(f"结果输出    : {args.out}")
    print("-" * 60)

    # 2) CreateTask
    print("\n[1/3] 创建转写任务 CreateTask ...")
    try:
        task = create_offline_task(
            creds,
            args.audio_url,
            source_language=args.source_language,
            task_key="smoke_test",
        )
    except TingwuError as exc:
        print(f"\n[CreateTask 失败]\n{exc}", file=sys.stderr)
        return 3
    print(f"      TaskId = {task.task_id}")
    print(f"      初始状态 = {task.status}")

    # 3) 轮询 GetTaskInfo
    print(f"\n[2/3] 轮询任务状态（每 {args.interval}s，最长 {args.max_minutes}min）...")
    try:
        task = poll_until_done(
            creds,
            task.task_id,
            interval_seconds=args.interval,
            max_minutes=args.max_minutes,
            on_poll=_print_poll,
        )
    except TingwuError as exc:
        print(f"\n[GetTaskInfo / 轮询失败]\n{exc}", file=sys.stderr)
        return 4
    print("      任务已完成 (COMPLETED)")
    print(f"      转写结果链接 = {task.transcription_url[:80]}...")

    # 4) 下载结果
    print("\n[3/3] 下载转写结果 Result.Transcription ...")
    try:
        download_transcription(task.transcription_url, args.out)
    except TingwuError as exc:
        print(f"\n[下载失败]\n{exc}", file=sys.stderr)
        return 5

    print("-" * 60)
    print("冒烟测试成功 ✅")
    print(f"原始转写已保存到：{args.out}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
