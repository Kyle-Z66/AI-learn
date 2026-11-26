"""
第 12 周单元测试 · 10 个核心机制样例均可运行 + 函数级逻辑
"""
from __future__ import annotations

import importlib
import inspect
from typing import Any

from week12.engineering.golden_set import load_golden_set

MODULES = (
    "01_golden_set_schema",
    "02_labeling_rules",
    "03_recall_at_k",
    "04_mrr",
    "05_context_precision_recall",
    "06_faithfulness",
    "07_answer_relevance",
    "08_ablation_matrix",
    "09_ci_gate",
    "10_report_writer",
)


def load(name: str) -> Any:
    return importlib.import_module(f"week12.core_mechanisms.{name}")


async def test_all_core_scripts_runnable() -> None:
    for name in MODULES:
        result: Any = load(name).demo()
        if inspect.isawaitable(result):
            await result


def test_golden_set_schema() -> None:
    module = load("01_golden_set_schema")
    cases = load_golden_set()
    described = module.describe_case(cases[0])
    assert described["relevant_chunk_ids"] == cases[0].relevant_chunk_ids
    assert {"question", "answer", "relevant_chunk_ids", "metadata"} <= set(
        described["payload_keys"]
    )


def test_labeling_rules() -> None:
    module = load("02_labeling_rules")
    assert len(module.LABELING_RULES) == 4
    assert module.check_label_rules(load_golden_set()) == ()


def test_recall_at_k_logic() -> None:
    module = load("03_recall_at_k")
    found, gold = module.QUERY_CASES[0]
    assert len(module.QUERY_CASES) == 3
    assert module.recall_at_k(found, gold, 5) == 1.0
    assert module.recall_at_k(found, gold, 1) == 0.5
    assert module.recall_at_k(module.QUERY_CASES[1][0], gold, 5) == 0.0


def test_mrr_logic() -> None:
    module = load("04_mrr")
    assert module.reciprocal_rank(["x", "a"], ["a"]) == 0.5
    assert module.mrr(module.RANKINGS, module.GOLD) > 0


def test_context_metrics_logic() -> None:
    module = load("05_context_precision_recall")
    found, gold = module.RETRIEVED, module.RELEVANT
    assert module.context_precision(found, gold, 5) == 2 / 5
    assert module.context_recall(found, gold) == 2 / 3


def test_faithfulness_logic() -> None:
    module = load("06_faithfulness")
    assert module.faithfulness(
        "级别为 2 级，影响 30 名用户，负责人张伟 [1]", module.CONTEXT, ("张伟", "李四")
    ) == 1.0
    assert module.faithfulness(
        "级别为 5 级，负责人李四", module.CONTEXT, ("张伟", "李四")
    ) < 1.0


def test_answer_relevance_logic() -> None:
    module = load("07_answer_relevance")
    direct = module.answer_relevance(module.QUESTION, "系统 cyclone 影响 30 名用户。")
    off_topic = module.answer_relevance(module.QUESTION, "系统 cyclone 的负责人为张伟。")
    assert direct > off_topic


def test_ablation_subset() -> None:
    module = load("08_ablation_matrix")
    assert module.DEMO_CASE_COUNT == 20


def test_ci_gate_logic() -> None:
    module = load("09_ci_gate")
    assert module.compare_to_baseline(module.CURRENT, module.BASELINE).passed
    broken = module.compare_to_baseline(module.BROKEN, module.BASELINE)
    assert not broken.passed and "recall_at_k" in broken.regressions
    assert module.run_gate(module.BROKEN, module.BASELINE) == 1


def test_report_writer_logic() -> None:
    module = load("10_report_writer")
    scores = module.demo_scores(1)
    assert scores.p95_latency_ms > module.demo_scores(0).p95_latency_ms
    report = load("10_report_writer").render_markdown_report([])
    assert "| 配置 |" in report
