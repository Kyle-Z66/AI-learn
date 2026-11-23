"""
第 2 周 · 动手项目：结构化输出 —— 校验 + 错误回灌重试
================================================================
【对应知识点】文档第 2 周「结构化输出」标准写法：
              "解析失败 → 自动重试并附上错误原因 → 最多 3 次"

【周次学习要点】
  - 抽取类任务：temperature=0 + response_format=json_object + Pydantic 校验三重保障。
  - 重试的关键不是"原样重发"，而是把 `ValidationError` 文本拼进下一轮 user 消息，
    让模型知道哪里错了 —— 这是文档强调的"很实用"的技巧。
  - 统一用 LLMProvider 接口（第 2 周动作 2），Mock 与真实模型共用同一套逻辑。

【易忽略细节 / 对照文档补足】
  1. 文档只写了捕获 ValidationError；这里补足**错误分类**：429/5xx 可重试，400/401 重试无用。
  2. 重试耗尽要抛出带最后一次错误的异常，便于上层告警，不能静默返回空结果。
  3. `response_format` 通过 **opts 透传给 provider；Mock 会忽略它，真实接口会生效。
  4. 每次重试都记录 attempt，生产环境应打日志/埋点（第 5 周可观测性会展开）。

【示例用途】被 __main__.py / prompt_lab/runner.py 引用；可运行入口见 week02/structured_output/
"""
from __future__ import annotations

from pydantic import ValidationError

from week02.engineering.provider_adapters import LLMProvider
from week02.structured_output.models import TicketExtract

SYSTEM_PROMPT = (
    "你是技术文档信息抽取助手。只输出 JSON，不要任何解释文字。"
    "字段：system_name(字符串)、severity(1-5 的整数)、affected_users(非负整数)。"
)


class ProviderError(Exception):
    """模拟 HTTP 层错误，携带状态码用于判断是否可重试。"""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code


def is_retryable(exc: Exception) -> bool:
    """错误分类：限流与服务端错误可重试，参数/鉴权错误重试也没用（补足点）。"""
    if isinstance(exc, ProviderError):
        return exc.status_code == 429 or exc.status_code >= 500
    return isinstance(exc, ValidationError)  # 输出格式错误可通过回灌修正


async def extract_with_retry(
    text: str,
    provider: LLMProvider,
    max_retries: int = 3,
    *,
    verbose: bool = False,
) -> TicketExtract:
    """结构化提取主流程：校验失败 → 错误回灌 → 最多 max_retries 次。"""
    last_error = ""
    for attempt in range(1, max_retries + 1):
        user_content = text
        if last_error:
            # 核心技巧：把上一次的错误原因回灌给模型，让它自己修
            user_content = f"{text}\n\n上一次输出未通过校验：{last_error}\n请修正后重新输出。"

        if verbose:
            print(f"    第 {attempt}/{max_retries} 次调用，回灌错误={bool(last_error)}")

        response = await provider.chat(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0,  # 抽取类任务必须 0（文档要求）
            response_format={"type": "json_object"},
        )

        try:
            return TicketExtract.model_validate_json(response.content)
        except ValidationError as exc:
            last_error = str(exc)
            if not is_retryable(exc):
                raise
            continue

    raise ValueError(f"结构化输出失败（已重试 {max_retries} 次）: {last_error}")
