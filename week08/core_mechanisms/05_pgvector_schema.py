"""
第 8 周 · 核心机制 05：pgvector 表结构与索引
================================================================
【对应知识点】文档第 8 周：CREATE TABLE + HNSW cosine index

【周次学习要点】
  - DDL 里显式放 dept_id / valid_until / metadata，把 RBAC 前置到索引设计阶段。
  - HNSW 用 vector_cosine_ops；IVF 是备选，后续按数据规模选择。
  - 业务复合索引 (dept_id, valid_until) 让标量过滤先缩小候选集。

【易忽略细节】
  1. 只建向量索引不建标量索引，过滤仍会退化为大范围扫描。
  2. metadata 用 JSONB 而不是 TEXT，便于后续按字段过滤与建立表达式索引。
  3. cosine 索引必须搭配余弦距离算子 <=>，用错算子索引不会被命中。

【示例用途】可运行：`python -m week08.core_mechanisms.05_pgvector_schema`
             测试见 tests/week08/test_core_mechanisms.py
"""
from __future__ import annotations

from week08.engineering.pgvector_sql import build_create_table_sql


def schema_checks(ddl: str) -> dict[str, bool]:
    """检查 DDL 是否覆盖文档要求的关键字段与索引。"""
    return {
        "vector 列": "embedding vector(" in ddl,
        "dept_id": "dept_id INT" in ddl,
        "valid_until": "valid_until DATE" in ddl,
        "metadata JSONB": "metadata JSONB" in ddl,
        "HNSW cosine": "USING hnsw" in ddl and "vector_cosine_ops" in ddl,
    }


def demo() -> None:
    ddl = build_create_table_sql(1024)
    checks = schema_checks(ddl)
    print(ddl)
    print("自检：" + " / ".join(f"{name}={'OK' if ok else '缺失'}" for name, ok in checks.items()))


if __name__ == "__main__":
    demo()
