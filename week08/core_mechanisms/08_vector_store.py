"""
第 8 周 · 核心机制 08：向量库 add / search 全流程
================================================================
【对应知识点】文档第 8 周：向量库部署与检索

【周次学习要点】
  - add 校验维度，search 先 where 过滤再按度量排序取 Top-K。
  - 同一批向量换度量会改变排序，但召回集合质量取决于向量本身。
  - 暴力精确检索用于给 ANN 当基准，教学库刻意不做近似。

【易忽略细节】
  1. Top-K 只是"候选"，第 9 周混合检索与重排会再筛选一次。
  2. score 不是概率，不同度量的分数不能直接横向比较。
  3. 同 id 重复 add 是覆盖语义，适合重嵌后更新。

【示例用途】可运行：`python -m week08.core_mechanisms.08_vector_store`
             测试见 tests/week08/test_core_mechanisms.py
"""
from __future__ import annotations

from week08.engineering.embeddings import HashEmbedding
from week08.engineering.models import EmbeddingRecord
from week08.engineering.vector_store import InMemoryVectorStore

TEXTS: tuple[str, ...] = (
    "SGCC-4012 上游连接超时",
    "ERR_4012 检查上游健康状态",
    "cyclone 级别 2 响应时限 30 分钟",
    "回滚脚本与发布检查清单",
)


def build_store() -> InMemoryVectorStore:
    """构造四维演示库，每条记录的 dept_id 不同。"""
    embedder = HashEmbedding(16)
    store = InMemoryVectorStore(16)
    for index, text in enumerate(TEXTS, start=1):
        store.add(
            EmbeddingRecord(
                f"c{index:03d}",
                text,
                tuple(embedder.embed(text)),
                {"dept_id": "ops" if index % 2 else "dev", "valid_until": "2030-12-31"},
            )
        )
    return store


def search_ids(metric: str = "cosine") -> list[str]:
    """返回指定度量下的 Top-3 命中 id。"""
    query = tuple(HashEmbedding(16).embed_query("ERR_4012 上游超时"))
    return [hit.record.id for hit in build_store().search(query, top_k=3, metric=metric)]


def demo() -> None:
    store = build_store()
    print(f"库中记录数={len(store)}")
    for metric in ("cosine", "dot", "euclidean"):
        print(f"{metric:<10} Top-3：{search_ids(metric)}")
    print("覆盖语义：", end=" ")
    embedder = HashEmbedding(16)
    store.add(EmbeddingRecord("c001", "更新后的文本", tuple(embedder.embed("更新后的文本"))))
    print(len(store))


if __name__ == "__main__":
    demo()
