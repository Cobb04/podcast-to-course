#!/usr/bin/env python3
"""小宇宙（Xiaoyuzhou）公开单集页面解析：提取公网音频直链与元数据。

只解析公开可访问的单集页面，**不下载音频本体**、**不调用通义听悟**、
**不绕过登录/付费/加密内容**。

提取策略（按可靠性排序，逐个尝试）：
    1. og:audio / og:audio:url  (<meta property=...>)
    2. JSON-LD (application/ld+json) 中的 PodcastEpisode.associatedMedia.contentUrl
    3. __NEXT_DATA__ 中的 episode.enclosure.url（小宇宙的 Next.js 数据）
    4. 页面内嵌 JSON 里的 audioUrl / audio_url / mediaUrl / enclosure / contentUrl

用法：
    python scripts/extract_xiaoyuzhou_audio.py "<单集URL>" --out outputs/xxx
    python scripts/extract_xiaoyuzhou_audio.py "<单集URL>" --out outputs/xxx --force
    python scripts/extract_xiaoyuzhou_audio.py --help

被 ingest_podcast.py 复用（调用 extract_episode()）。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
REQUEST_TIMEOUT = 20
# 音频直链候选字段名（页面内嵌 JSON 里可能出现的键）
AUDIO_KEY_CANDIDATES = (
    "audioUrl",
    "audio_url",
    "mediaUrl",
    "contentUrl",
    "enclosure",
)


class ExtractError(RuntimeError):
    """解析失败时抛出，message 面向使用者、包含可行动提示。"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def fetch_html(url: str) -> str:
    """请求页面 HTML，使用浏览器 UA，设置 timeout。"""
    try:
        import requests
    except ImportError as exc:
        raise ExtractError(
            "未安装 requests，无法请求页面。请运行：pip install -r requirements.txt"
        ) from exc

    try:
        resp = requests.get(
            url,
            headers={"User-Agent": BROWSER_UA},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise ExtractError(
            f"请求页面失败：{exc}\n"
            "排查建议：确认链接是否正确、是否为公开单集、网络是否可访问 xiaoyuzhoufm.com。"
        ) from exc

    return resp.text


def _extract_next_data(html: str) -> Optional[dict]:
    """解析 __NEXT_DATA__ 中的 JSON。"""
    m = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S
    )
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        return None


def _find_episode_node(obj: Any) -> Optional[dict]:
    """在 __NEXT_DATA__ 里递归定位 episode 节点（含 enclosure + title/eid）。"""
    if isinstance(obj, dict):
        if "enclosure" in obj and ("title" in obj or "eid" in obj):
            return obj
        for v in obj.values():
            found = _find_episode_node(v)
            if found:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _find_episode_node(v)
            if found:
                return found
    return None


def _deep_find_audio(obj: Any) -> Optional[str]:
    """在任意嵌套 JSON 中深度搜索音频直链字段。"""
    if isinstance(obj, dict):
        for key in AUDIO_KEY_CANDIDATES:
            if key in obj:
                val = obj[key]
                # enclosure 可能是 {"url": "..."} 或直接字符串
                if isinstance(val, dict) and isinstance(val.get("url"), str):
                    if _looks_like_audio(val["url"]):
                        return val["url"]
                elif isinstance(val, str) and _looks_like_audio(val):
                    return val
        for v in obj.values():
            found = _deep_find_audio(v)
            if found:
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _deep_find_audio(v)
            if found:
                return found
    return None


def _looks_like_audio(url: str) -> bool:
    """粗略判断是否音频直链。"""
    if not isinstance(url, str) or not url.startswith("http"):
        return False
    return any(ext in url.lower() for ext in (".m4a", ".mp3", ".aac", ".wav"))


def _meta_content(html: str, prop: str) -> Optional[str]:
    """提取 <meta property="prop" content="...">（property 或 name 均可）。"""
    for attr in ("property", "name"):
        m = re.search(
            rf'<meta[^>]+{attr}=["\']{re.escape(prop)}["\'][^>]*>',
            html,
            re.I,
        )
        if m:
            c = re.search(r'content=["\'](.*?)["\']', m.group(0))
            if c and c.group(1).strip():
                return c.group(1).strip()
    return None


def _extract_from_json_ld(html: str) -> Optional[str]:
    """从 JSON-LD 里找 PodcastEpisode 的音频链接。"""
    for block in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S
    ):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        # associatedMedia.contentUrl 或直接 contentUrl
        found = _deep_find_audio(data)
        if found:
            return found
    return None


def _check_public_access(episode_node: Optional[dict]) -> None:
    """基于页面数据做公开性边界检查：私有 / 付费内容直接拒绝，不尝试绕过。"""
    if not isinstance(episode_node, dict):
        return
    if episode_node.get("isPrivateMedia") is True:
        raise ExtractError(
            "该单集标记为私有内容（isPrivateMedia=true），本工具只处理公开单集，"
            "不会尝试绕过。"
        )
    pay_type = episode_node.get("payType")
    if pay_type and str(pay_type).upper() not in ("FREE", "PAYTYPE_FREE", ""):
        raise ExtractError(
            f"该单集疑似付费内容（payType={pay_type}），本工具只处理公开免费单集，"
            "不会尝试绕过付费。"
        )


def extract_episode(url: str) -> dict:
    """解析单集页面，返回 episode metadata dict。失败抛 ExtractError。

    此函数是可复用入口，供 ingest_podcast.py 直接调用。
    """
    if "xiaoyuzhoufm.com" not in url:
        raise ExtractError(
            f"链接不像小宇宙单集页面：{url}\n"
            "本脚本只支持 xiaoyuzhoufm.com 的公开单集链接。"
        )

    html = fetch_html(url)
    next_data = _extract_next_data(html)
    episode_node = _find_episode_node(next_data) if next_data else None

    # 公开性边界检查（发现私有/付费立即拒绝）
    _check_public_access(episode_node)

    # 逐策略尝试提取 audio_url，记录尝试路径便于失败时报告
    attempts: list[str] = []
    audio_url: Optional[str] = None

    audio_url = _meta_content(html, "og:audio")
    attempts.append(f"og:audio -> {'命中' if audio_url else '未命中'}")

    if not audio_url:
        audio_url = _meta_content(html, "og:audio:url")
        attempts.append(f"og:audio:url -> {'命中' if audio_url else '未命中'}")

    if not audio_url:
        audio_url = _extract_from_json_ld(html)
        attempts.append(f"JSON-LD contentUrl -> {'命中' if audio_url else '未命中'}")

    if not audio_url and episode_node:
        enc = episode_node.get("enclosure")
        if isinstance(enc, dict) and _looks_like_audio(enc.get("url", "")):
            audio_url = enc["url"]
        attempts.append(
            f"__NEXT_DATA__ episode.enclosure.url -> {'命中' if audio_url else '未命中'}"
        )

    if not audio_url and next_data:
        audio_url = _deep_find_audio(next_data)
        attempts.append(
            f"内嵌 JSON 深度搜索({'/'.join(AUDIO_KEY_CANDIDATES)}) "
            f"-> {'命中' if audio_url else '未命中'}"
        )

    if not audio_url:
        raise ExtractError(
            "未能从该小宇宙页面提取公开音频 URL，可能是页面结构变化、"
            "非公开内容或需要登录。\n"
            "已尝试的解析路径：\n  - " + "\n  - ".join(attempts)
        )

    # 补全元数据（尽力而为，缺失字段留空字符串而非伪造）
    node = episode_node or {}
    podcast = node.get("podcast") or {}
    podcast_name = podcast.get("title") if isinstance(podcast, dict) else ""

    title = (
        node.get("title")
        or _meta_content(html, "og:title")
        or ""
    )

    return {
        "source": "xiaoyuzhou",
        "episode_url": url,
        "title": title,
        "podcast_name": podcast_name or "",
        "published_at": node.get("pubDate", "") or "",
        "duration": node.get("duration", "") or "",
        "audio_url": audio_url,
        "extracted_at": _now_iso(),
        "_extraction_attempts": attempts,
    }


def _slug_from_url(url: str) -> str:
    """从单集 URL 末段生成 slug（作为默认输出目录名）。"""
    tail = url.rstrip("/").split("/")[-1]
    return re.sub(r"[^0-9A-Za-z_-]", "", tail) or "episode"


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="解析小宇宙公开单集，提取音频直链与元数据到 episode.json（不下载音频，不调用通义听悟）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("url", help="小宇宙公开单集 URL")
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="输出目录（默认 outputs/<slug>）。episode.json 写入此目录。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="覆盖已存在的 episode.json（默认不覆盖）",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)

    skill_root = Path(__file__).resolve().parent.parent
    out_dir = args.out or (skill_root / "outputs" / _slug_from_url(args.url))
    out_dir = Path(out_dir)
    dest = out_dir / "episode.json"

    if dest.exists() and not args.force:
        print(
            f"[跳过] {dest} 已存在。如需覆盖请加 --force。",
            file=sys.stderr,
        )
        return 1

    print(f"解析单集：{args.url}")
    try:
        episode = extract_episode(args.url)
    except ExtractError as exc:
        print(f"\n[解析失败]\n{exc}", file=sys.stderr)
        return 2

    out_dir.mkdir(parents=True, exist_ok=True)
    dest.write_text(
        json.dumps(episode, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print("-" * 60)
    print(f"标题      : {episode['title']}")
    print(f"播客      : {episode['podcast_name']}")
    print(f"发布时间  : {episode['published_at']}")
    print(f"时长(秒)  : {episode['duration']}")
    print(f"音频直链  : {episode['audio_url']}")
    print("-" * 60)
    print(f"已写入：{dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
