"""
第 8 周 · 工程层示范：本地向量、三种度量与 pgvector SQL
================================================================
【对应知识点】文档第 8 周：Embedding 选型 + 向量库 + 标量过滤

【周次学习要点】
  - 用 HashEmbedding 做确定性替身，完整走通"文本 → 向量 → 入库 → 检索"。
  - 同一个查询分别用 cosine / dot / euclidean 排序，观察口径差异。
  - DDL 与检索 SQL 由函数生成并参数化，可直接对照文档里的 pgvector 示例。

【易忽略细节 / 对照文档补足】
  1. 文档默认推荐 pgvector，但教学环境不启数据库；SQL 生成与内存库共用字段语义。
  2. 演示数据里放了过期文档，验证 where 过滤确实在打分前生效。
  3. 这不是真实语义检索：结果只说明工程链路正确，不说明 embedding 质量。

【示例用途】可运行：`python -m week08.engineering.engineering_demo`
             测试见 tests/week08/test_engineering.py
"""
from __future__ import annotations

import math
import tempfile
from pathlib import Path

from week08.engineering.embeddings import HashEmbedding, normalize_vector
from week08.engineering.models import EmbeddingRecord
from week08.engineering.pgvector_sql import (
    build_create_table_sql,
    build_search_params,
    build_search_sql,
)
from week08.engineering.vector_store import (
    InMemoryVectorStore,
    load_store,
    save_store,
)

DEMO_TEXTS: tuple[str, ...] = (
    "SGCC-4012 上游连接超时 ERR_4012",
    "ERR_4012 检查上游健康状态与连接池",
    "cyclone 级别 2 局部降级，30 分钟响应",
    "回滚脚本与发布检查清单",
)


def demo_embeddings() -> None:
    for dim in (16, 1024):
        vector = HashEmbedding(dim).embed(DEMO_TEXTS[0])
        norm = math.sqrt(sum(value * value for value in vector))
        print(f"dim={dim:<4} 向量长度={len(vector):<4} L2 范数={norm:.4f}")
    raw = [3.0, 4.0]
    print(f"归一化 [3,4] → {[round(value, 3) for value in normalize_vector(raw)]}")


def build_demo_store() -> InMemoryVectorStore:
    """构造含部门与有效期元数据的演示库。"""
    embedder = HashEmbedding(16)
    store = InMemoryVectorStore(16, metric="cosine")
    for index, text in enumerate(DEMO_TEXTS, start=1):
        store.add(
            EmbeddingRecord(
                id=f"c{index:03d}",
                text=text,
                vector=tuple(embedder.embed(text)),
                metadata={
                    "dept_id": "ops" if index % 2 else "dev",
                    "valid_until": "2025-01-01" if index == 4 else "2030-12-31",
                },
            )
        )
    return store


def demo_search() -> None:
    store = build_demo_store()
    query = tuple(HashEmbedding(16).embed_query("ERR_4012 上游超时怎么处理"))
    for metric in ("cosine", "dot", "euclidean"):
        hits = store.search(query, top_k=2, metric=metric)
        print(f"{metric:<10} Top-2：" + " / ".join(hit.record.id for hit in hits))
    filtered = store.search(
        query,
        top_k=4,
        where={"dept_id": "ops", "valid_until_after": "2026-01-01"},
    )
    print("标量过滤后：" + " / ".join(hit.record.id for hit in filtered))


def demo_persistence() -> None:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "store.json"
        before = build_demo_store()
        save_store(before, path)
        after = load_store(path)
        print(f"持久化：保存前 {len(before)} 条，重载后 {len(after)} 条")


def demo_sql() -> None:
    ddl = build_create_table_sql(1024)
    print("DDL 关键行：")
    for line in ddl.splitlines():
        if "dept_id" in line or "valid_until" in line or "hnsw" in line:
            print("  " + line.strip())
    print("检索 SQL：")
    print(build_search_sql().strip())
    print("参数：", build_search_params("[0.1,0.2]", 7, 50))


def demo() -> None:
    demo_embeddings()
    print("\n-- 检索与过滤 --")
    demo_search()
    print("\n-- 持久化 --")
    demo_persistence()
    print("\n-- pgvector SQL --")
    demo_sql()


if __name__ == "__main__":
    demo()
