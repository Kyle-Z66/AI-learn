"""
第 7 周 · 动手项目：四种切分策略的对比口径
================================================================
【对应知识点】文档第 7 周切分实验：chunk 数 / 平均长度 / 语义完整性 / 截断比例

【周次学习要点】
  - 四种策略跑同一份 Document，保证差异只来自策略本身。
  - "截断比例"只统计含条款或表格的 chunk，避免被普通段落稀释。
  - 语义完整性目前只能给人工抽检提示，程序不假装给出客观分数。

【易忽略细节】
  1. 表格行的完整性看最后一行是否以 "|" 收尾，不看整块竖线奇偶。
  2. 条款被切断的判据是最后一个"第 N 条"首句是否以句末标点结束。
  3. small-to-big 的小块数量天然更多，不能只按 chunk 数判定策略优劣。

【示例用途】被 chunking_lab/__main__.py 调用；测试见 tests/week07/test_chunking_lab.py
"""
from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field

from week07.engineering.chunkers import (
    estimate_tokens,
    fixed_size,
    markdown_heading,
    recursive,
    small_to_big,
)
from week07.engineering.models import Chunk, Document

CLAUSE_RE = re.compile(r"第[一二三四五六七八九十百\d]+条")
SENTENCE_END = "。；;！？.!?"


@dataclass(frozen=True)
class StrategyResult:
    """一种切分策略在语料上的可比较结果。"""

    name: str
    count: int
    avg_tokens: float
    truncation_ratio: float
    samples: tuple[str, ...] = field(default_factory=tuple)
    chunks: tuple[Chunk, ...] = field(default_factory=tuple)


def is_structural_truncation(text: str) -> bool:
    """判断表格行或条款是否被切断。"""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return False
    last = lines[-1]
    if last.startswith("|") and not last.endswith("|"):
        return True
    if not last.startswith("|") and last.endswith("|"):
        return True
    matches = list(CLAUSE_RE.finditer(text))
    if matches:
        first_line = text[matches[-1].start():].strip().split("\n")[0]
        if first_line and first_line[-1] not in SENTENCE_END:
            return True
    return False


def truncation_ratio(chunks: list[Chunk]) -> float:
    """含结构标记的 chunk 中，被切断的比例。"""
    relevant = [chunk for chunk in chunks if CLAUSE_RE.search(chunk.text) or "|" in chunk.text]
    if not relevant:
        return 0.0
    broken = sum(1 for chunk in relevant if is_structural_truncation(chunk.text))
    return broken / len(relevant)


def manual_review_hints() -> tuple[str, ...]:
    """人工抽检 10 个样本时要看的三件事。"""
    return (
        "专有名词 SGCC-4012 / ERR_4012 是否完整落在同一块",
        "条款编号第 N 条是否被从中间切断",
        "表格行是否保留'故障码 → 处置建议'的完整对应",
        "标题前缀是否存在，脱离原文仍能判断所属章节",
    )


def build_results(document: Document) -> tuple[StrategyResult, ...]:
    """在同一份 Document 上跑四种策略。"""
    strategies: tuple[tuple[str, Callable[[Document], list[Chunk]]], ...] = (
        ("A 固定 512/64", lambda doc: fixed_size(doc, chunk_size=512, overlap=64)),
        ("B 递归 512/64", lambda doc: recursive(doc, chunk_size=512, overlap=64)),
        ("C 标题前缀", lambda doc: markdown_heading(doc, chunk_size=512)),
        (
            "D small-to-big",
            lambda doc: small_to_big(doc, small_size=96, big_size=512, overlap=16),
        ),
    )
    results: list[StrategyResult] = []
    for name, function in strategies:
        chunks = function(document)
        if not chunks:
            results.append(StrategyResult(name, 0, 0.0, 0.0))
            continue
        average = sum(estimate_tokens(chunk.text) for chunk in chunks) / len(chunks)
        samples = tuple(
            f"[{chunk.title_path or '无标题'}] {chunk.text[:48]}" for chunk in chunks[:2]
        )
        results.append(
            StrategyResult(
                name=name,
                count=len(chunks),
                avg_tokens=average,
                truncation_ratio=truncation_ratio(chunks),
                samples=samples,
                chunks=tuple(chunks),
            )
        )
    return tuple(results)


def format_results(results: tuple[StrategyResult, ...]) -> str:
    """把对比结果渲染成定宽表格文本。"""
    lines = ["策略                chunk数  平均token  结构截断率"]
    for result in results:
        lines.append(
            f"{result.name:<18} {result.count:>6} {result.avg_tokens:>10.1f} "
            f"{result.truncation_ratio:>10.0%}"
        )
    return "\n".join(lines)


__all__ = [
    "CLAUSE_RE",
    "StrategyResult",
    "build_results",
    "format_results",
    "is_structural_truncation",
    "manual_review_hints",
    "truncation_ratio",
]
