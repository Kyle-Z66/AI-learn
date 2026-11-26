"""
第 8 周 · 补足要点：向量检索的工程认知边界
================================================================
【对应知识点】文档第 8 周：pgvector 差异化叙事与 ANN 调参

【周次学习要点】
  - 向量检索不是玄学：它就是在熟悉的 RDBMS 上做近邻查询。
  - RBAC 与有效期字段必须在索引设计阶段进入表结构，事后补要全量重建。
  - ANN 参数没有"最优解"，只有"给定延迟预算下的召回率曲线"。

【易忽略细节】
  1. 过滤条件进 WHERE 而不是在应用层后置过滤，否则 Top-K 会漏召回。
  2. 选库先看团队能力：已有 PostgreSQL 运维经验时 pgvector 起步成本最低。
  3. 先修检索再修生成：第 8 周的召回率是第 10~11 周生成质量的上限。

【示例用途】可运行：`python -m week08.pitfalls.extra_gotchas`
             测试见 tests/week08/test_pitfalls.py
"""
from __future__ import annotations

SQL_MAPPING: tuple[tuple[str, str], ...] = (
    ("embedding <=> query", "ORDER BY 的排序键"),
    ("dept_id = $1", "RBAC 权限过滤"),
    ("valid_until > CURRENT_DATE", "有效期过滤"),
    ("LIMIT 50", "Top-K 截断"),
)

ANN_TRADEOFF: tuple[tuple[str, str, str], ...] = (
    ("ef_search 增大", "召回率上升", "查询延迟上升"),
    ("probes 增大", "召回率上升", "扫描桶数上升"),
    ("lists 增大", "单桶变小", "需更多 probes 才能保召回"),
)


def demo_sql_mindset() -> None:
    print("向量检索 = 熟悉的 SQL 加一个排序算子：")
    for expression, meaning in SQL_MAPPING:
        print(f"  {expression:<28} → {meaning}")


def demo_rbac_first() -> None:
    print("RBAC 字段要在 CREATE TABLE 阶段就存在：dept_id / valid_until / metadata")
    print("后置过滤会让 Top-K 里全是无权文档，看起来'检索不准'其实是权限漏了。")


def demo_ann_tradeoff() -> None:
    for action, gain, cost in ANN_TRADEOFF:
        print(f"{action:<12} 收益：{gain:<10} 代价：{cost}")


def demo() -> None:
    demo_sql_mindset()
    demo_rbac_first()
    demo_ann_tradeoff()


if __name__ == "__main__":
    demo()
