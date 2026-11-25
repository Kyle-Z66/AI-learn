"""
第 5 周单元测试 · 动手项目：审计链路查询与成本报表
"""
from __future__ import annotations

import importlib
from typing import Any

from week05.audit_lab.models import AUDIT_FIELD_COUNT, LabCase, to_audit_record
from week05.audit_lab.reporter import (
    build_metrics,
    print_cost_report,
    print_trace_chain,
)
from week05.engineering.audit import SQLiteAuditStore


def load_main() -> Any:
    """__main__ 不是常规模块名，用 importlib 动态加载。"""
    return importlib.import_module("week05.audit_lab.__main__")


def build_store() -> tuple[SQLiteAuditStore, list[LabCase]]:
    main = load_main()
    cases: list[LabCase] = main.build_cases()
    store = SQLiteAuditStore()
    for index, case in enumerate(cases, start=1):
        store.append(to_audit_record(case, index))
    return store, cases


def test_audit_field_count_is_19() -> None:
    assert AUDIT_FIELD_COUNT == 19


def test_lab_case_expands_to_audit_record() -> None:
    case = LabCase("trace-1", "ticket_extract", "qwen", "success", 1000, 200, 500.0)
    record = to_audit_record(case, 1)
    assert record.trace_id == "trace-1"
    assert record.request_id == "trace-1-01"
    assert record.cost_yuan > 0
    cached = LabCase("trace-2", "ticket_extract", "qwen", "cache_hit", 0, 0, 10.0)
    assert to_audit_record(cached, 1).cost_yuan == 0


def test_trace_chain_query_and_daily_report() -> None:
    store, cases = build_store()
    chain = print_trace_chain(store, cases[0].trace_id)
    assert "共 2 条记录" in chain
    assert "qwen" in chain and "deepseek" in chain
    assert "降级=True" in chain
    report = print_cost_report(store)
    assert "2026-11-25" in report
    assert "deepseek" in report and "qwen" in report
    assert "合计" in report


def test_metrics_from_audit_source() -> None:
    store, cases = build_store()
    ttfts = {
        f"{case.trace_id}-{index:02d}": 120.0
        for index, case in enumerate(cases, start=1)
        if case.status.startswith("success")
    }
    snapshot = build_metrics(store.all_records(), ttfts)
    assert snapshot.count == 5
    assert snapshot.success_rate == 0.6
    assert snapshot.error_429_ratio == 0.2
    assert snapshot.cache_hit_rate == 0.2


def test_main_entry_runnable() -> None:
    load_main().demo()
