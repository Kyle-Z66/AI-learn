"""
第 11 周单元测试 · 生成侧坑点与认知边界
"""
from __future__ import annotations

from week11.pitfalls.extra_gotchas import (
    CITATION_VS_PLAIN,
    FIX_ORDER,
    REFUSAL_SIGNALS,
    demo_citation_is_the_difference,
    demo_fix_retrieval_first,
    demo_refusal_is_success,
)
from week11.pitfalls.generation_pitfalls import (
    demo_budget_cuts_evidence,
    demo_citation_drift,
    demo_fabrication_when_context_thin,
    demo_low_temp_not_enough,
)


def test_generation_pitfall_demos_runnable() -> None:
    demo_fabrication_when_context_thin()
    demo_citation_drift()
    demo_budget_cuts_evidence()
    demo_low_temp_not_enough()


def test_extra_gotcha_demos_runnable() -> None:
    assert len(FIX_ORDER) == 3
    assert len(CITATION_VS_PLAIN) == 2
    assert len(REFUSAL_SIGNALS) == 3
    demo_fix_retrieval_first()
    demo_citation_is_the_difference()
    demo_refusal_is_success()


def test_pitfall_order_and_diagnosis() -> None:
    assert "检索" in FIX_ORDER[0] and "Prompt" in FIX_ORDER[-1]
    assert any("拒答为零" in signal for signal, _ in REFUSAL_SIGNALS)
    assert "引用" in CITATION_VS_PLAIN[1][0]
