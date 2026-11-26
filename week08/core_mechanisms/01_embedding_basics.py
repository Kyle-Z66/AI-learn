"""
第 8 周 · 核心机制 01：文本如何变成向量
================================================================
【对应知识点】文档第 8 周：Embedding 原理、维度与归一化

【周次学习要点】
  - 文本 → token → 定长浮点数组；维度固定才能入库、才能相互比较。
  - 教学替身 HashEmbedding 可复现，真实模型要查"文档/查询同模型同版本"。
  - 归一化把向量长度归一，cosine 与 dot 的排序才能对齐。

【易忽略细节】
  1. 哈希向量只反映词面重合，不理解"超时"与"响应慢"的语义相近。
  2. dim=16 用来打印观察，dim=1024 对齐生产 DDL 的 vector(1024)。
  3. 零向量无法归一化，实现里要原样返回，不能除以 0。

【示例用途】可运行：`python -m week08.core_mechanisms.01_embedding_basics`
             测试见 tests/week08/test_core_mechanisms.py
"""
from __future__ import annotations

import math

from week08.engineering.embeddings import HashEmbedding, tokenize


def vector_profile(text: str, dim: int = 16) -> tuple[int, int, float]:
    """返回 (token 数, 向量维度, L2 范数)。"""
    vector = HashEmbedding(dim).embed(text)
    norm = math.sqrt(sum(value * value for value in vector))
    return len(tokenize(text)), len(vector), norm


def demo() -> None:
    text = "SGCC-4012 上游连接超时 ERR_4012"
    tokens, dim, norm = vector_profile(text)
    print(f"文本：{text}")
    print(f"token 数={tokens} 向量维度={dim} L2 范数={norm:.4f}")
    print("生产模型需保证 query/doc 使用同一模型与同一版本。")


if __name__ == "__main__":
    demo()
