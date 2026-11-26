"""
第 10 周单元测试 · Rerank 认知误区
"""
from __future__ import annotations

import importlib
from typing import Any

from week10.pitfalls.extra_gotchas import (
    BUDGET_RULES,
    DEBUG_ORDER,
    JAVA_ANALOGY,
    demo,
    demo_budget_rules,
    demo_debug_order,
    demo_java_analogy,
)
from week10.pitfalls.rerank_pitfalls import (
    demo_degraded_flag_missing,
    demo_rerank_as_retrieval,
    demo_timeout_drags_request,
    demo_too_many_candidates,
)

_latency_module: Any = importlib.import_module(
    "week10.core_mechanisms.08_latency_model"
)
estimate_latency_ms = _latency_module.estimate_latency_ms


def test_rerank_pitfall_demos_runnable() -> None:
    demo_timeout_drags_request()
    demo_too_many_candidates()
    demo_rerank_as_retrieval()
    demo_degraded_flag_missing()


def test_latency_grows_with_candidates() -> None:
    assert estimate_latency_ms(50) < estimate_latency_ms(100)
    assert estimate_latency_ms(100) < estimate_latency_ms(200)


def test_rerank_cannot_recall_missing_documents() -> None:
    pool = {"d1", "d2"}
    assert "d9" not in pool


def test_extra_gotcha_demos_runnable() -> None:
    assert len(JAVA_ANALOGY) == 3
    assert len(BUDGET_RULES) == 2
    assert len(DEBUG_ORDER) == 3
    demo_java_analogy()
    demo_budget_rules()
    demo_debug_order()
    demo()
