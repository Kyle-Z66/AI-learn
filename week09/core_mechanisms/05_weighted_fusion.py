"""
第 9 周 · 核心机制 05：归一化后加权融合
================================================================
【对应知识点】文档第 9 周：加权分数融合（需先归一化两路分数）

【周次学习要点】
  - 两路分数先 min-max 压到 [0,1]，再按权重相加，否则 BM25 的几分会压倒 cosine。
  - 权重是可解释的业务旋钮：偏专名场景调高 BM25 权重，偏问答调高向量权重。
  - 只在一路出现的文档，另一路按 0 分计，而不是"缺失即满分"。

【易忽略细节】
  1. 归一化是在"本次召回结果集合"上做的，换一批候选分数分布就变。
  2. 全部分数相等时分母为 0 → 返回全 0，不能产生 NaN。
  3. 权重必须在 [0,1]，且两路权重和为 1；越界要报错而不是静默截断。

【示例用途】可运行：`python -m week09.core_mechanisms.05_weighted_fusion`
             测试见 tests/week09/test_core_mechanisms.py
"""
from __future__ import annotations

from week09.engineering.fusion import weighted_score_fusion

SPARSE_SCORES = {"c-01": 4.2, "c-02": 3.1, "c-03": 1.8}
DENSE_SCORES = {"c-01": 0.42, "c-02": 0.88, "c-03": 0.75}


def fuse(weight_sparse: float) -> list[str]:
    """教学入口：不同权重下观察排序翻转。"""
    return weighted_score_fusion(SPARSE_SCORES, DENSE_SCORES, weight_sparse)


def demo() -> None:
    print("原始分：BM25 量纲是几，cosine 量纲是零点几")
    print(f"  BM25: {SPARSE_SCORES}")
    print(f"  dense: {DENSE_SCORES}")
    for weight in (0.8, 0.5, 0.2):
        print(f"  BM25 权重={weight:.1f} → {fuse(weight)}")
    print("权重改变会翻转排序；RRF 不依赖这种手工调参，故更稳")


if __name__ == "__main__":
    demo()
