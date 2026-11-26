"""
第 10 周 · 动手项目：rerank 实验语料（独立复制，思想复用第 9 周）
================================================================
【对应知识点】文档第 10 周：Top-50 → Top-5，三方指标对比

【周次学习要点】
  - 语料独立成文件，便于第 10 周实验单独运行、不依赖第 9 周目录状态。
  - 15 条模拟电网/运维 chunk：含型号、错误码、失效条目与跨部门内容。
  - 数据全部本地构造，不接真实系统、不引入 API Key。

【易忽略细节】
  1. 这是教学模拟，不对应任何真实业务数据；REPORT 只写程序真实输出。
  2. 标注 relevant 用 chunk_id，避免文本差异影响 Recall/MRR 计算。
  3. 候选预算上限写 50，但实际语料 15 条 → 实验里取 min(50, 15)。

【示例用途】被 rerank_lab/__main__.py 与 tests/week10/test_rerank_lab.py 引用。
"""
from __future__ import annotations

from dataclasses import dataclass

from week09.engineering.models import Candidate


@dataclass(frozen=True)
class LabQuery:
    """rerank 实验查询：文本 + 相关 chunk + 过滤条件。"""

    query_id: str
    text: str
    relevant: str
    dept: str | None = None
    valid_only: bool = True


CORPUS: list[Candidate] = [
    Candidate("c-01", "SGCC-4012 断路器巡检周期与温度阈值", "manual", "运维"),
    Candidate("c-02", "SGCC-4012 机械故障排查步骤", "manual", "运维"),
    Candidate("c-03", "SGCC-5200 隔离开关检修周期", "manual", "运维"),
    Candidate("c-04", "ERR_4012 错误码表示通信链路超时", "error_codes", "运维"),
    Candidate("c-05", "ERR_5200 错误码表示传感器校准失败", "error_codes", "运维"),
    Candidate("c-06", "断路器通用巡检流程与安全注意事项", "manual", "运维"),
    Candidate("c-07", "变电站冬季防冻巡检要点", "manual", "运维"),
    Candidate("c-08", "SGCC-4012 停用批次退运办法", "archive", "运维", False),
    Candidate("c-09", "国网设备型号命名规则与 SGCC 前缀", "glossary", "运维"),
    Candidate("c-10", "设备巡检工单审批流转规则", "process", "运维"),
    Candidate("c-11", "财务差旅报销标准", "finance", "财务"),
    Candidate("c-12", "SGCC-4012 采购合同编号规则", "finance", "财务"),
    Candidate("c-13", "API 网关错误码与重试策略", "error_codes", "研发"),
    Candidate("c-14", "WebSocket 断连后的消息补偿", "design", "研发"),
    Candidate("c-15", "巡检机器人调度策略", "design", "研发"),
]

QUERIES: list[LabQuery] = [
    LabQuery("q-01", "SGCC-4012 巡检周期", "c-01", "运维"),
    LabQuery("q-02", "ERR_4012 通信超时排查", "c-04", "运维"),
    LabQuery("q-03", "断路器通用巡检流程", "c-06", "运维"),
    LabQuery("q-04", "SGCC-4012 机械故障", "c-02", "运维"),
    LabQuery("q-05", "变电站冬季防冻巡检", "c-07", "运维"),
    LabQuery("q-06", "巡检工单审批规则", "c-10", "运维"),
]


def build_corpus() -> list[Candidate]:
    """返回拷贝，避免实验过程修改共享语料。"""
    return [item.copy_without_scores() for item in CORPUS]


__all__ = ["CORPUS", "QUERIES", "LabQuery", "build_corpus"]
