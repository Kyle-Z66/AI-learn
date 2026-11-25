"""
第 5 周 · 核心机制 05：哪些错误值得重试
================================================================
【对应知识点】文档第 5 周：429/5xx/超时可重试，400/鉴权失败不可重试

【周次学习要点】
  - 重试只针对"暂时性故障"；确定性错误重试多少次都是浪费配额。
  - 判据集中到一个函数，才能让降级链、网关、脚本用同一套口径。
  - 未知异常默认不重试：宁可快速失败，也不要放大未知故障。

【易忽略细节】
  1. 429 可重试，但必须遵守 Retry-After，否则仍会被限流。
  2. asyncio.TimeoutError 在 Python 3.11+ 就是内置 TimeoutError，统一判据即可。
  3. 鉴权失败重试会触发风控，绝不能进入退避循环。

【示例用途】可运行：`python -m week05.core_mechanisms.05_retryable_errors`
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

from week05.engineering.retry import (
    HttpStatusError,
    NonRetryableError,
    RetryPolicy,
    call_with_retry,
    is_retryable,
)


async def demo() -> None:
    errors: list[BaseException] = [
        HttpStatusError(429, "限流", retry_after=1.0),
        HttpStatusError(503, "服务不可用"),
        HttpStatusError(400, "参数错误"),
        HttpStatusError(401, "鉴权失败"),
        TimeoutError("读取超时"),
        ConnectionError("连接失败"),
        NonRetryableError("业务校验失败"),
        ValueError("未知解析异常"),
    ]
    for exc in errors:
        status = exc.status_code if isinstance(exc, HttpStatusError) else "-"
        print(f"{type(exc).__name__:<20} status={status:<4} 可重试={is_retryable(exc)}")

    attempts = 0

    async def broken() -> str:
        nonlocal attempts
        attempts += 1
        raise HttpStatusError(401, "API Key 无效")

    try:
        await call_with_retry(broken, RetryPolicy(max_attempts=5))
    except HttpStatusError as exc:
        print(f"不可重试错误只调用 {attempts} 次（配置上限 5）：{exc}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(demo())
