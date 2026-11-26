"""
第 8 周 · 核心机制 02：cosine / dot / euclidean 的口径差异
================================================================
【对应知识点】文档第 8 周：相似度度量 cosine vs dot vs euclidean

【周次学习要点】
  - cosine 只看方向，dot 同时看方向与长度，euclidean 看绝对距离。
  - 归一化之后 cosine 与 dot 排序一致；未归一化时二者可能给出不同 Top-K。
  - 本工程把三者统一成"分数越大越相关"，euclidean 返回负距离。

【易忽略细节】
  1. pgvector 的 <=> 是余弦距离，相似度要写成 1 - distance。
  2. 未归一化向量用 dot，长文本会因为范数大而虚假领先。
  3. 零向量的 cosine 无定义，这里返回 0.0 而不是抛异常。

【示例用途】可运行：`python -m week08.core_mechanisms.02_similarity_metrics`
             测试见 tests/week08/test_core_mechanisms.py
"""
from __future__ import annotations

from week08.engineering.embeddings import HashEmbedding
from week08.engineering.vector_store import VALID_METRICS, similarity

QUERY = "ERR_4012 上游连接超时"
DOCUMENT = "ERR_4012 检查上游健康状态与连接池"


def metric_scores(query: str = QUERY, document: str = DOCUMENT) -> dict[str, float]:
    """返回同一对向量在三种度量下的分数。"""
    embedder = HashEmbedding(16)
    left = embedder.embed_query(query)
    right = embedder.embed(document)
    return {metric: similarity(left, right, metric) for metric in VALID_METRICS}


def demo() -> None:
    scores = metric_scores()
    for metric, score in scores.items():
        print(f"{metric:<10} 分数={score:+.4f}")
    print("向量已归一化，所以 cosine 与 dot 应当相等；euclidean 是负距离。")


if __name__ == "__main__":
    demo()
