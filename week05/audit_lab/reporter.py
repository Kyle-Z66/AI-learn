"""
第 5 周 · 动手项目：链路查询 + 成本报表 + 指标快照
================================================================
【对应知识点】文档第 5 周验收：审计可查完整链路、成本按天/provider 聚合

【周次学习要点】
  - 审计记录是事实源：报表与指标都从同一批记录算，避免口径不一致。
  - 成本报表按 (日期, provider, 场景) 聚合并支持过滤。
  - 指标侧补 TTFT（审计 19 字段不含它），由采集时单独传入。

【易忽略细节】
  1. 同一 trace 的多条记录要按 timestamp/rowid 排序才还原真实顺序。
  2. 失败记录 input/output token 可能为 0，不会被误判成缓存命中（看 status）。
  3. 报表里的 provider 是实际厂商，降级场景不能用首选模型单价。

【示例用途】被 __main__.py 调用；测试见 tests/week05/test_audit_lab.py
"""
from __future__ import annotations

from collections.abc import Sequence

from week05.engineering.audit import AuditRecord, SQLiteAuditStore
from week05.engineering.cost_report import build_daily_report, format_report
from week05.engineering.metrics import MetricsCollector, MetricsSnapshot, RequestMetric


def print_trace_chain(store: SQLiteAuditStore, trace_id: str) -> str:
    """按 trace 打印完整链路，返回可断言的文本。"""
    records = store.find_by_trace(trace_id)
    lines = [f"trace={trace_id} 共 {len(records)} 条记录"]
    for record in records:
        lines.append(
            f"  {record.request_id} | {record.provider:<8} | {record.status:<22} | "
            f"重试={record.retry_count} | 降级={record.fallback_used} | "
            f"成本={record.cost_yuan:.4f}元"
        )
    return "\n".join(lines)


def print_cost_report(store: SQLiteAuditStore) -> str:
    """验收接口：按天 / provider 聚合的成本报表。"""
    return format_report(build_daily_report(store.all_records()))


def build_metrics(
    records: Sequence[AuditRecord],
    ttft_by_request: dict[str, float] | None = None,
) -> MetricsSnapshot:
    """从审计事实源构建指标快照；TTFT 需调用方额外提供。"""
    ttfts = ttft_by_request or {}
    collector = MetricsCollector()
    for record in records:
        collector.record(
            RequestMetric(
                provider=record.provider,
                latency_ms=record.latency_ms,
                ttft_ms=ttfts.get(record.request_id),
                ok=record.status.startswith("success"),
                status_code=record.http_status,
                input_tokens=record.input_tokens,
                output_tokens=record.output_tokens,
                cache_hit="cache" in record.status,  # 失败记录的 0 token 不是缓存命中
            )
        )
    return collector.snapshot()
