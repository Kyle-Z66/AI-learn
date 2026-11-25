"""
第 5 周单元测试 · 10 个核心机制样例均可运行
"""
from __future__ import annotations

import importlib
import inspect
from typing import Any

from week02.engineering.provider_adapters import LLMProvider, get_provider
from week05.engineering.circuit_breaker import BreakerConfig, BreakerState, CircuitBreaker

MODULES = (
    "01_circuit_breaker_states",
    "02_half_open_probe",
    "03_degradation_chain",
    "04_timeout_layers",
    "05_retryable_errors",
    "06_exponential_backoff",
    "07_idempotency_key",
    "08_audit_fields",
    "09_cost_aggregation",
    "10_observability_metrics",
)


async def test_all_core_scripts_runnable() -> None:
    """数字前缀模块不能直接 import，用 importlib 动态加载后逐个跑 demo。"""
    for name in MODULES:
        module = importlib.import_module(f"week05.core_mechanisms.{name}")
        result: Any = module.demo()
        if inspect.isawaitable(result):
            await result


async def test_degradation_chain_skips_open_provider() -> None:
    module = importlib.import_module("week05.core_mechanisms.03_degradation_chain")
    providers: dict[str, LLMProvider] = {
        "qwen": module.BrokenProvider(),
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
    _, used, cost = await module.call_with_fallback(messages, providers, breakers)
    assert used == "deepseek"
    assert cost > 0
    assert breakers["qwen"].state is BreakerState.OPEN


def test_cost_helper_uses_provider_price() -> None:
    module = importlib.import_module("week05.core_mechanisms.09_cost_aggregation")
    qwen = module.make_record("2026-11-25", "qwen", 1000)
    deepseek = module.make_record("2026-11-25", "deepseek", 1000)
    assert qwen.cost_yuan > deepseek.cost_yuan
