"""
第 12 周 · 核心机制 03：Recall@k
================================================================
【对应知识点】文档第 12 周：检索侧指标 Recall@k

【周次学习要点】
  - Recall@k = Top-K 命中的标注片段数 / 标注片段总数，分母不是 k。
  - k 越大召回越高但成本越高；报告固定 k=5，便于四配置横向比较。
  - 多条相关片段时支持部分命中，不像 MRR 只看第一个。

【易忽略细节】
  1. 若标注列表为空，返回 0 而不是除零异常：真实标注缺失应当被门禁发现，
     而不是在指标计算处崩掉。
  2. 检索列表可能有重复 ID，用集合求交避免重复命中虚高分。
  3. Java 常用 BigDecimal 控制精度；这里保留 float 原始值，
     只在报告渲染时统一格式化，避免中间多次四舍五入。

【示例用途】可运行：`python -m week12.core_mechanisms.03_recall_at_k`
             测试见 tests/week12/test_core_mechanisms.py
"""
from __future__ import annotations

from week12.engineering.metrics import recall_at_k

QUERY_CASES: tuple[tuple[list[str], list[str]], ...] = (
    (["a", "b", "c", "d", "e"], ["a", "c"]),
    (["x", "y"], ["a", "c"]),
    (["a", "a", "b"], ["a", "b"]),
)


def demo() -> None:
    for k in (1, 3, 5):
        scores = [recall_at_k(found, expected, k) for found, expected in QUERY_CASES]
        print(f"k={k}: {[round(score, 3) for score in scores]}")
    print("分母始终是标注片段数；Top-K 只决定分子能取到哪些结果。")


if __name__ == "__main__":
    demo()
