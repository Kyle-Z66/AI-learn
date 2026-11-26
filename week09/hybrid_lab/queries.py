"""
第 9 周 · 动手项目：普通 / 专名 / 带过滤的查询集
================================================================
【对应知识点】文档第 9 周：构造专名查询对比纯向量与混合召回

【周次学习要点】
  - 10 条查询分三组：普通语义问题、专名问题、带 dept/valid 过滤的问题。
  - relevant 用 chunk_id 集合标注，Recall@K 可直接逐条核对。
  - 过滤条件随查询携带，两路方法用同一条件，比较才公平。

【易忽略细节】
  1. 普通问题不该只靠 BM25；专名问题不该只靠向量；分组才能看清互补性。
  2. 带过滤的查询若把过滤放在融合后，会出现"少一条"现象，实验里能复现。
  3. 标注只针对本教学语料，不作为任何真实业务的评测集。

【示例用途】被 hybrid_lab/__main__.py 与 tests/week09/test_hybrid_lab.py 引用。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QueryCase:
    """一条可复现的查询用例：问题文本 + 过滤条件 + 相关文档集合。"""

    query_id: str
    text: str
    group: str  # 普通 / 专名 / 过滤
    relevant: frozenset[str]
    dept: str | None = None
    valid_only: bool = True


QUERIES: list[QueryCase] = [
    QueryCase("q-01", "断路器巡检需要注意什么", "普通", frozenset({"c-06"})),
    QueryCase("q-02", "冬天变电站设备防冻怎么做", "普通", frozenset({"c-07"})),
    QueryCase("q-03", "巡检工单审批流程", "普通", frozenset({"c-11"})),
    QueryCase("q-04", "SGCC-4012 巡检周期", "专名", frozenset({"c-01"})),
    QueryCase("q-05", "ERR_4012 通信超时怎么排查", "专名", frozenset({"c-04"})),
    QueryCase("q-06", "SGCC-5200 检修周期", "专名", frozenset({"c-03"})),
    QueryCase(
        "q-07",
        "ERR_4012 重复报障工单",
        "专名",
        frozenset({"c-10"}),
        valid_only=False,
    ),
    QueryCase("q-08", "SGCC-4012 巡检周期", "过滤", frozenset({"c-01"}), "运维"),
    QueryCase("q-09", "断路器巡检流程", "过滤", frozenset({"c-06"}), "运维"),
    QueryCase("q-10", "差旅报销发票要求", "过滤", frozenset({"c-12"}), "财务"),
]


__all__ = ["QUERIES", "QueryCase"]
