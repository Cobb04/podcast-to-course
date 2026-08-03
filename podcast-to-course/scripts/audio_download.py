"""Download public podcast audio to a resumable local cache."""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import unquote, urlparse


class AudioDownloadError(RuntimeError):
    """A public audio URL could not be downloaded safely."""


_CONTENT_TYPE_SUFFIXES = {
    "audio/aac": ".aac",
    "audio/flac": ".flac",
    "audio/m4a": ".m4a",
    "audio/mp4": ".m4a",
    "audio/mpeg": ".mp3",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
    "audio/x-m4a": ".m4a",
    "audio/x-wav": ".wav",
}
_SUPPORTED_SUFFIXES = {
    ".aac",
    ".aiff",
    ".flac",
    ".m4a",
    ".mp3",
    ".ogg",
    ".wav",
}
_USER_AGENT = "podcast-to-course/1.0 (+https://github.com/Cobb04/podcast-to-course)"


def infer_audio_suffix(url: str, content_type: str = "") -> str:
    """Infer a WhisperKit-compatible extension from URL or Content-Type."""
    suffix = Path(unquote(urlparse(url).path)).suffix.lower()
    if suffix in _SUPPORTED_SUFFIXES:
        return suffix
    media_type = content_type.partition(";")[0].strip().lower()
    return _CONTENT_TYPE_SUFFIXES.get(media_type, ".m4a")


def download_public_audio(
    url: str,
    out_dir: Path,
    *,
    timeout_seconds: int = 60,
    chunk_size: int = 1024 * 1024,
    content_type_hint: str = "",
) -> Path:
    """Download a public HTTP(S) audio URL, resuming a partial file when possible.

    The completed file is cached as ``source_audio.<ext>``. A failed transfer leaves
    ``.part`` in place so the next invocation can send an HTTP Range request.
    """
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise AudioDownloadError("音频地址必须是公开可访问的 HTTP(S) URL。")

    try:
        import requests
    except ImportError as exc:
        raise AudioDownloadError(
            "未安装 requests。请运行：pip install -r requirements.txt"
        ) from exc

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = infer_audio_suffix(url, content_type_hint)
    destination = out_dir / f"source_audio{suffix}"
    partial = destination.with_suffix(destination.suffix + ".part")
    manifest = destination.with_name(destination.name + ".download.json")

    if destination.exists() and destination.stat().st_size > 0:
        try:
            cached = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cached = {}
        if (
            cached.get("source_url") == url
            and cached.get("bytes") == destination.stat().st_size
        ):
            return destination
        if partial.exists():
            partial.unlink()

    resume_at = partial.stat().st_size if partial.exists() else 0
    headers = {"User-Agent": _USER_AGENT}
    if resume_at:
        headers["Range"] = f"bytes={resume_at}-"

    try:
        response = requests.get(
            url,
            headers=headers,
            stream=True,
            timeout=(15, timeout_seconds),
            allow_redirects=True,
        )
        with response:
            if response.status_code not in (200, 206):
                raise AudioDownloadError(
                    f"下载音频失败：HTTP {response.status_code} ({response.url})"
                )

            # A server may ignore Range and return the full object with 200.
            append = resume_at > 0 and response.status_code == 206
            mode = "ab" if append else "wb"
            with partial.open(mode) as handle:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        handle.write(chunk)
            content_length = response.headers.get("Content-Length")
            expected_bytes = None
            if content_length and content_length.isdigit():
                expected_bytes = int(content_length) + (resume_at if append else 0)
            final_url = response.url
            response_content_type = response.headers.get("Content-Type", "")
            etag = response.headers.get("ETag", "")
            last_modified = response.headers.get("Last-Modified", "")
    except AudioDownloadError:
        raise
    except requests.RequestException as exc:
        raise AudioDownloadError(f"下载音频失败：{exc}") from exc
    except OSError as exc:
        raise AudioDownloadError(f"写入本地音频失败：{exc}") from exc

    if not partial.exists() or partial.stat().st_size == 0:
        raise AudioDownloadError("下载完成但音频文件为空。")
    actual_bytes = partial.stat().st_size
    if expected_bytes is not None and actual_bytes != expected_bytes:
        raise AudioDownloadError(
            f"音频下载不完整：期望 {expected_bytes} bytes，实际 {actual_bytes} bytes。"
        )
    os.replace(partial, destination)
    manifest.write_text(
        json.dumps(
            {
                "source_url": url,
                "final_url": final_url,
                "bytes": destination.stat().st_size,
                "content_type": response_content_type,
                "etag": etag,
                "last_modified": last_modified,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    return destination
