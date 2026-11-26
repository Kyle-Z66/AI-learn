"""
第 8 周 · 本周特有坑：向量化阶段最容易悄悄出错的地方
================================================================
【对应知识点】文档第 8 周：归一化、模型选型、维度、标量过滤

【周次学习要点】
  - 未归一化误用 dot：长文本因范数大虚假领先，cosine 不受长度影响。
  - query/doc 用不同模型或不同版本：向量空间不对齐，分数再高也无意义。
  - 维度不匹配与过期文档未过滤，是上线后最难排查的两类静默错误。

【易忽略细节】
  1. 归一化要做在入库和查询两侧，只做一侧等于没做。
  2. 换模型必须全量重嵌，且旧索引要下线，不能同库混存。
  3. 过期文档不删也不过滤，会持续污染 Top-K，尤其在政策/手册类知识库。

【示例用途】可运行：`python -m week08.pitfalls.embedding_pitfalls`
             测试见 tests/week08/test_pitfalls.py
"""
from __future__ import annotations

from week08.engineering.embeddings import HashEmbedding, normalize_vector
from week08.engineering.models import EmbeddingRecord
from week08.engineering.vector_store import InMemoryVectorStore, similarity

BASE = [1.0, 2.0, 3.0, 4.0]


def scale_effect(vector: list[float], factor: float) -> tuple[float, float]:
    """返回放大 factor 后 (dot, cosine) 分数的变化。"""
    scaled = [value * factor for value in vector]
    return (
        similarity(BASE, scaled, "dot"),
        similarity(BASE, scaled, "cosine"),
    )


def mismatch_error() -> str:
    """演示查询/文档维度不一致时的报错文本。"""
    store = InMemoryVectorStore(16)
    document = HashEmbedding(16).embed("文档文本")
    store.add(EmbeddingRecord("c1", "文档文本", tuple(document)))
    wrong_query = HashEmbedding(1024).embed_query("查询文本")
    try:
        store.search(wrong_query)
    except ValueError as error:
        return str(error)
    return ""


def expired_ids(where: dict[str, str]) -> list[str]:
    """构造含过期记录的库，返回过滤后的命中 id。"""
    store = InMemoryVectorStore(16)
    embedder = HashEmbedding(16)
    entries = (
        ("c1", "现行流程", "2030-12-31"),
        ("c2", "过期流程", "2025-01-01"),
    )
    for doc_id, text, valid_until in entries:
        store.add(
            EmbeddingRecord(
                doc_id,
                text,
                tuple(embedder.embed(text)),
                {"valid_until": valid_until},
            )
        )
    hits = store.search(tuple(embedder.embed_query("流程")), top_k=2, where=where)
    return [hit.record.id for hit in hits]


def demo_unnormalized_dot() -> None:
    base_dot, base_cosine = scale_effect(BASE, 1.0)
    big_dot, big_cosine = scale_effect(BASE, 10.0)
    print(f"放大 10 倍：dot {base_dot:.1f} → {big_dot:.1f}，"
          f"cosine {base_cosine:.4f} → {big_cosine:.4f}")
    print("cosine 不受向量长度影响，dot 会；未归一化时别用 dot 排序。")


def demo_model_mismatch() -> None:
    print("查询/文档维度不一致：", mismatch_error())
    print("即使维度相同，换模型也要全量重嵌，因为向量空间已改变。")


def demo_dimension_mismatch() -> None:
    store = InMemoryVectorStore(16)
    vector = HashEmbedding(1024).embed("文本")
    try:
        store.add(EmbeddingRecord("bad", "文本", tuple(vector)))
    except ValueError as error:
        print("入库被拒：", error)


def demo_expired_documents() -> None:
    unfiltered = expired_ids({})
    filtered = expired_ids({"valid_until_after": "2026-01-01"})
    print(f"不过滤：{unfiltered}；过滤后：{filtered}")
    print("过期文档不进候选集，比检索完再人工剔除可靠得多。")


def demo() -> None:
    demo_unnormalized_dot()
    demo_model_mismatch()
    demo_dimension_mismatch()
    demo_expired_documents()
    print("归一化后的单位向量：", [round(value, 3) for value in normalize_vector(BASE)])


if __name__ == "__main__":
    demo()
