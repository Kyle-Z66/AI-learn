"""
第 10 周 · 核心机制 07：从 50 条候选中选出 Top-5
================================================================
【对应知识点】文档第 10 周：Top-50 → Top-5

【周次学习要点】
  - 精排只改顺序、不增候选：Top-5 一定来自首阶段 Top-50。
  - 打分与候选必须按下标对齐；用 zip(strict=True) 能在长度不一致时立刻报错。
  - 同分按 chunk_id 兜底，保证不同运行下顺序一致。

【易忽略细节】
  1. 别把 rerank 分数当成召回分再过滤一遍；候选集合在精排阶段不应改变。
  2. top_k 大于候选数时返回全部候选，不要抛异常拖垮请求。
  3. 首阶段顺序要留作降级备份，不能就地覆盖原列表。

【示例用途】可运行：`python -m week10.core_mechanisms.07_topk_selection`
             测试见 tests/week10/test_core_mechanisms.py
"""
from __future__ import annotations

from collections.abc import Sequence

from week10.engineering.models import RerankCandidate

CANDIDATES: list[RerankCandidate] = [
    RerankCandidate("d1", "断路器通用巡检流程", 0.95),
    RerankCandidate("d2", "SGCC-4012 型号说明书", 0.91),
    RerankCandidate("d3", "SGCC-4012 断路器巡检周期", 0.88),
    RerankCandidate("d4", "ERR_4012 错误码排查", 0.80),
]
SCORES = [0.45, 0.48, 0.99, 0.70]


def select_top_k(
    candidates: Sequence[RerankCandidate],
    scores: Sequence[float],
    k: int,
) -> list[RerankCandidate]:
    """按精排分降序取前 k 条；长度不一致直接报错。"""
    pairs = list(zip(candidates, scores, strict=True))
    ordered = sorted(pairs, key=lambda item: (-item[1], item[0].chunk_id))
    return [candidate for candidate, _ in ordered[:k]]


def demo() -> None:
    print(f"首阶段顺序：{[c.chunk_id for c in CANDIDATES]}")
    print(f"精排分数：{SCORES}")
    for candidate in select_top_k(CANDIDATES, SCORES, k=3):
        print(f"  → {candidate.chunk_id} :: {candidate.text}")
    print("d3 从首阶段第 3 升到第 1；候选集合不变，只是顺序被重排")


if __name__ == "__main__":
    demo()
