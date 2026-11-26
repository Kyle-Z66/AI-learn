"""
第 9 周 · 核心机制 08：过滤必须在两路召回之前
================================================================
【对应知识点】文档第 8 周标量过滤 + 第 9 周融合：过滤时机

【周次学习要点】
  - 正确顺序：dept / valid 过滤 → 两路建索引 → 融合 → Top-K。
  - 先融合后过滤会"吃掉"Top-K 名额：被剔除文档占的位置不会自动补位。
  - 这与 Java 侧 SQL 的 WHERE 必须在 ORDER BY LIMIT 之前是同一个道理。

【易忽略细节】
  1. 失效文档若排名很高，后过滤会让返回条数小于 top_k，线上表现为"莫名少一条"。
  2. 权限过滤放融合后还可能通过分数反推被过滤文档的存在，属于信息泄漏。
  3. 过滤条件变化时索引要重建；缓存索引必须把过滤条件作为 key 的一部分。

【示例用途】可运行：`python -m week09.core_mechanisms.08_filter_and_fusion`
             测试见 tests/week09/test_core_mechanisms.py
"""
from __future__ import annotations

from week09.engineering.bm25_index import BM25Index
from week09.engineering.dense_index import DenseIndex
from week09.engineering.fusion import reciprocal_rank_fusion
from week09.engineering.models import Candidate

CORPUS: list[Candidate] = [
    Candidate("f-1", "SGCC-4012 巡检周期与温度阈值", "manual", dept="运维"),
    Candidate("f-2", "SGCC-4012 停用批次处理办法", "archive", dept="运维", valid=False),
    Candidate("f-3", "断路器通用巡检流程", "manual", dept="运维"),
    Candidate("f-4", "SGCC-4012 财务资产登记", "finance", dept="财务"),
]


def _fuse(pool: list[Candidate], query: str) -> list[str]:
    sparse = BM25Index(pool).score_map(query)
    dense = DenseIndex(pool).score_map(query)
    rankings = [
        [doc_id for doc_id, _ in sorted(sparse.items(), key=lambda item: -item[1])],
        [doc_id for doc_id, _ in sorted(dense.items(), key=lambda item: -item[1])],
    ]
    return reciprocal_rank_fusion(rankings, k=60)


def filter_then_fuse(query: str, top_k: int = 3) -> list[str]:
    """正确：先按 dept=运维 / valid=True 过滤，再融合。"""
    pool = [item for item in CORPUS if item.dept == "运维" and item.valid]
    return _fuse(pool, query)[:top_k]


def fuse_then_filter(query: str, top_k: int = 3) -> list[str]:
    """错误：先融合再过滤；失效文档占掉名额且不会被补位。"""
    fused = _fuse(CORPUS, query)[:top_k]
    by_id = {item.chunk_id: item for item in CORPUS}
    return [
        doc_id
        for doc_id in fused
        if by_id[doc_id].dept == "运维" and by_id[doc_id].valid
    ]


def demo() -> None:
    query = "SGCC-4012 巡检"
    good = filter_then_fuse(query)
    bad = fuse_then_filter(query)
    print(f"查询：{query}，Top-K=3")
    print(f"  先过滤再融合：{good}（{len(good)} 条，全部来自过滤后的池）")
    print(f"  先融合再过滤：{bad}（{len(bad)} 条，被剔除的排名没有补位）")
    print("把 WHERE 提到召回之前，是 ES / SQL 时代就有的常识，RAG 同样适用")


if __name__ == "__main__":
    demo()
