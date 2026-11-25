"""
第 5 周 · 核心机制 03：熔断感知的降级链
================================================================
【对应知识点】文档第 5 周：多模型降级链（熔断 + 自动切换）

【周次学习要点】
  - 第 3 周的降级链靠 try/except；本周加上熔断器，已知故障模型直接跳过。
  - 降级判定看"实际使用的 provider"，账单也记在它头上。
  - 熔断打开时要快速跳过，不能每次都等它超时后才切换。

【易忽略细节】
  1. 熔断参数用 failure_threshold=1 只为演示；生产一般用 5（文档默认值）。
  2. 降级成功也要记录 TTFT/成本，否则监控里看不到"用户其实等了两家"。
  3. 这里显式指定 qwen 优先（第 3 周默认顺序是 deepseek 优先），才能看到降级。
  4. MockProvider 复用第 2 周实现，无需 API Key。

【示例用途】可运行：`python -m week05.core_mechanisms.03_degradation_chain`
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

import asyncio
from typing import Any

from week02.engineering.provider_adapters import ChatResponse, LLMProvider, get_provider

from week05.engineering.circuit_breaker import BreakerConfig, CircuitBreaker
from week05.engineering.cost_report import estimate_cost


class BrokenProvider:
    """只抛异常的假 provider，用于验证自动降级。"""

    def __init__(self) -> None:
        self.calls = 0

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0,
        max_tokens: int = 512,
        **opts: Any,
    ) -> ChatResponse:
        self.calls += 1
        raise ConnectionError("模拟 qwen 服务不可用")


async def call_with_fallback(
    messages: list[dict[str, str]],
    providers: dict[str, LLMProvider],
    breakers: dict[str, CircuitBreaker],
    order: tuple[str, ...] = ("qwen", "deepseek", "glm"),
) -> tuple[str, str, float]:
    """按优先级尝试；熔断打开的模型跳过，全部不可用才抛错。"""
    for name in order:
        breaker = breakers[name]
        if not await breaker.allow_request():
            print(f"  {name} 熔断中 → 直接跳过，不浪费超时预算")
            continue
        try:
            response = await providers[name].chat(messages)
        except Exception as exc:
            await breaker.record_failure()
            print(f"  {name} 调用失败（{exc}）→ 尝试下一家")
            continue
        await breaker.record_success()
        cost = estimate_cost(name, response.input_tokens, response.output_tokens)
        return response.content, name, cost
    raise RuntimeError("所有模型均不可用")


async def demo() -> None:
    providers: dict[str, LLMProvider] = {
        "qwen": BrokenProvider(),
        "deepseek": get_provider("deepseek", use_mock=True),
        "glm": get_provider("glm", use_mock=True),
    }
    breakers = {
        name: CircuitBreaker(
            name,
            BreakerConfig(failure_threshold=1, recovery_timeout=60.0, success_threshold=1),
        )
        for name in providers
    }
    messages = [{"role": "user", "content": "系统 cyclone 级别 2 影响 30 人"}]

    for index in range(2):
        print(f"第 {index + 1} 次请求：")
        content, used, cost = await call_with_fallback(messages, providers, breakers)
        print(f"  实际使用={used} 成本={cost:.4f} 元 内容片段={content[:40]}")
    print("qwen 熔断器状态：", breakers["qwen"].snapshot().state)


if __name__ == "__main__":
    asyncio.run(demo())
