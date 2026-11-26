"""
第 9 周 · 本周特有坑：混合检索四个高频翻车点
================================================================
【对应知识点】文档第 9 周：融合 / 分词 / 过滤 / 专名召回

【周次学习要点】
  - 直接相加原始分：BM25 的量纲压倒 cosine，权重被数据悄悄决定。
  - 先去重后融合：同一文档在两路都命中本应加成，去重会丢掉这个信号。
  - tokenizer 不一致：建库用大粒度、查询用小粒度，专名永远召不回。
  - 过滤放在融合后：Top-K 名额被失效文档占掉，且不会自动补位。

【易忽略细节】
  1. 去重要放在"融合累加分数"之后；RRF 天然按 doc_id 累加双路贡献。
  2. ES 的 analyzer 变更必须重建索引；RAG 里同样要重建向量与 BM25 两路。
  3. 这些坑在单路系统里不显眼，混合后才集中爆发。

【示例用途】可运行：`python -m week09.pitfalls.hybrid_pitfalls`
             测试见 tests/week09/test_pitfalls.py
"""
from __future__ import annotations

import importlib
from typing import Any

from week09.engineering.fusion import min_max_normalize, reciprocal_rank_fusion

# 数字开头的模块名只能用 importlib 加载，与 week06 测试一致。
_filter_module: Any = importlib.import_module(
    "week09.core_mechanisms.08_filter_and_fusion"
)
filter_then_fuse = _filter_module.filter_then_fuse
fuse_then_filter = _filter_module.fuse_then_filter

RAW_SPARSE = {"c-01": 10.0, "c-02": 9.5, "c-03": 0.0}
RAW_DENSE = {"c-01": 0.5, "c-02": 0.8, "c-03": 0.32}


def raw_sum() -> dict[str, float]:
    """错误示范：直接相加，BM25 的绝对量级决定胜负。"""
    return {
        doc_id: RAW_SPARSE.get(doc_id, 0.0) + RAW_DENSE.get(doc_id, 0.0)
        for doc_id in set(RAW_SPARSE) | set(RAW_DENSE)
    }


def normalized_sum() -> dict[str, float]:
    """正确示范：各自归一化到 [0,1] 后再相加。"""
    sparse_norm = min_max_normalize(RAW_SPARSE)
    dense_norm = min_max_normalize(RAW_DENSE)
    return {
        doc_id: sparse_norm.get(doc_id, 0.0) + dense_norm.get(doc_id, 0.0)
        for doc_id in set(RAW_SPARSE) | set(RAW_DENSE)
    }


def demo_raw_score_addition() -> None:
    print("直接加原始分：", raw_sum(), "→ c-01 胜（只因为 BM25 数值大）")
    print("归一化后相加：", normalized_sum(), "→ c-02 胜（cosine 优势被看见）")


def demo_dedup_loses_score() -> None:
    rankings = [["c-01", "c-02"], ["c-01", "c-03"]]
    fused = reciprocal_rank_fusion(rankings, k=60)
    dedup_first = ["c-01", "c-02", "c-03"]
    print(f"正确（先融合累加双路贡献）：{fused}")
    print(f"错误（先去重只留单路顺序）：{dedup_first}")
    print("c-01 两路都命中，RRF 得分翻倍；提前去重会丢掉这个强信号")


def demo_tokenizer_mismatch() -> None:
    indexed = ["sgcc-4012", "断路器", "巡检"]
    queried = ["sgcc", "4012", "断路", "路器", "巡检"]
    overlap = set(indexed) & set(queried)
    print(f"建库 token：{indexed}")
    print(f"查询 token：{queried}")
    print(f"交集：{sorted(overlap)} → 专名 sgcc-4012 完全失配")
    print("修复：两边都调用 week09.engineering.bm25_index.tokenize")


def demo_filter_after_fusion() -> None:
    query = "SGCC-4012 巡检"
    good = filter_then_fuse(query)
    bad = fuse_then_filter(query)
    print(f"先过滤再融合：{good}（{len(good)} 条）")
    print(f"先融合再过滤：{bad}（{len(bad)} 条，名额未补位）")


def demo() -> None:
    demo_raw_score_addition()
    demo_dedup_loses_score()
    demo_tokenizer_mismatch()
    demo_filter_after_fusion()


if __name__ == "__main__":
    demo()
