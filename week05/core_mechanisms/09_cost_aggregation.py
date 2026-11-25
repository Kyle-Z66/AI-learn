"""
第 5 周 · 核心机制 09：按 provider 差异化计价与日聚合
================================================================
【对应知识点】文档第 5 周：成本按 provider 差异化计算 + 成本日聚合报表

【周次学习要点】
  - 单价表按 provider 配置（第 2 周"不硬编码价格"的延续）。
  - 报表按 (日期, provider, 场景) 聚合，支持按天/按厂商过滤。
  - 成本记在"实际使用的模型"上，降级后不能按首选模型算。

【易忽略细节】
  1. 示意单价不是实时价格，生产必须从配置中心读取。
  2. 重试与降级的每条记录都要计入，否则账单与实际调用不一致。
  3. 缓存命中导致 token 用量偏低，分析单位成本时要看命中率。

【示例用途】可运行：`python -m week05.core_mechanisms.09_cost_aggregation`
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

from dataclasses import replace

from week05.engineering.audit import AuditRecord
from week05.engineering.cost_report import (
    build_daily_report,
    estimate_cost,
    format_report,
)


def make_record(day: str, provider: str, tokens: int) -> AuditRecord:
    """构造一条已按 provider 单价算好成本的审计记录。"""
    return AuditRecord(
        trace_id=f"trace-{provider}-{tokens}",
        request_id=f"req-{provider}-{tokens}",
        timestamp=f"{day}T10:00:00",
        user_id="u-1",
        scenario="ticket_extract",
        provider=provider,
        model=provider,
        status="success",
        http_status=200,
        error_type="",
        error_message="",
        retry_count=0,
        fallback_used=False,
        input_tokens=tokens,
        output_tokens=tokens // 4,
        latency_ms=500.0,
        cost_yuan=estimate_cost(provider, tokens, tokens // 4),
        request_digest="",
        response_digest="",
    )


def demo() -> None:
    records = [
        make_record("2026-11-25", "qwen", 1000),
        make_record("2026-11-25", "deepseek", 1000),
        make_record("2026-11-25", "qwen", 2000),
        make_record("2026-11-26", "deepseek", 500),
    ]
    rows = build_daily_report(records)
    print(format_report(rows))
    print("\n只看 deepseek：")
    print(format_report(build_daily_report(records, provider="deepseek")))
    print("\n只看 2026-11-25：")
    print(format_report(build_daily_report(records, day="2026-11-25")))
    print("不可变记录可直接复制改场景：", replace(records[0], scenario="qa").scenario)


if __name__ == "__main__":
    demo()
