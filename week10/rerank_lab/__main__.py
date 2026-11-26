"""
第 10 周 · 动手项目入口：Top-50 候选 → Top-5 三方对比
================================================================
【对应知识点】文档第 10 周验收：纯向量 vs 混合 vs 混合+rerank

【周次学习要点】
  - 候选预算 50（教学语料 15 条，实际取 min(50, 15)），Top-5 输出。
  - 三路共用过滤条件、查询与 K；指标为 Recall@5 与 MRR@5。
  - 精排只在混合召回的候选内重排，不会补回漏掉的文档。

【易忽略细节】
  1. 打分用确定性教学 reranker，无模型下载、无网络、可复现。
  2. 延迟不参与本次指标；候选预算的数量级另见 core_mechanisms/08。
  3. REPORT.md 只粘贴本程序真实输出，不手写业务结论。

【示例用途】可运行：`python -m week10.rerank_lab`
             测试见 tests/week10/test_rerank_lab.py
"""
from __future__ import annotations

from dataclasses import dataclass

from week09.engineering.dense_index import DenseIndex
from week09.engineering.hybrid_retriever import HybridRetriever
from week09.engineering.models import Candidate

from week10.engineering.reranker import DeterministicReranker
from week10.rerank_lab.corpus import QUERIES, LabQuery, build_corpus

CANDIDATE_BUDGET = 50
TOP_K = 5


@dataclass(frozen=True)
class LabRow:
    """一条查询的三方对比记录。"""

    query_id: str
    relevant: str
    dense_top: tuple[str, ...]
    hybrid_top: tuple[str, ...]
    rerank_top: tuple[str, ...]
    recall: dict[str, float]
    mrr: dict[str, float]


def recall_at_k(retrieved: list[str], relevant: str, k: int) -> float:
    """Recall@K：相关文档是否进入前 K。"""
    return 1.0 if relevant in set(retrieved[:k]) else 0.0


def mrr_at_k(retrieved: list[str], relevant: str, k: int) -> float:
    """MRR@K：第一个命中位置的倒数，未命中为 0。"""
    for rank, doc_id in enumerate(retrieved[:k], start=1):
        if doc_id == relevant:
            return 1.0 / rank
    return 0.0


def _pool(corpus: list[Candidate], case: LabQuery) -> list[Candidate]:
    """按部门 / 有效期过滤，三路方法共用。"""
    return [
        item
        for item in corpus
        if (not case.valid_only or item.valid)
        and (case.dept is None or item.dept == case.dept)
    ]


def run_experiment(
    candidate_budget: int = CANDIDATE_BUDGET,
    top_k: int = TOP_K,
) -> list[LabRow]:
    """对每条查询跑三路，返回逐条对比。"""
    corpus = build_corpus()
    retriever = HybridRetriever(corpus)
    reranker = DeterministicReranker()
    rows: list[LabRow] = []
    for case in QUERIES:
        pool = _pool(corpus, case)
        dense_ids = [
            doc_id for doc_id, _ in DenseIndex(pool).search(case.text, top_k)
        ]
        hybrid_items = retriever.retrieve(
            case.text,
            top_k=min(candidate_budget, len(pool)),
            dept=case.dept,
            valid_only=case.valid_only,
        )
        hybrid_ids = [item.chunk_id for item in hybrid_items[:top_k]]
        pairs = [
            (
                item.chunk_id,
                reranker.score(case.text, item.text),
            )
            for item in hybrid_items
        ]
        ordered = sorted(pairs, key=lambda pair: (-pair[1], pair[0]))
        rerank_ids = [doc_id for doc_id, _ in ordered[:top_k]]
        rankings = {
            "dense": dense_ids,
            "hybrid": hybrid_ids,
            "rerank": rerank_ids,
        }
        rows.append(
            LabRow(
                query_id=case.query_id,
                relevant=case.relevant,
                dense_top=tuple(dense_ids),
                hybrid_top=tuple(hybrid_ids),
                rerank_top=tuple(rerank_ids),
                recall={
                    name: recall_at_k(ranking, case.relevant, top_k)
                    for name, ranking in rankings.items()
                },
                mrr={
                    name: mrr_at_k(ranking, case.relevant, top_k)
                    for name, ranking in rankings.items()
                },
            )
        )
    return rows


def demo() -> None:
    rows = run_experiment()
    print(
        f"第 10 周 rerank 实验：候选预算 {CANDIDATE_BUDGET}，输出 Top-{TOP_K}，"
        f"{len(rows)} 条查询"
    )
    print("-" * 94)
    print(
        f"{'编号':<6}{'相关':<7}{'纯向量':>8}{'混合':>8}{'混合+rerank':>12}"
        "  纯向量 Top-5 → 混合 Top-5 → 精排 Top-5"
    )
    print("-" * 94)
    for row in rows:
        print(
            f"{row.query_id:<6}{row.relevant:<7}"
            f"{row.recall['dense']:>8.2f}{row.recall['hybrid']:>8.2f}"
            f"{row.recall['rerank']:>12.2f}  "
            f"{','.join(row.dense_top)} → {','.join(row.hybrid_top)} → "
            f"{','.join(row.rerank_top)}"
        )
    print("-" * 94)
    for metric in ("recall", "mrr"):
        print(
            f"{metric.upper()}@{TOP_K} 均值："
            + "  ".join(
                f"{name}={sum(getattr(row, metric)[name] for row in rows) / len(rows):.3f}"
                for name in ("dense", "hybrid", "rerank")
            )
        )
    print("rerank 只重排已召回候选；MRR 的变化体现它把相关文档提前的能力")


if __name__ == "__main__":
    demo()
