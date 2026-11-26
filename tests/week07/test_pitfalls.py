"""
第 7 周单元测试 · 解析结构丢失与调参顺序误区
"""
from __future__ import annotations

from week07.engineering.models import PAGE_SEPARATOR
from week07.pitfalls.document_pitfalls import (
    CLAUSE_RE,
    demo,
    demo_fixed_cuts_clause,
    demo_lost_heading,
    demo_lost_page,
    demo_lost_table,
    pages_preserved,
    starts_mid_clause,
    table_columns_preserved,
)
from week07.pitfalls.extra_gotchas import (
    DEBUG_ORDER,
    GOOD_CHUNK_CRITERIA,
    demo_chunk_criteria,
    demo_debug_order,
    demo_overlap_cost,
    overlap_cost,
)


def test_document_pitfall_helpers() -> None:
    assert pages_preserved(f"a{PAGE_SEPARATOR}b") == 1
    assert table_columns_preserved(["a | b", "no table"]) == 1
    assert CLAUSE_RE.search("第7条 出现 ERR_4012")
    assert starts_mid_clause("7条 出现 ERR_4012 时先查上游")
    assert not starts_mid_clause("第7条 出现 ERR_4012 时先查上游")


def test_document_pitfall_demos_runnable() -> None:
    demo_lost_page()
    demo_lost_table()
    demo_lost_heading()
    demo_fixed_cuts_clause()
    demo()


def test_chunk_criteria_and_debug_order() -> None:
    assert len(GOOD_CHUNK_CRITERIA) == 3
    assert DEBUG_ORDER[0] == "解析保真"
    assert DEBUG_ORDER.index("召回率") < DEBUG_ORDER.index("重排")
    assert overlap_cost(512, 64, 1) == 0
    assert overlap_cost(512, 64, 5) == 256


def test_extra_gotcha_demos_runnable() -> None:
    demo_chunk_criteria()
    demo_overlap_cost()
    demo_debug_order()
