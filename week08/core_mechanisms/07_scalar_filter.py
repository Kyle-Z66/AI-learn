"""
第 8 周 · 核心机制 07：标量过滤先于向量检索
================================================================
【对应知识点】文档第 8 周：按权限/时间过滤后再向量检索

【周次学习要点】
  - where 支持 metadata 等值过滤和 valid_until_after 日期比较。
  - 过滤在打分前执行：过期或越权文档根本不进入候选集。
  - 这与 SQL 的 WHERE + ORDER BY embedding <=> 是同一套思维。

【易忽略细节】
  1. 先取 Top-K 再过滤会漏结果：Top-K 里可能全是无权访问的文档。
  2. 日期用 ISO 字符串，字典序即时间序，教学替身无需日期类型。
  3. 生产库要把过滤字段建进索引，否则过滤阶段仍是全表扫。

【示例用途】可运行：`python -m week08.core_mechanisms.07_scalar_filter`
             测试见 tests/week08/test_core_mechanisms.py
"""
from __future__ import annotations

from week08.engineering.embeddings import HashEmbedding
from week08.engineering.models import EmbeddingRecord
from week08.engineering.vector_store import InMemoryVectorStore

TODAY = "2026-11-26"
ITEMS: tuple[tuple[str, str, str, str], ...] = (
    ("c1", "SGCC-4012 上游超时处置", "ops", "2030-12-31"),
    ("c2", "ERR_4012 旧版处置流程", "ops", "2025-06-30"),
    ("c3", "SGCC-4012 权限配置", "dev", "2030-12-31"),
)


def filtered_search(
    query: str,
    *,
    dept_id: str = "ops",
    top_k: int = 10,
) -> list[str]:
    """构造演示库并返回过滤后的命中 id。"""
    embedder = HashEmbedding(16)
    store = InMemoryVectorStore(16)
    for doc_id, text, dept, valid_until in ITEMS:
        store.add(
            EmbeddingRecord(
                doc_id,
                text,
                tuple(embedder.embed(text)),
                {"dept_id": dept, "valid_until": valid_until},
            )
        )
    hits = store.search(
        tuple(embedder.embed_query(query)),
        top_k=top_k,
        where={"dept_id": dept_id, "valid_until_after": TODAY},
    )
    return [hit.record.id for hit in hits]


def demo() -> None:
    hits = filtered_search("SGCC-4012 超时")
    print(f"部门=ops 且有效期晚于 {TODAY} 的命中：{hits}")
    print("c2 已过期、c3 属于其他部门，均在打分前被排除。")


if __name__ == "__main__":
    demo()
