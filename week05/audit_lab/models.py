"""
第 5 周 · 动手项目数据模型：审计实验输入
================================================================
【对应知识点】文档第 5 周 19 字段审计 + 成本日聚合

【周次学习要点】
  - 实验用 LabCase 描述"一次尝试"，再展开成 19 字段审计记录。
  - 同一个 trace 下的多条 LabCase 构成完整链路（失败 → 降级 → 成功）。
  - 成本在创建记录时按实际 provider 单价计算，不做事后估算。

【易忽略细节】
  1. 字段数由工程层 AUDIT_FIELDS 推导，避免实验与代码各写一份清单。
  2. request_id 在链路内递增，方便按时间排序还原过程。
  3. TTFT 不属于 19 字段，放在指标侧单独采集。

【示例用途】被 reporter.py / __main__.py 引用；测试见 tests/week05/test_audit_lab.py
"""
from __future__ import annotations

from dataclasses import dataclass

from week05.engineering.audit import AUDIT_FIELDS, AuditRecord
from week05.engineering.cost_report import estimate_cost

AUDIT_FIELD_COUNT = len(AUDIT_FIELDS)


@dataclass(frozen=True)
class LabCase:
    """一次 LLM 尝试的输入（实验用简化模型）。"""

    trace_id: str
    scenario: str
    provider: str
    status: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    http_status: int | None = 200
    error_type: str = ""
    error_message: str = ""
    retry_count: int = 0
    fallback_used: bool = False
    day: str = "2026-11-25"
    user_id: str = "u-1024"


def to_audit_record(case: LabCase, sequence: int) -> AuditRecord:
    """展开成 19 字段记录；成本按实际 provider 计价。"""
    return AuditRecord(
        trace_id=case.trace_id,
        request_id=f"{case.trace_id}-{sequence:02d}",
        timestamp=f"{case.day}T10:00:{sequence:02d}",
        user_id=case.user_id,
        scenario=case.scenario,
        provider=case.provider,
        model=case.provider,
        status=case.status,
        http_status=case.http_status,
        error_type=case.error_type,
        error_message=case.error_message,
        retry_count=case.retry_count,
        fallback_used=case.fallback_used,
        input_tokens=case.input_tokens,
        output_tokens=case.output_tokens,
        latency_ms=case.latency_ms,
        cost_yuan=estimate_cost(case.provider, case.input_tokens, case.output_tokens),
        request_digest="ticket_extract",
        response_digest=case.status,
    )
