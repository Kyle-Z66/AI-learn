"""
第 9 周 · 动手项目入口：纯向量 vs 混合检索召回对比
================================================================
【对应知识点】文档第 9 周验收：专名查询下两种方式的召回差异

【周次学习要点】
  - 同一批查询、同一个 K、同一套前置过滤，只换检索方式。
  - 输出逐条 Recall@K 与分组均值，能看出混合在专名上的增益。
  - 结果由本文件真实计算，REPORT.md 只粘贴运行输出。

【易忽略细节】
  1. 候选池按用例过滤后再建索引；两路方法必须一眼看出条件一致。
  2. 带过期文档的查询显式 valid_only=False，否则相关文档被前置过滤掉。
  3. 不做 rerank（第 10 周）、不做完整评测体系（第 12 周），边界守住。

【示例用途】可运行：`python -m week09.hybrid_lab`
             测试见 tests/week09/test_hybrid_lab.py
"""
from __future__ import annotations

from dataclasses import dataclass

from week09.engineering.dense_index import DenseIndex
from week09.engineering.hybrid_retriever import HybridRetriever
from week09.engineering.models import Candidate
from week09.hybrid_lab.corpus import build_corpus
from week09.hybrid_lab.queries import QUERIES, QueryCase

# 教学语料较小，用 Recall@1 放大两路的差异；K 越大差异越容易被抹平。
TOP_K = 1


@dataclass(frozen=True)
class ExperimentRow:
    """一条对比记录：同查询下两路分别的命中数与召回率。"""

    query_id: str
    group: str
    text: str
    dense_top: tuple[str, ...]
    hybrid_top: tuple[str, ...]
    dense_recall: float
    hybrid_recall: float


def recall(retrieved: list[str], relevant: frozenset[str], k: int) -> float:
    """单条查询 Recall@K；相关集合为空时记 0。"""
    if not relevant:
        return 0.0
    return len(set(retrieved[:k]) & set(relevant)) / len(relevant)


def _filtered_pool(corpus: list[Candidate], case: QueryCase) -> list[Candidate]:
    """按用例的 dept / valid 条件过滤，两路方法共用。"""
    return [
        item
        for item in corpus
        if (not case.valid_only or item.valid)
        and (case.dept is None or item.dept == case.dept)
    ]


def run_experiment(k: int = TOP_K) -> list[ExperimentRow]:
    """对每条查询分别跑纯向量与混合检索，返回逐条对比。"""
    corpus = build_corpus()
    retriever = HybridRetriever(corpus)
    rows: list[ExperimentRow] = []
    for case in QUERIES:
        pool = _filtered_pool(corpus, case)
        dense_ids = [doc_id for doc_id, _ in DenseIndex(pool).search(case.text, k)]
        hybrid_ids = [
            item.chunk_id
            for item in retriever.retrieve(
                case.text,
                top_k=k,
                dept=case.dept,
                valid_only=case.valid_only,
            )
        ]
        rows.append(
            ExperimentRow(
                query_id=case.query_id,
                group=case.group,
                text=case.text,
                dense_top=tuple(dense_ids),
                hybrid_top=tuple(hybrid_ids),
                dense_recall=recall(dense_ids, case.relevant, k),
                hybrid_recall=recall(hybrid_ids, case.relevant, k),
            )
        )
    return rows


def demo() -> None:
    rows = run_experiment()
    print(
        f"第 9 周混合检索实验：{len(rows)} 条查询，Recall@{TOP_K}（放大差异），RRF k=60"
    )
    print("-" * 92)
    print(f"{'编号':<6}{'组':<6}{'查询':<22}{'纯向量':>8}{'混合':>8}  纯向量 Top-1 → 混合 Top-1")
    print("-" * 92)
    for row in rows:
        print(
            f"{row.query_id:<6}{row.group:<6}{row.text:<22}"
            f"{row.dense_recall:>8.2f}{row.hybrid_recall:>8.2f}  "
            f"{','.join(row.dense_top)} → {','.join(row.hybrid_top)}"
        )
    print("-" * 92)
    for group in ("普通", "专名", "过滤"):
        selected = [row for row in rows if row.group == group]
        dense_avg = sum(row.dense_recall for row in selected) / len(selected)
        hybrid_avg = sum(row.hybrid_recall for row in selected) / len(selected)
        print(f"{group}组均值：纯向量={dense_avg:.3f}  混合={hybrid_avg:.3f}")
    all_dense = sum(row.dense_recall for row in rows) / len(rows)
    all_hybrid = sum(row.hybrid_recall for row in rows) / len(rows)
    print(f"总体均值：纯向量={all_dense:.3f}  混合={all_hybrid:.3f}")


if __name__ == "__main__":
    demo()
