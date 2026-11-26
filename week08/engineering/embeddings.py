"""
第 8 周 · 工程层：确定性本地向量（教学替身）
================================================================
【对应知识点】文档第 8 周：Embedding 原理、归一化、维度选择

【周次学习要点】
  - HashEmbedding 用 SHA-256 把 token 哈希到固定维度槽位，带符号累加。
  - embed() 与 embed_query() 走完全相同的代码，杜绝"查询/文档用不同模型"。
  - normalize=True 时输出单位向量，cosine 与 dot 的排序才会一致。

【易忽略细节 / 对照文档补足】
  1. **这是教学替身，不是真实语义模型**：哈希向量只反映词面重合，不理解语义。
  2. 生产上 bge-m3 / qwen3-embedding / text-embedding-v3 必须文档与查询同模型同版本。
  3. 维度必须固定：换 dim 后旧向量与新向量不能混用，否则检索结果无意义。
  4. dim=16 便于打印观察，dim=1024 用来对齐生产 DDL 的 vector(1024)。

【示例用途】core_mechanisms 01~04、vector_lab 与测试共用
"""
from __future__ import annotations

import hashlib
import math
import re

_TOKEN_RE = re.compile(r"[\u4e00-\u9fff]|[a-z0-9_]+")


def tokenize(text: str) -> list[str]:
    """中文按字、英文按词切分；教学替身不做分词模型。"""
    return _TOKEN_RE.findall(text.lower())


def normalize_vector(vector: list[float] | tuple[float, ...]) -> list[float]:
    """L2 归一化；零向量原样返回，避免除零。"""
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0.0:
        return list(vector)
    return [value / norm for value in vector]


class HashEmbedding:
    """确定性哈希向量器：无网络、无 Key、可复现，仅用于教学与测试。"""

    def __init__(self, dim: int = 16, *, normalize: bool = True) -> None:
        if dim <= 0:
            raise ValueError("dim 必须为正整数")
        self.dim = dim
        self.normalize = normalize

    def _raw_vector(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        for token in tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dim
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        return vector

    def _finalize(self, vector: list[float]) -> list[float]:
        return normalize_vector(vector) if self.normalize else vector

    def embed(self, text: str) -> list[float]:
        """文档侧向量；与 embed_query 必须保持同一实现。"""
        return self._finalize(self._raw_vector(text))

    def embed_query(self, text: str) -> list[float]:
        """查询侧向量；故意与 embed 共用逻辑，避免模型不一致。"""
        return self._finalize(self._raw_vector(text))


__all__ = ["HashEmbedding", "normalize_vector", "tokenize"]
