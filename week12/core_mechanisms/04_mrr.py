"""
第 12 周 · 核心机制 04：MRR@10
================================================================
【对应知识点】文档第 12 周：检索侧指标 MRR@10

【周次学习要点】
  - RR = 1 / 第一个命中的名次；MRR = 所有查询的 RR 均值。
  - 与 Recall 互补：Recall 看"找全没有"，MRR 看"排得靠不靠前"。
  - 未命中记 0；超过 k 的命中也不计分，体现 Top-K 的用户体验。

【易忽略细节】
  1. zip(strict=True) 让"检索列表与标注列表数量不一致"当场报错，
     避免 Java 里常见的"两个 List 长度不同却悄悄按短的遍历"。
  2. 同一查询的多个相关片段只取第一个命中位置，不能把多个 1/rank 累加。
  3. 排序同分时的兜底字段要稳定，否则 MRR 会因 tie-break 抖动。

【示例用途】可运行：`python -m week12.core_mechanisms.04_mrr`
             测试见 tests/week12/test_core_mechanisms.py
"""
from __future__ import annotations

from week12.engineering.metrics import mrr, reciprocal_rank

RANKINGS: tuple[list[str], ...] = (
    ["x", "a", "b"],
    ["a", "x", "b"],
    ["x", "y", "z"],
)
GOLD: tuple[list[str], ...] = (["a"], ["a"], ["a"])


def demo() -> None:
    for ranking, expected in zip(RANKINGS, GOLD, strict=True):
        print(f"{ranking} → RR={reciprocal_rank(ranking, expected):.3f}")
    print(f"MRR@10 = {mrr(RANKINGS, GOLD):.3f}")
    print("第一篇就命中得 1.0，第二篇 0.5，未命中 0；排名比找全更影响体验。")


if __name__ == "__main__":
    demo()
