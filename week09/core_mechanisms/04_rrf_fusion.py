"""
第 9 周 · 核心机制 04：RRF 倒数排名融合
================================================================
【对应知识点】文档第 9 周：RRF score = Σ 1/(k + rank_i)，k=60

【周次学习要点】
  - RRF 只用排名不用分数：两路量纲不同也能直接融合，默认选它。
  - k=60 压低头部差距：第一名与第二名的贡献差很小，结果更稳。
  - 同时出现在两路的文档得分相加，天然实现"交叉验证"加成。

【易忽略细节】
  1. rank 从 1 开始；从 0 开始会让第一名权重异常放大。
  2. 文档只在一路出现也能得分，不要因为"另一路没有"就丢弃。
  3. 同分必须按 chunk_id 兜底排序，否则不同 Python 版本结果会漂移。

【示例用途】可运行：`python -m week09.core_mechanisms.04_rrf_fusion`
             测试见 tests/week09/test_core_mechanisms.py
"""
from __future__ import annotations

from week09.engineering.fusion import reciprocal_rank_fusion

# 模拟两路召回：BM25 把专名排第一，向量路更偏语义近邻。
SPARSE_RANKING = ["c-01", "c-03", "c-02", "c-04"]
DENSE_RANKING = ["c-02", "c-01", "c-04", "c-03"]


def merge(rankings: list[list[str]], k: int = 60) -> list[str]:
    """教学入口：把多路排名融成单一序列。"""
    return reciprocal_rank_fusion(rankings, k=k)


def demo() -> None:
    rankings = [SPARSE_RANKING, DENSE_RANKING]
    for k in (60, 5):
        fused = merge(rankings, k=k)
        print(f"k={k} 融合顺序：{fused}")
        print(f"  前两名：{fused[:2]}（k 越大越不偏袒单路第一名）")
    print("无需归一化、无需知道 BM25/cosine 的数值范围 → RRF 是稳的默认选择")


if __name__ == "__main__":
    demo()
