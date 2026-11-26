"""
第 12 周单元测试 · 工程层：golden set / 指标 / 四配置评测 / 报告 / 门禁
"""
from __future__ import annotations

from pathlib import Path

from week12.engineering.ci_gate import compare_to_baseline, run_gate
from week12.engineering.engineering_demo import demo
from week12.engineering.golden_set import (
    DEFAULT_GOLDEN_SET,
    golden_set_summary,
    load_golden_set,
    validate_golden_set,
)
from week12.engineering.metrics import (
    answer_relevance,
    context_precision,
    context_recall,
    faithfulness,
    mean,
    mrr,
    p95_latency_ms,
    recall_at_k,
    reciprocal_rank,
)
from week12.engineering.models import EvalScores, GoldenCase
from week12.engineering.report import render_markdown_report
from week12.engineering.runner import run_all_configs, run_evaluation


def test_golden_set_loading_and_validation() -> None:
    cases = load_golden_set()
    assert len(cases) == 100
    assert validate_golden_set(cases) == ()
    assert DEFAULT_GOLDEN_SET.exists()
    assert golden_set_summary(cases)["count"] == 100
    assert all(case.metadata["source"] == "教学样例-非真实业务数据" for case in cases)


def test_golden_case_roundtrip() -> None:
    case = GoldenCase("q", "a", ("DOC-1#p1",), {"source": "teaching"})
    restored = GoldenCase.from_dict(case.to_dict())
    assert restored == case


def test_invalid_golden_set_raises(tmp_path: Path) -> None:
    target = tmp_path / "bad.json"
    target.write_text('{"question": "q"}', encoding="utf-8")
    try:
        load_golden_set(target)
    except ValueError:
        pass
    else:
        raise AssertionError("顶层非数组应抛 ValueError")


def test_metrics_all_functions() -> None:
    assert recall_at_k(["a", "b"], ["a"], 5) == 1.0
    assert recall_at_k(["x"], ["a"], 5) == 0.0
    assert reciprocal_rank(["x", "a"], ["a"], 10) == 0.5
    assert mrr([["a"], ["x", "a"]], [["a"], ["a"]]) == 0.75
    assert context_precision(["a", "x"], ["a"], 2) == 0.5
    assert context_recall(["a", "x"], ["a", "b"]) == 0.5
    assert faithfulness("影响 30 人 [1]", "影响 30 人") == 1.0
    assert faithfulness("影响 500 人 [1]", "影响 30 人") == 0.0
    assert answer_relevance("系统 cyclone 影响多少人？", "影响 30 人") > 0
    assert p95_latency_ms([1.0, 2.0, 3.0, 4.0]) == 4.0
    assert p95_latency_ms([]) == 0.0
    assert mean([1.0, 2.0]) == 1.5 and mean([]) == 0.0


def test_runner_small_subset() -> None:
    cases = load_golden_set()[:3]
    result = run_evaluation(cases, "hybrid")
    assert result.case_count == 3
    assert len(result.per_case_recall) == 3
    assert 0 <= result.scores.recall_at_k <= 1
    assert result.scores.p95_latency_ms >= 0
    results = run_all_configs(cases)
    assert [item.config for item in results] == [
        "bm25_only", "dense_only", "hybrid", "hybrid_rerank"
    ]


def test_report_and_gate() -> None:
    results = run_all_configs(load_golden_set()[:2])
    report = render_markdown_report(results)
    assert "| 配置 |" in report and "p95 延迟(ms)" in report
    assert "逐案 Recall@5 分布" in report
    assert all(item.config in report for item in results)

    baseline = EvalScores(0.9, 0.8, 0.7, 0.9, 0.9, 0.6, 40.0)
    good = EvalScores(0.89, 0.79, 0.69, 0.89, 0.89, 0.59, 45.0)
    bad = EvalScores(0.7, 0.6, 0.5, 0.7, 0.7, 0.4, 40.0)
    assert compare_to_baseline(good, baseline).exit_code() == 0
    assert run_gate(bad, baseline) == 1
    assert "recall_at_k" in compare_to_baseline(bad, baseline).regressions


def test_engineering_demo_runs() -> None:
    demo()
