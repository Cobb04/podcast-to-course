"""通义听悟（Alibaba Tingwu）新版离线转写 API 封装。

只做一件事：把公网音频 URL 提交给通义听悟离线转写，轮询到完成，
返回转写结果 JSON 的下载链接。**不使用**听悟的摘要 / 章节 / 问答等大模型能力。

API 事实（版本 2023-09-30，ROA 风格，华北2-北京）：
  - CreateTask :  PUT  /openapi/tingwu/v2/tasks?type=offline
  - GetTaskInfo:  GET  /openapi/tingwu/v2/tasks/{TaskId}

签名交给官方 SDK（aliyun-python-sdk-core 的 CommonRequest）处理，
避免手写 ROA 签名出错。

被 tingwu_smoke_test.py 和 ingest_podcast.py 共用。
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

DEFAULT_REGION = "cn-beijing"
API_VERSION = "2023-09-30"
CREATE_TASK_URI = "/openapi/tingwu/v2/tasks"
GET_TASK_URI = "/openapi/tingwu/v2/tasks/"  # 后接 {TaskId}

# 官方公开测试音频（16k 采样中文示例），用于冒烟测试
DEFAULT_TEST_AUDIO_URL = (
    "https://isv-data.oss-cn-hangzhou.aliyuncs.com/"
    "ics/MaaS/ASR/test_audio/asr_example.wav"
)

# 轮询参数
POLL_INTERVAL_SECONDS = 30
POLL_MAX_MINUTES = 30


class TingwuError(RuntimeError):
    """通义听悟调用相关的可读错误，message 面向使用者、包含可行动提示。"""


@dataclass
class TingwuCredentials:
    """从环境变量读取的凭据。绝不硬编码，绝不落盘。"""

    access_key_id: str
    access_key_secret: str
    app_key: str
    region: str = DEFAULT_REGION

    ENV_KEY_ID = "ALIBABA_CLOUD_ACCESS_KEY_ID"
    ENV_KEY_SECRET = "ALIBABA_CLOUD_ACCESS_KEY_SECRET"
    ENV_APP_KEY = "TINGWU_APP_KEY"
    ENV_REGION = "TINGWU_REGION"

    @classmethod
    def from_env(cls) -> "TingwuCredentials":
        """从环境变量装载凭据，缺失时抛出明确说明缺哪个变量的错误。"""
        missing = []
        key_id = os.environ.get(cls.ENV_KEY_ID, "").strip()
        key_secret = os.environ.get(cls.ENV_KEY_SECRET, "").strip()
        app_key = os.environ.get(cls.ENV_APP_KEY, "").strip()

        if not key_id:
            missing.append(cls.ENV_KEY_ID)
        if not key_secret:
            missing.append(cls.ENV_KEY_SECRET)
        if not app_key:
            missing.append(cls.ENV_APP_KEY)

        if missing:
            raise TingwuError(
                "缺少必需的环境变量：" + ", ".join(missing) + "\n"
                "请先配置阿里云凭据，例如：\n"
                f'  export {cls.ENV_KEY_ID}="..."\n'
                f'  export {cls.ENV_KEY_SECRET}="..."\n'
                f'  export {cls.ENV_APP_KEY}="..."\n'
                "（可复制 .env.example 为 .env 后 source，详见 README。）"
            )

        region = os.environ.get(cls.ENV_REGION, "").strip() or DEFAULT_REGION
        return cls(
            access_key_id=key_id,
            access_key_secret=key_secret,
            app_key=app_key,
            region=region,
        )


@dataclass
class TranscriptionTask:
    """一次离线转写任务的运行时状态。"""

    task_id: str
    status: str = "UNKNOWN"
    transcription_url: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    last_response: dict = field(default_factory=dict)


def _build_client(creds: TingwuCredentials):
    """构造 aliyun-python-sdk-core 的 AcsClient，导入失败给出安装提示。"""
    try:
        from aliyunsdkcore.client import AcsClient
    except ImportError as exc:  # noqa: PERF203
        raise TingwuError(
            "未安装 aliyun-python-sdk-core，无法调用通义听悟 API。\n"
            "请运行：pip install -r requirements.txt\n"
            "（或：pip install aliyun-python-sdk-core）"
        ) from exc

    return AcsClient(
        creds.access_key_id,
        creds.access_key_secret,
        creds.region,
    )


def _build_common_request(creds: TingwuCredentials, uri: str, method: str):
    """构造一个指向听悟 ROA 接口的 CommonRequest。"""
    from aliyunsdkcore.request import CommonRequest

    req = CommonRequest()
    req.set_domain(f"tingwu.{creds.region}.aliyuncs.com")
    req.set_version(API_VERSION)
    req.set_protocol_type("https")
    req.set_method(method)
    req.set_uri_pattern(uri)
    req.add_header("Content-Type", "application/json")
    return req


def _do_request(client, req, *, action: str) -> dict:
    """执行请求并把响应解析为 dict，网络/解析错误转成可读的 TingwuError。"""
    try:
        raw = client.do_action_with_exception(req)
    except Exception as exc:  # SDK 会抛 ServerException / ClientException
        raise TingwuError(
            f"{action} 调用失败：{exc}\n"
            "排查建议：确认 AccessKey 是否有听悟权限、AppKey 是否正确、"
            "网络是否可达 tingwu.<region>.aliyuncs.com。"
        ) from exc

    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise TingwuError(
            f"{action} 返回内容无法解析为 JSON：{raw!r}"
        ) from exc


def create_offline_task(
    creds: TingwuCredentials,
    file_url: str,
    *,
    source_language: str = "cn",
    task_key: Optional[str] = None,
    diarization_enabled: bool = True,
    speaker_count: int = 0,
) -> TranscriptionTask:
    """提交离线转写任务，返回含 TaskId 的 TranscriptionTask。

    只开启转写（Transcription）与说话人分离；不启用摘要/章节等大模型能力。
    speaker_count=0 表示不定人数说话人分离。
    """
    if not file_url:
        raise TingwuError("file_url 为空：离线转写必须提供公网可访问的音频 URL。")

    client = _build_client(creds)
    req = _build_common_request(creds, CREATE_TASK_URI, "PUT")
    # type=offline 作为 query 参数
    req.add_query_param("type", "offline")

    transcription: dict[str, Any] = {"OutputLevel": 1}
    if diarization_enabled:
        transcription["DiarizationEnabled"] = True
        transcription["Diarization"] = {"SpeakerCount": speaker_count}

    body: dict[str, Any] = {
        "AppKey": creds.app_key,
        "Input": {
            "SourceLanguage": source_language,
            "FileUrl": file_url,
        },
        "Parameters": {
            "Transcription": transcription,
        },
    }
    if task_key:
        body["Input"]["TaskKey"] = task_key

    req.set_content(json.dumps(body).encode("utf-8"))

    resp = _do_request(client, req, action="CreateTask")
    code = str(resp.get("Code", ""))
    if code not in ("0", "Success", "success"):
        raise TingwuError(
            "CreateTask 返回错误：\n"
            f"  Code={resp.get('Code')}\n"
            f"  Message={resp.get('Message')}\n"
            f"  完整响应：{json.dumps(resp, ensure_ascii=False)}"
        )

    data = resp.get("Data") or {}
    task_id = data.get("TaskId")
    if not task_id:
        raise TingwuError(
            "CreateTask 成功但未返回 TaskId，无法继续。\n"
            f"  完整响应：{json.dumps(resp, ensure_ascii=False)}"
        )

    return TranscriptionTask(
        task_id=task_id,
        status=data.get("TaskStatus", "ONGOING"),
        last_response=resp,
    )


def get_task_info(creds: TingwuCredentials, task_id: str) -> TranscriptionTask:
    """查询任务状态，解析出 TaskStatus 和 Result.Transcription 链接。"""
    client = _build_client(creds)
    req = _build_common_request(creds, GET_TASK_URI + task_id, "GET")

    resp = _do_request(client, req, action="GetTaskInfo")
    code = str(resp.get("Code", ""))
    if code not in ("0", "Success", "success"):
        raise TingwuError(
            "GetTaskInfo 返回错误：\n"
            f"  Code={resp.get('Code')}\n"
            f"  Message={resp.get('Message')}\n"
            f"  完整响应：{json.dumps(resp, ensure_ascii=False)}"
        )

    data = resp.get("Data") or {}
    result = data.get("Result") or {}
    return TranscriptionTask(
        task_id=task_id,
        status=data.get("TaskStatus", "UNKNOWN"),
        transcription_url=result.get("Transcription"),
        error_code=data.get("ErrorCode"),
        error_message=data.get("ErrorMessage"),
        last_response=resp,
    )


def poll_until_done(
    creds: TingwuCredentials,
    task_id: str,
    *,
    interval_seconds: int = POLL_INTERVAL_SECONDS,
    max_minutes: int = POLL_MAX_MINUTES,
    on_poll: Optional[Callable[[TranscriptionTask, int], None]] = None,
) -> TranscriptionTask:
    """每 interval_seconds 轮询一次，直到 COMPLETED / FAILED 或超时。

    on_poll(task, elapsed_seconds) 用于打印进度（不使用 HTTP 回调）。
    """
    deadline = max_minutes * 60
    elapsed = 0

    while True:
        task = get_task_info(creds, task_id)
        if on_poll:
            on_poll(task, elapsed)

        status = (task.status or "").upper()
        if status == "COMPLETED":
            if not task.transcription_url:
                raise TingwuError(
                    "任务已 COMPLETED，但 Result.Transcription 为空，拿不到转写结果。\n"
                    f"  完整响应：{json.dumps(task.last_response, ensure_ascii=False)}"
                )
            return task
        if status == "FAILED":
            raise TingwuError(
                "任务转写失败（TaskStatus=FAILED）：\n"
                f"  ErrorCode={task.error_code}\n"
                f"  ErrorMessage={task.error_message}\n"
                f"  完整响应：{json.dumps(task.last_response, ensure_ascii=False)}"
            )

        if elapsed >= deadline:
            raise TingwuError(
                f"轮询超时：等待超过 {max_minutes} 分钟任务仍未完成"
                f"（最后状态 {task.status}）。\n"
                "可稍后凭 TaskId 重新查询，或检查音频文件是否过大 / 不可访问。"
            )

        time.sleep(interval_seconds)
        elapsed += interval_seconds


def download_transcription(url: str, dest_path) -> None:
    """下载 Result.Transcription 指向的 JSON 到 dest_path。"""
    try:
        import requests
    except ImportError as exc:
        raise TingwuError(
            "未安装 requests，无法下载转写结果。请运行：pip install -r requirements.txt"
        ) from exc

    from pathlib import Path

    dest = Path(dest_path)
    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise TingwuError(
            f"下载转写结果失败：{exc}\n"
            "该链接为带时效的预签名 URL，若已过期请重新调用 GetTaskInfo 获取新链接。"
        ) from exc

    dest.write_bytes(resp.content)
