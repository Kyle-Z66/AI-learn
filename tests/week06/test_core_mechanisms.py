"""
第 6 周单元测试 · 10 个核心机制样例均可运行
"""
from __future__ import annotations

import importlib
import inspect
from typing import Any

MODULES = (
    "01_fastapi_routes",
    "02_request_response_models",
    "03_dependency_injection",
    "04_streaming_response",
    "05_health_readiness",
    "06_asgi_testing",
    "07_coverage_gate",
    "08_docker_config",
    "09_stage_checklist",
    "10_rag_preview",
)


def load(name: str) -> Any:
    return importlib.import_module(f"week06.core_mechanisms.{name}")


async def test_all_core_scripts_runnable() -> None:
    for name in MODULES:
        result: Any = load(name).demo()
        if inspect.isawaitable(result):
            await result


def test_coverage_formula() -> None:
    assert load("07_coverage_gate").coverage_rate(3, 4) == 0.75
    assert load("07_coverage_gate").coverage_rate(0, 0) == 0.0


def test_docker_static_check_all_pass() -> None:
    checks = load("08_docker_config").check_config()
    assert checks and all(checks.values())


def test_stage_checklist_is_complete() -> None:
    module = load("09_stage_checklist")
    items = module.STAGE_ITEMS
    assert len(items) == 6
    assert module.completion_rate(items) == 1.0
    assert all(item.evidence for item in items)


def test_rag_preview_has_nine_stages() -> None:
    stages = load("10_rag_preview").RAG_STAGES
    assert len(stages) == 9
    assert stages[0][0] == "解析" and stages[-1][0] == "引用"
    assert all(source and target for _, source, target in stages)
