"""
第 12 周单元测试 · 评测坑点与认知边界
"""
from __future__ import annotations

from week12.pitfalls.evaluation_pitfalls import (
    demo_fabricated_data,
    demo_latency_vs_quality,
    demo_leakage,
    demo_mean_only,
)
from week12.pitfalls.extra_gotchas import (
    ABLATION_PITCH,
    ASSET_STEPS,
    GUARD_VS_SCOREBOARD,
    demo_ablation_pitch,
    demo_asset_accumulates,
    demo_few_but_gold,
    demo_guard_not_scoreboard,
)


def test_evaluation_pitfall_demos_runnable() -> None:
    demo_fabricated_data()
    demo_leakage()
    demo_mean_only()
    demo_latency_vs_quality()


def test_extra_gotcha_demos_runnable() -> None:
    assert len(ASSET_STEPS) == 3
    assert len(GUARD_VS_SCOREBOARD) == 2
    assert "消融" in ABLATION_PITCH
    demo_asset_accumulates()
    demo_few_but_gold()
    demo_ablation_pitch()
    demo_guard_not_scoreboard()


def test_leakage_split_is_disjoint() -> None:
    from week12.engineering.golden_set import load_golden_set

    cases = load_golden_set()
    dev = [case for case in cases if int(case.metadata["case_id"][-1]) % 5 != 0]
    holdout = [case for case in cases if int(case.metadata["case_id"][-1]) % 5 == 0]
    assert len(dev) + len(holdout) == len(cases)
    dev_ids = {c.metadata["case_id"] for c in dev}
    holdout_ids = {c.metadata["case_id"] for c in holdout}
    assert not (dev_ids & holdout_ids)
