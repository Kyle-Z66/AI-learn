"""
第 3 周 · 动手项目入口：P1 多模型统一网关 v0.1
================================================================
【示例用途】可运行：`python -m week03.p1_gateway`
             无 API Key 也能跑：默认使用第 2 周的 MockProvider。

【本周边界】只验证"配置切换 + 降级链 + 成本打印"；熔断、审计、可观测在第 5 周。
"""
from __future__ import annotations

import asyncio

from week02.engineering.provider_adapters import get_provider

from week03.engineering.gateway_protocol import GatewayConfig
from week03.engineering.provider_registry import FaultInjectingProvider
from week03.p1_gateway.gateway import P1Gateway
from week03.p1_gateway.models import GatewayRequest

MESSAGES: list[dict[str, str]] = [
    {"role": "user", "content": "系统 isc 故障，级别 3，影响 50 人"},
]


async def main() -> None:
    """演示两件事：三家统一调用、主模型故障时自动降级。"""
    print("=== 1. 同一套代码调通三家模型 ===")
    for name in ("qwen", "deepseek", "glm"):
        gateway = P1Gateway(GatewayConfig(order=(name,), use_mock=True))
        response = await gateway.chat(GatewayRequest(MESSAGES))
        print(
            f"配置 {name:<9} → 实际 {response.model:<15} "
            f"token {response.input_tokens}/{response.output_tokens} "
            f"成本 {response.cost_yuan:.4f}"
        )

    print("=== 2. 降级链：主模型故障自动切换 ===")
    faulty = FaultInjectingProvider(get_provider("deepseek", use_mock=True), fail_times=1)
    gateway = P1Gateway(
        GatewayConfig(order=("deepseek", "qwen"), use_mock=True),
        overrides={"deepseek": faulty},
    )
    response = await gateway.chat(GatewayRequest(MESSAGES))
    print("实际使用模型：", response.model)
    print("主模型调用次数：", faulty.calls)
    print("网关统计：", gateway.report())


if __name__ == "__main__":
    asyncio.run(main())
