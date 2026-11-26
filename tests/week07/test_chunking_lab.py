"""
第 7 周单元测试 · 动手项目：同语料四策略对比
"""
from __future__ import annotations

from week07.chunking_lab.__main__ import main
from week07.chunking_lab.corpus import (
    CORPUS_MARKDOWN,
    build_corpus_document,
    corpus_headings,
)
from week07.chunking_lab.evaluate import (
    StrategyResult,
    build_results,
    format_results,
    is_structural_truncation,
    manual_review_hints,
    truncation_ratio,
)
from week07.engineering.models import Chunk


def test_corpus_has_required_structures() -> None:
    assert "SGCC-4012" in CORPUS_MARKDOWN
    assert "ERR_4012" in CORPUS_MARKDOWN
    assert "第13条" in CORPUS_MARKDOWN
    assert "| 故障码 |" in CORPUS_MARKDOWN
    assert len(corpus_headings()) >= 8


def test_build_results_has_four_strategies() -> None:
    document = build_corpus_document()
    results = build_results(document)
    assert len(results) == 4
    assert [result.name[0] for result in results] == ["A", "B", "C", "D"]
    assert all(isinstance(result, StrategyResult) for result in results)
    assert all(result.count > 0 for result in results)
    assert all(0.0 <= result.truncation_ratio <= 1.0 for result in results)
    assert all(result.samples for result in results)
    assert "chunk数" in format_results(results)


def test_structural_truncation_detection() -> None:
    assert is_structural_truncation("| ERR_4012 | 检查上游")
    assert not is_structural_truncation("| ERR_4012 | 检查上游 |")
    assert is_structural_truncation("第7条 出现 ERR_4012 时先查上游")
    assert not is_structural_truncation("第7条 出现 ERR_4012 时先查上游。")
    assert truncation_ratio([]) == 0.0
    plain = Chunk("c1", "d1", "普通正文没有结构标记")
    assert truncation_ratio([plain]) == 0.0


def test_manual_review_hints_are_actionable() -> None:
    hints = manual_review_hints()
    assert len(hints) >= 3
    assert any("SGCC-4012" in hint for hint in hints)


def test_lab_cli_runnable() -> None:
    main()
