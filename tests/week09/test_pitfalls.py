"""
第 9 周单元测试 · 混合检索认知误区
"""
from __future__ import annotations

import importlib
from typing import Any

from week09.pitfalls.extra_gotchas import (
    ES_MAPPING,
    HYBRID_NECESSITY,
    demo,
    demo_es_mapping,
    demo_necessity,
    demo_rrf_k_stability,
)
from week09.pitfalls.hybrid_pitfalls import (
    demo_dedup_loses_score,
    demo_filter_after_fusion,
    demo_raw_score_addition,
    demo_tokenizer_mismatch,
    normalized_sum,
    raw_sum,
)

_filter_module: Any = importlib.import_module(
    "week09.core_mechanisms.08_filter_and_fusion"
)


def test_hybrid_pitfall_demos_runnable() -> None:
    demo_raw_score_addition()
    demo_dedup_loses_score()
    demo_tokenizer_mismatch()
    demo_filter_after_fusion()


def test_raw_score_addition_trap_is_reproduced() -> None:
    assert raw_sum()["c-01"] > raw_sum()["c-02"]
    assert normalized_sum()["c-02"] > normalized_sum()["c-01"]


def test_tokenizer_mismatch_loses_proper_noun() -> None:
    indexed = {"sgcc-4012", "断路器", "巡检"}
    queried = {"sgcc", "4012", "断路", "路器", "巡检"}
    assert "sgcc-4012" not in indexed & queried


def test_filter_after_fusion_loses_top_k_slots() -> None:
    query = "SGCC-4012 巡检"
    assert len(_filter_module.filter_then_fuse(query)) == 2
    assert len(_filter_module.fuse_then_filter(query)) < 2


def test_extra_gotcha_demos_runnable() -> None:
    assert len(HYBRID_NECESSITY) == 3
    assert len(ES_MAPPING) == 4
    demo_necessity()
    demo_es_mapping()
    demo_rrf_k_stability()
    demo()
