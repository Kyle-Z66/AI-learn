"""
第 9 周 · 核心机制 03：稠密向量召回（复用第 8 周）
================================================================
【对应知识点】文档第 9 周：向量路召回；第 8 周嵌入与向量库

【周次学习要点】
  - 直接复用 week08.engineering.vector_store.HashEmbedding，本周不重写向量库。
  - 余弦相似度衡量语义方向；同义词可命中，但罕见型号/错误码是盲区。
  - 第 8 周的归一化、HNSW/IVF 不再展开，这里只把它作为"另一路召回"。

【易忽略细节】
  1. 哈希嵌入确定性：同一文本每次得到同一向量，适合教学与单测。
  2. query 和 doc 必须过同一个 embed 方法；换模型就要整库重建。
  3. 零向量相似度必须置 0，否则 NaN 会让后续融合排序失真。

【示例用途】可运行：`python -m week09.core_mechanisms.03_dense_retrieval`
             测试见 tests/week09/test_core_mechanisms.py
"""
from __future__ import annotations

from week09.engineering.dense_index import DenseIndex
from week09.engineering.models import Candidate

CORPUS: list[Candidate] = [
    Candidate("v1", "断路器巡检周期与温度阈值说明", "manual"),
    Candidate("v2", "SGCC-4012 型号隔离开关检修步骤", "manual"),
    Candidate("v3", "ERR_4012 错误码与通信链路超时排查", "error_codes"),
    Candidate("v4", "差旅报销与发票归档要求", "finance"),
]


def dense_top(query: str, top_k: int = 3) -> list[tuple[str, float]]:
    """向量路召回；查询与文档共用第 8 周确定性嵌入。"""
    return DenseIndex(CORPUS).search(query, top_k=top_k)


def demo() -> None:
    for query in ("断路器巡检注意事项", "SGCC-4012 怎么处理"):
        print(f"查询：{query}")
        results = dense_top(query)
        if not results:
            print("  （无正分候选）")
        for doc_id, score in results:
            text = next(doc.text for doc in CORPUS if doc.chunk_id == doc_id)
            print(f"  {doc_id}: cosine={score:.4f} :: {text}")
    print("专名 query 的向量结果并不精确命中型号 → 需要 BM25 补位")


if __name__ == "__main__":
    demo()
