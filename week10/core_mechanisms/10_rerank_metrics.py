"""
第 10 周 · 核心机制 10：rerank 前后的 Recall@K 与 MRR 变化
================================================================
【对应知识点】文档第 10 周：跑对比实验记录 Recall@5 / MRR

【周次学习要点】
  - Recall@K 看"相关文档有没有进前 K"；MRR 看"第一个相关文档排在第几位"。
  - 首阶段与精排阶段必须共用同一批 query 与 K，指标才可对比。
  - 本周只做这两个轻量指标；系统化评测留到第 12 周。

【易忽略细节】
  1. MRR 用 1/rank，排名 1 得 1，排名 2 得 0.5；没命中得 0。
  2. rerank 不改候选集合时 Recall@K 常常不变，变化主要体现在 MRR。
  3. 小样本指标波动大，只用来验证链路，不要写成产品效果承诺。

【示例用途】可运行：`python -m week10.core_mechanisms.10_rerank_metrics`
             测试见 tests/week10/test_core_mechanisms.py
"""
from __future__ import annotations

from collections.abc import Sequence

CASES: list[tuple[str, list[str], list[str], str]] = [
    ("SGCC-4012 巡检", ["d1", "d2", "d3"], ["d3", "d2", "d1"], "d3"),
    ("ERR_4012 错误码", ["d1", "d4", "d5"], ["d4", "d1", "d5"], "d4"),
    ("断路器通用流程", ["d2", "d1", "d5"], ["d1", "d2", "d5"], "d1"),
]


def recall_at_k(retrieved: Sequence[str], relevant: str, k: int) -> float:
    """单条查询的 Recall@K；相关文档只有一个，命中即 1.0。"""
    return 1.0 if relevant in set(retrieved[:k]) else 0.0


def mrr_at_k(retrieved: Sequence[str], relevant: str, k: int) -> float:
    """单条查询的倒数排名：第一个命中位置的倒数，未命中为 0。"""
    for rank, doc_id in enumerate(retrieved[:k], start=1):
        if doc_id == relevant:
            return 1.0 / rank
    return 0.0


def before_after(k: int = 3) -> dict[str, dict[str, float]]:
    """比较首阶段顺序与精排顺序的平均 Recall@K / MRR@K。"""
    result = {
        "before": {"recall": 0.0, "mrr": 0.0},
        "after": {"recall": 0.0, "mrr": 0.0},
    }
    for _, stage, reranked, relevant in CASES:
        for label, ranking in (("before", stage), ("after", reranked)):
            result[label]["recall"] += recall_at_k(ranking, relevant, k)
            result[label]["mrr"] += mrr_at_k(ranking, relevant, k)
    count = len(CASES)
    for label in result:
        for metric in result[label]:
            result[label][metric] /= count
    return result


def demo() -> None:
    metrics = before_after()
    print(f"rerank 前后对比：{len(CASES)} 条查询，K=3")
    for label in ("before", "after"):
        print(
            f"  {label:<7} Recall@3={metrics[label]['recall']:.3f} "
            f"MRR@3={metrics[label]['mrr']:.3f}"
        )
    print("候选集合不变时 Recall 持平，MRR 提升说明相关文档被排得更靠前")


if __name__ == "__main__":
    demo()
