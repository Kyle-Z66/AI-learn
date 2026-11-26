"""
第 8 周 · 核心机制 04：维度不匹配与暴力截断
================================================================
【对应知识点】文档第 8 周：维度选择与向量库列定义

【周次学习要点】
  - 向量列 vector(1024) 要求所有向量严格 1024 维，差一维都不行。
  - 直接切片截断会丢掉尾部信息，还可能改变向量范数，检索分数失真。
  - 正确做法是换同维度的模型或全量重嵌，而不是"补零/截断"凑数。

【易忽略细节】
  1. 补零看似能入库，但零维度不携带任何语义，等于悄悄降低模型质量。
  2. 不同模型即使维度相同，向量空间也不对齐，不能混用。
  3. InMemoryVectorStore.add() 会显式拒绝维度不符，避免静默错误。

【示例用途】可运行：`python -m week08.core_mechanisms.04_dimension_truncation`
             测试见 tests/week08/test_core_mechanisms.py
"""
from __future__ import annotations

from week08.engineering.embeddings import HashEmbedding
from week08.engineering.models import EmbeddingRecord
from week08.engineering.vector_store import InMemoryVectorStore


def truncated_norm(vector: list[float], dim: int) -> float:
    """暴力截断到 dim 维后的 L2 范数，用来量化信息损失。"""
    head = vector[:dim]
    return sum(value * value for value in head) ** 0.5


def demo() -> None:
    full = HashEmbedding(1024).embed("SGCC-4012 上游连接超时")
    print(f"原向量维度={len(full)} 范数={sum(v * v for v in full) ** 0.5:.4f}")
    print(f"截断到 16 维后范数={truncated_norm(full, 16):.4f}（信息丢失）")

    store = InMemoryVectorStore(16)
    try:
        store.add(EmbeddingRecord("bad", "维度不匹配", tuple(full)))
    except ValueError as error:
        print("入库被拒：", error)
    good = HashEmbedding(16).embed("SGCC-4012 上游连接超时")
    store.add(EmbeddingRecord("good", "同维度", tuple(good)))
    print(f"正确维度的记录已入库：{len(store)} 条")


if __name__ == "__main__":
    demo()
