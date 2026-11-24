"""
第 3 周 · 工程规范示范：配置切换 + 降级链 + 成本打印
================================================================
【对应知识点】文档第 3 周 P1 v0.1 三条要求：配置切换 / 降级链 / 统一响应对象

【周次学习要点】
  - 同一套代码，改配置即可切换模型；调用方完全不感知厂商差异。
  - 降级链用最小骨架验证思路，熔断与审计留到第 5 周。
  - 统一响应把"内容、实际模型、token、耗时、成本"打成一包，便于上层与对账。

【易忽略细节】
  1. 单价是示意值，真实项目从配置读；价格随厂商调整，不写死在代码里。
  2. 降级后响应里的 model 是实际备用模型，不是请求时配置的首选模型。
  3. 无 API Key 时用 Mock，三家都能跑；配了 Key 走真实适配器即可。

【示例用途】可运行：`python -m week03.engineering.engineering_demo`
             测试见 tests/week03/test_engineering.py
"""
from __future__ import annotations

import asyncio

from week02.engineering.provider_adapters import get_provider

from week03.engineering.gateway_protocol import GatewayConfig
from week03.engineering.provider_registry import FaultInjectingProvider, ProviderRegistry

MESSAGES: list[dict[str, str]] = [
    {"role": "user", "content": "系统 isc 故障，级别 3，影响 50 人"},
]


async def demo_config_switch() -> None:
    """三家模型各调一次：只改配置，不动调用代码。"""
    for name in ("qwen", "deepseek", "glm"):
        registry = ProviderRegistry(GatewayConfig(order=(name,), use_mock=True))
        response = await registry.chat(MESSAGES)
        print(
            f"配置 {name:<9} → 实际模型 {response.model:<15} "
            f"token {response.input_tokens}/{response.output_tokens} "
            f"耗时 {response.latency_ms:.2f}ms 成本 {response.cost_yuan:.4f}"
        )


async def demo_fallback() -> None:
    """主模型前两次失败，自动切到备用模型。"""
    faulty = FaultInjectingProvider(get_provider("deepseek", use_mock=True), fail_times=2)
    config = GatewayConfig(order=("deepseek", "qwen"), use_mock=True)
    registry = ProviderRegistry(config, overrides={"deepseek": faulty})
    response = await registry.chat(MESSAGES)
    print("降级链结果：", response.model)
    print("主模型调用次数：", faulty.calls, "| 最终使用：", registry.last_used)


if __name__ == "__main__":
    asyncio.run(demo_config_switch())
    asyncio.run(demo_fallback())
