"""
第 3 周单元测试 · 动手项目：P1 多模型统一网关 v0.1
"""
from __future__ import annotations

import pytest
from week02.engineering.provider_adapters import get_provider
from week03.engineering.gateway_protocol import GatewayConfig
from week03.engineering.provider_registry import FaultInjectingProvider
from week03.p1_gateway.gateway import P1Gateway
from week03.p1_gateway.models import GatewayRequest

REQUEST = GatewayRequest(messages=[{"role": "user", "content": "cyclone 级别 4，影响 12 人"}])


async def test_gateway_calls_all_three_models() -> None:
    for name in ("qwen", "deepseek", "glm"):
        gateway = P1Gateway(GatewayConfig(order=(name,), use_mock=True))
        response = await gateway.chat(REQUEST)
        assert response.model in {"qwen-plus", "deepseek-chat", "glm-4-plus"}
        assert response.cost_yuan > 0
        assert gateway.stats.succeeded == 1


async def test_gateway_records_fallback_stats() -> None:
    faulty = FaultInjectingProvider(get_provider("deepseek", use_mock=True), fail_times=1)
    gateway = P1Gateway(
        GatewayConfig(order=("deepseek", "qwen"), use_mock=True),
        overrides={"deepseek": faulty},
    )
    response = await gateway.chat(REQUEST)
    assert response.model == "qwen-plus"
    assert gateway.stats.total == 1
    assert gateway.stats.fallback_used == 1
    assert gateway.stats.records[0].provider == "qwen"
    assert "降级 1" in gateway.report()


async def test_gateway_all_fail_records_error() -> None:
    always_fail = FaultInjectingProvider(get_provider("deepseek", use_mock=True), fail_times=100)
    gateway = P1Gateway(
        GatewayConfig(order=("deepseek",), use_mock=True),
        overrides={"deepseek": always_fail},
    )
    with pytest.raises(RuntimeError):
        await gateway.chat(REQUEST)
    assert gateway.stats.total == 1
    assert gateway.stats.succeeded == 0
    assert gateway.stats.records[0].ok is False


def test_report_format() -> None:
    gateway = P1Gateway(GatewayConfig(use_mock=True))
    assert "请求 0" in gateway.report()
    assert "累计成本" in gateway.report()
