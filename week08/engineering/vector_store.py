"""
第 8 周 · 工程层：内存向量库（暴力精确检索）
================================================================
【对应知识点】文档第 8 周：向量库 add / search / 标量过滤 / 持久化

【周次学习要点】
  - 暴力精确检索是 ANN 的正确性基线：HNSW / IVF 都要和它比召回率。
  - 标量过滤在向量打分之前执行，等价于 SQL 的 WHERE 先收窄候选集。
  - 三种度量统一成"分数越大越相关"：欧氏距离取负值返回。

【易忽略细节 / 对照文档补足】
  1. 未归一化向量用 cosine 是对的，用 dot 会被向量长度带偏（见 pitfalls）。
  2. valid_until_after 是字符串日期比较（ISO 格式字典序即时间序），教学够用。
  3. 持久化用 JSON 而不是 pickle：可读、可 diff、不执行反序列化代码。
  4. 这里没有 ANN：召回基准用"候选子集模拟近似"，第 9 周才做混合检索。

【示例用途】core_mechanisms 07~10、vector_lab 与测试共用
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path

from week08.engineering.models import EmbeddingRecord, SearchHit

VALID_METRICS = ("cosine", "dot", "euclidean")


def similarity(
    left: list[float] | tuple[float, ...],
    right: list[float] | tuple[float, ...],
    metric: str = "cosine",
) -> float:
    """返回相似度；统一为"越大越相关"，euclidean 返回负距离。"""
    if len(left) != len(right):
        raise ValueError("向量维度不一致，不能计算相似度")
    if metric not in VALID_METRICS:
        raise ValueError(f"未知度量：{metric}")
    if metric == "dot":
        return sum(a * b for a, b in zip(left, right, strict=True))
    if metric == "euclidean":
        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right, strict=True)))
        return -distance
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


class InMemoryVectorStore:
    """精确检索的内存向量库；生产可替换为 pgvector / Milvus。"""

    def __init__(self, dim: int, *, metric: str = "cosine") -> None:
        if dim <= 0:
            raise ValueError("dim 必须为正整数")
        if metric not in VALID_METRICS:
            raise ValueError(f"未知度量：{metric}")
        self.dim = dim
        self.metric = metric
        self._records: dict[str, EmbeddingRecord] = {}

    def add(self, record: EmbeddingRecord) -> None:
        """新增或覆盖一条记录；维度不符直接报错而不是静默截断。"""
        if len(record.vector) != self.dim:
            raise ValueError(
                f"向量维度 {len(record.vector)} 与库的 {self.dim} 不符，请重新嵌入"
            )
        self._records[record.id] = record

    def records(self) -> list[EmbeddingRecord]:
        """按 id 排序返回全部记录，便于稳定复现实验。"""
        return [self._records[key] for key in sorted(self._records)]

    def __len__(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        self._records.clear()

    @staticmethod
    def _matches(record: EmbeddingRecord, where: dict[str, str] | None) -> bool:
        if not where:
            return True
        for key, expected in where.items():
            if key == "valid_until_after":
                actual = record.metadata.get("valid_until", "")
                if not actual or actual <= expected:
                    return False
            elif record.metadata.get(key) != expected:
                return False
        return True

    def search(
        self,
        query: list[float] | tuple[float, ...],
        *,
        top_k: int = 5,
        where: dict[str, str] | None = None,
        metric: str | None = None,
    ) -> list[SearchHit]:
        """先做标量过滤，再暴力打分排序，返回 top_k 个命中。"""
        if len(query) != self.dim:
            raise ValueError("查询向量维度与库不一致")
        chosen = metric or self.metric
        candidates = [
            record for record in self._records.values() if self._matches(record, where)
        ]
        scored = [(record, similarity(query, record.vector, chosen)) for record in candidates]
        scored.sort(key=lambda item: (-item[1], item[0].id))
        return [SearchHit(record, score) for record, score in scored[:top_k]]


def save_store(store: InMemoryVectorStore, path: str | Path) -> None:
    """把向量库快照写成 JSON，便于重载与版本对比。"""
    payload = {
        "dim": store.dim,
        "metric": store.metric,
        "records": [asdict(record) for record in store.records()],
    }
    Path(path).write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def load_store(path: str | Path) -> InMemoryVectorStore:
    """从 JSON 重载向量库；重载后检索结果应与保存前一致。"""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    store = InMemoryVectorStore(int(payload["dim"]), metric=str(payload["metric"]))
    for item in payload["records"]:
        store.add(
            EmbeddingRecord(
                id=str(item["id"]),
                text=str(item["text"]),
                vector=tuple(float(value) for value in item["vector"]),
                metadata={str(key): str(value) for key, value in item["metadata"].items()},
            )
        )
    return store


__all__ = [
    "VALID_METRICS",
    "InMemoryVectorStore",
    "load_store",
    "save_store",
    "similarity",
]
