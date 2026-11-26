"""
第 8 周 · 工程层：pgvector 参数化 SQL 生成
================================================================
【对应知识点】文档第 8 周：建表 + 索引 + 带标量过滤的向量检索

【周次学习要点】
  - RBAC（dept_id）与有效期（valid_until）在建表阶段就进字段，不是事后补丁。
  - HNSW 索引用 vector_cosine_ops；IVF 索引作为大数据的备选单列出来。
  - 检索 SQL 用 %s 占位符，向量与业务参数都从外面传，杜绝字符串拼接注入。

【易忽略细节 / 对照文档补足】
  1. 文档给了 SQL 示例但没强调参数化；这里把 SQL 与参数分开返回。
  2. cosine 距离 <=> 返回 0~2，相似度是 1 - distance，别和归一化点积混用。
  3. HNSW 查询调 ef_search、IVF 调 probes；参数越大召回越高、延迟越大。

【示例用途】core_mechanisms/05、vector_lab 与测试共用
"""
from __future__ import annotations


def build_create_table_sql(dim: int = 1024) -> str:
    """返回建表与 HNSW 余弦索引 DDL；dim 决定向量列长度。"""
    if dim <= 0:
        raise ValueError("dim 必须为正整数")
    return f"""CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS chunks (
    id BIGSERIAL PRIMARY KEY,
    doc_id BIGINT NOT NULL,
    content TEXT NOT NULL,
    embedding vector({dim}),
    dept_id INT,
    valid_until DATE,
    metadata JSONB
);

CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw
    ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS chunks_dept_valid
    ON chunks (dept_id, valid_until);
"""


def build_ivf_index_sql(lists: int = 100) -> str:
    """IVF 备选索引：lists 是倒排桶数量，通常取 sqrt(行数) 量级。"""
    if lists <= 0:
        raise ValueError("lists 必须为正整数")
    return (
        "CREATE INDEX IF NOT EXISTS chunks_embedding_ivf\n"
        f"    ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = {lists});\n"
    )


def build_search_sql() -> str:
    """参数化检索 SQL：%s 依次为向量、部门、向量、top_k。"""
    return """SELECT content, 1 - (embedding <=> %s::vector) AS score
FROM chunks
WHERE dept_id = %s AND valid_until > CURRENT_DATE
ORDER BY embedding <=> %s::vector
LIMIT %s;
"""


def build_search_params(
    vector_literal: str, dept_id: int, top_k: int
) -> tuple[str, int, str, int]:
    """按 build_search_sql() 的占位符顺序返回参数。"""
    return (vector_literal, dept_id, vector_literal, top_k)


__all__ = [
    "build_create_table_sql",
    "build_ivf_index_sql",
    "build_search_params",
    "build_search_sql",
]
