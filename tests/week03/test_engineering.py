"""
第 3 周单元测试 · 工程层：网关协议、配置切换与降级链
"""
from __future__ import annotations

import pytest
from week02.engineering.provider_adapters import get_provider
from week03.engineering.gateway_protocol import GatewayConfig, LLMResponse, calculate_cost
from week03.engineering.provider_registry import FaultInjectingProvider, ProviderRegistry

MESSAGES: list[dict[str, str]] = [{"role": "user", "content": "系统 isc 故障，级别 3"}]


def test_calculate_cost_formula() -> None:
    assert calculate_cost(1000, 500, 0.5, 1.0) == pytest.approx(1.0)


def test_gateway_config_defaults() -> None:
    config = GatewayConfig()
    assert config.order == ("deepseek", "qwen", "glm")
    assert config.use_mock is True
    assert set(config.pricing) == {"qwen", "deepseek", "glm"}


def test_llm_response_fields() -> None:
    response = LLMResponse("内容", "qwen-plus", 10, 20, 1.5, 0.05)
    assert response.model == "qwen-plus"
    assert response.cost_yuan == pytest.approx(0.05)


async def test_registry_config_switch() -> None:
    registry = ProviderRegistry(GatewayConfig(order=("qwen",), use_mock=True))
    response = await registry.chat(MESSAGES)
    assert response.model == "qwen-plus"
    assert registry.last_used == "qwen"


async def test_registry_fallback_to_second_model() -> None:
    faulty = FaultInjectingProvider(get_provider("deepseek", use_mock=True), fail_times=1)
    registry = ProviderRegistry(
        GatewayConfig(order=("deepseek", "qwen"), use_mock=True),
        overrides={"deepseek": faulty},
    )
    response = await registry.chat(MESSAGES)
    assert response.model == "qwen-plus"
    assert registry.last_used == "qwen"
    assert faulty.calls == 1


async def test_registry_all_models_fail() -> None:
    # 用永久故障的 Provider 模拟"所有模型调用失败"；未知模型属配置错误，会直接抛 ValueError
    always_fail = FaultInjectingProvider(get_provider("deepseek", use_mock=True), fail_times=100)
    registry = ProviderRegistry(
        GatewayConfig(order=("deepseek",), use_mock=True),
        overrides={"deepseek": always_fail},
    )
    with pytest.raises(RuntimeError, match="所有模型均不可用"):
        await registry.chat(MESSAGES)
