"""
第 9 周 · 核心机制 06：为什么不能直接相加 BM25 与 cosine
================================================================
【对应知识点】文档第 9 周验收：解释两路分数量纲不同不可直接相加

【周次学习要点】
  - BM25 无上界、受文档长度与 IDF 影响；cosine 固定在 [-1,1]（此处只取正分）。
  - 直接相加等于把 BM25 当成"重要得多"的一路，权重被量纲悄悄决定。
  - min-max 归一化后两路都在 [0,1]，这时权重才真正表达业务意图。

【易忽略细节】
  1. 归一化基于当前候选集的最大/最小；新增一篇文档就可能改变所有分数。
  2. 全相等分数归一化后全为 0，此时加权融合没有区分度 → 应回退看排名。
  3. 这是"需要调参"的融合方式，稳定性不如只用排名的 RRF。

【示例用途】可运行：`python -m week09.core_mechanisms.06_normalization_trap`
             测试见 tests/week09/test_core_mechanisms.py
"""
from __future__ import annotations

from collections.abc import Mapping

from week09.engineering.fusion import min_max_normalize

SPARSE = {"c-01": 3.2, "c-02": 2.9, "c-03": 0.8}
DENSE = {"c-01": 0.78, "c-02": 0.61, "c-03": 0.95}


def raw_sum(sparse: Mapping[str, float], dense: Mapping[str, float]) -> dict[str, float]:
    """错误示范：直接加原始分，BM25 数量级彻底压过 cosine。"""
    return {
        doc_id: sparse.get(doc_id, 0.0) + dense.get(doc_id, 0.0)
        for doc_id in set(sparse) | set(dense)
    }


def normalized_sum(
    sparse: Mapping[str, float],
    dense: Mapping[str, float],
) -> dict[str, float]:
    """正确示范：各自归一化到 [0,1] 后再相加。"""
    sparse_norm = min_max_normalize(sparse)
    dense_norm = min_max_normalize(dense)
    return {
        doc_id: sparse_norm.get(doc_id, 0.0) + dense_norm.get(doc_id, 0.0)
        for doc_id in set(sparse) | set(dense)
    }


def demo() -> None:
    bad = raw_sum(SPARSE, DENSE)
    good = normalized_sum(SPARSE, DENSE)
    print("直接相加（错）：", {k: round(v, 4) for k, v in sorted(bad.items())})
    print("归一化后相加（对）：", {k: round(v, 4) for k, v in sorted(good.items())})
    print("直接相加时 c-01 靠 BM25 绝对值胜出；归一化后 c-03 的 cosine 优势才显现")
    print("结论：要么先归一化再加权，要么直接用只看排名的 RRF")


if __name__ == "__main__":
    demo()
