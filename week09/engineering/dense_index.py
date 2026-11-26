"""
第 9 周 · 工程层：稠密向量召回（复用第 8 周嵌入与向量库）
================================================================
【对应知识点】文档第 9 周：向量路召回；第 8 周嵌入与向量库

【周次学习要点】
  - 本周不重写向量库：直接复用 week08 的 HashEmbedding 与 InMemoryVectorStore。
  - 余弦打分沿用第 8 周 similarity，保证两度量口径与向量实验一致。
  - 第 8 周的归一化、HNSW/IVF 不再展开，这里只把它作为"另一路召回"。

【易忽略细节 / 对照文档补足】
  1. 哈希嵌入确定性：同一文本每次得到同一向量，适合教学与单测。
  2. query 走 embed_query、doc 走 embed；第 8 周刻意让两者共用实现防漂移。
  3. 零向量相似度必须置 0，否则 NaN 会让后续融合排序失真。

【示例用途】被 hybrid_retriever.py / core_mechanisms/01、03、09 引用；
             测试见 tests/week09/test_engineering.py
"""
from __future__ import annotations

from collections.abc import Sequence

from week08.engineering.embeddings import HashEmbedding
from week08.engineering.models import EmbeddingRecord
from week08.engineering.vector_store import InMemoryVectorStore, similarity

from week09.engineering.models import Candidate


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    """复用第 8 周余弦实现；维度不一致时返回 0 而非抛异常，便于融合兜底。"""
    if len(left) != len(right):
        return 0.0
    return similarity(list(left), list(right), "cosine")


class DenseIndex:
    """稠密路索引：嵌入与检索都复用第 8 周实现，不重写向量库。"""

    def __init__(
        self,
        candidates: list[Candidate],
        embedding: HashEmbedding | None = None,
    ) -> None:
        self._embedding = embedding if embedding is not None else HashEmbedding()
        self._store = InMemoryVectorStore(dim=self._embedding.dim, metric="cosine")
        for candidate in candidates:
            self._store.add(
                EmbeddingRecord(
                    id=candidate.chunk_id,
                    text=candidate.text,
                    vector=tuple(self._embedding.embed(candidate.text)),
                    metadata={
                        "source": candidate.source,
                        "dept": candidate.dept,
                        "valid": str(candidate.valid),
                        **candidate.metadata,
                    },
                )
            )

    def score_map(self, query: str) -> dict[str, float]:
        """返回 chunk_id → 余弦相似度，只保留正分。"""
        hits = self._store.search(
            self._embedding.embed_query(query),
            top_k=len(self._store),
        )
        return {hit.record.id: hit.score for hit in hits if hit.score > 0.0}

    def search(self, query: str, top_k: int = 10) -> list[tuple[str, float]]:
        """按相似度降序返回 (chunk_id, score)；同分按 id 排序保证确定性。"""
        items = sorted(
            self.score_map(query).items(),
            key=lambda item: (-item[1], item[0]),
        )
        return items[:top_k]


__all__ = ["DenseIndex", "cosine_similarity"]
