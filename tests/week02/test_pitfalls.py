"""
第 2 周单元测试 · LLM 认知误区与补足点
"""
from __future__ import annotations

from week02.pitfalls import extra_gotchas, llm_pitfalls


def test_all_pitfalls_runnable() -> None:
    for fn in (
        llm_pitfalls.pitfall_1,
        llm_pitfalls.pitfall_2,
        llm_pitfalls.pitfall_3,
        llm_pitfalls.pitfall_4,
        llm_pitfalls.pitfall_5,
        llm_pitfalls.pitfall_6,
        llm_pitfalls.pitfall_7,
        llm_pitfalls.pitfall_8,
    ):
        fn()


def test_extra_gotchas_runnable() -> None:
    extra_gotchas.demo_float_nondeterminism()
    extra_gotchas.demo_sse_chunking()
    extra_gotchas.demo_cache_prefix()
    extra_gotchas.demo_fallback_cost()


def test_usage_record() -> None:
    record = extra_gotchas.UsageRecord("qwen-plus", 100, 50)
    assert record.model == "qwen-plus"
    assert record.input_tokens + record.output_tokens == 150
