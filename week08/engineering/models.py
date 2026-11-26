"""
第 8 周 · 工程层：向量检索的数据契约
================================================================
【对应知识点】文档第 8 周：向量库存入"向量 + 元数据"

【周次学习要点】
  - EmbeddingRecord 把向量与业务元数据绑在一起，标量过滤才有字段可用。
  - SearchHit 只多一个 score，排序与展示共用同一结构。
  - metadata 用 dict[str, str]：dept_id / valid_until 都能以字符串无损存储。

【易忽略细节 / 对照文档补足】
  1. 文档只写 embedding vector(1024)，没说元数据必须随向量一起存；分开存就无法做 RBAC。
  2. vector 用 tuple 而非 list，避免调用方意外改动已入库的向量。
  3. 这是教学替身模型，不引入任何真实 embedding API 或 Key。

【示例用途】被 embeddings.py / vector_store.py / vector_lab 引用；
             测试见 tests/week08/test_engineering.py
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EmbeddingRecord:
    """一条可检索记录：文本 + 向量 + 用于标量过滤的元数据。"""

    id: str
    text: str
    vector: tuple[float, ...]
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class SearchHit:
    """检索命中：记录本身 + 相似度分数（越大越相关）。"""

    record: EmbeddingRecord
    score: float


__all__ = ["EmbeddingRecord", "SearchHit"]
