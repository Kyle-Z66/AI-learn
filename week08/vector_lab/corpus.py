"""
第 8 周 · 动手项目语料：第 7 周 chunk 文案的本地副本
================================================================
【对应知识点】文档第 8 周：把切分结果接入 embedding 与向量库

【周次学习要点】
  - 复制第 7 周语料的 chunk 文案，避免跨周耦合过深。
  - 每条记录带 dept_id 与 valid_until，用来做标量过滤实验。
  - 文本里保留 SGCC-4012 / ERR_4012，便于观察词面命中。

【易忽略细节】
  1. 这是"教学替身"向量实验，结果只说明工程链路，不代表真实语义质量。
  2. 过期记录故意留在库里，验证过滤而不是靠删除来保证正确。
  3. 维度固定为 16 便于打印；生产 DDL 用 1024，两者字段语义一致。

【示例用途】被 vector_lab/benchmark.py 与测试引用
"""
from __future__ import annotations

from dataclasses import dataclass

from week08.engineering.embeddings import HashEmbedding
from week08.engineering.models import EmbeddingRecord
from week08.engineering.vector_store import InMemoryVectorStore

TODAY = "2026-11-26"
QUERY = "ERR_4012 SGCC-4012 上游超时怎么处理"


@dataclass(frozen=True)
class LabItem:
    """一条带业务过滤字段的切分文案。"""

    doc_id: str
    text: str
    dept_id: str
    valid_until: str


LAB_ITEMS: tuple[LabItem, ...] = (
    LabItem(
        "c001",
        "SGCC-4012 网关运维知识库 / 1 适用范围与术语\n"
        "第1条 本规范适用于 SGCC-4012 网关的部署、升级、回滚与日常巡检。",
        "ops",
        "2030-12-31",
    ),
    LabItem(
        "c002",
        "1.1 术语表\nSGCC-4012 是本实验中的网关代号，"
        "ERR_4012 是其上游连接超时故障码。",
        "ops",
        "2030-12-31",
    ),
    LabItem(
        "c003",
        "2 告警分级\n第3条 cyclone 级别 1 表示单点告警，不影响整体服务。",
        "ops",
        "2030-12-31",
    ),
    LabItem(
        "c004",
        "2.1 响应动作\n值班人员先确认告警来源，再判断是否属于误报。",
        "dev",
        "2030-12-31",
    ),
    LabItem(
        "c005",
        "3 故障码对照表\n| ERR_4012 | 上游连接超时 | 检查上游健康状态与连接池 |",
        "ops",
        "2030-12-31",
    ),
    LabItem(
        "c006",
        "3.1 排障顺序\n第7条 出现 ERR_4012 时，先查上游健康探测，再查连接池。",
        "ops",
        "2025-06-30",
    ),
    LabItem(
        "c007",
        "4 变更与回滚\n第10条 所有变更必须先在小流量环境验证。",
        "platform",
        "2030-12-31",
    ),
    LabItem(
        "c008",
        "4.1 发布检查清单\n检查项包括配置版本、依赖版本、健康检查端点与熔断阈值四项。",
        "dev",
        "2030-12-31",
    ),
    LabItem(
        "c009",
        "5 复盘与知识沉淀\n第13条 级别 3 以上故障必须在 48 小时内产出复盘文档。",
        "platform",
        "2030-12-31",
    ),
    LabItem(
        "c010",
        "历史复盘按月归档，检索时以故障码与条款编号作为主要过滤条件。",
        "ops",
        "2030-12-31",
    ),
)


def build_store(*, dim: int = 16, metric: str = "cosine") -> InMemoryVectorStore:
    """把语料嵌入后装入内存向量库。"""
    embedder = HashEmbedding(dim)
    store = InMemoryVectorStore(dim, metric=metric)
    for item in LAB_ITEMS:
        store.add(
            EmbeddingRecord(
                item.doc_id,
                item.text,
                tuple(embedder.embed(item.text)),
                {"dept_id": item.dept_id, "valid_until": item.valid_until},
            )
        )
    return store


__all__ = ["LAB_ITEMS", "QUERY", "TODAY", "LabItem", "build_store"]
