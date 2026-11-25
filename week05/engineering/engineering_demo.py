"""
第 5 周 · 动作综合示范：熔断 + 重试 + 审计 + 成本 + 指标
================================================================
【对应知识点】文档第 5 周三个工作任务的工程层串讲

【周次学习要点】
  - 熔断挡住持续失败，重试消化瞬时失败，审计记录全部结果，报表算清成本。
  - 四者职责不同：熔断看"一段时间"，重试看"一次调用"，审计看"每一条链路"。

【易忽略细节 / 对照文档补足】
  1. 熔断器时钟注入后，恢复窗口无需真的 sleep，单测和演示都稳定。
  2. 审计写入的是脱敏摘要，不是请求原文。
  3. 指标用 nearest-rank 分位数，和监控大盘口径保持一致。

【示例用途】可运行：`python -m week05.engineering.engineering_demo`
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

import asyncio
from contextlib import suppress

from week05.engineering.audit import (
    AuditRecord,
    SQLiteAuditStore,
    new_trace_id,
    sanitize,
)
from week05.engineering.circuit_breaker import (
    BreakerConfig,
    CircuitBreaker,
    CircuitOpenError,
)
from week05.engineering.cost_report import build_daily_report, format_report
from week05.engineering.metrics import MetricsCollector, RequestMetric
from week05.engineering.retry import HttpStatusError, RetryPolicy, call_with_retry


async def demo_breaker() -> None:
    """连续失败 → open → 恢复窗口 → half_open → 成功 → closed。"""
    now = [0.0]
    breaker = CircuitBreaker(
        "qwen",
        BreakerConfig(
            failure_threshold=2,
            recovery_timeout=10.0,
            success_threshold=1,
        ),
        clock=lambda: now[0],
    )

    async def fail() -> str:
        raise ConnectionError("模拟厂商故障")

    async def ok() -> str:
        return "ok"

    for _ in range(2):
        with suppress(ConnectionError):
            await breaker.guard(fail)
    print("连续 2 次失败后：", breaker.snapshot().state)

    try:
        await breaker.guard(ok)
    except CircuitOpenError:
        print("熔断期间请求被快速拒绝，没有再打模型")

    now[0] = 11.0  # 注入时钟推进 11 秒，跨过恢复窗口
    print("恢复窗口过后：", breaker.snapshot().state)
    print("探针结果：", await breaker.guard(ok), "→ 状态：", breaker.snapshot().state)


async def demo_retry() -> None:
    """429 + Retry-After：指数退避重试后成功。"""
    attempts = 0

    async def flaky() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise HttpStatusError(429, "限流", retry_after=0.001)
        return "done"

    result = await call_with_retry(
        flaky,
        RetryPolicy(max_attempts=3, base_delay=0.001, jitter=False),
    )
    print("重试结果：", result, "| 实际尝试次数：", attempts)


def demo_audit_cost_metrics() -> None:
    """19 字段审计落库 + 日报表 + 指标快照。"""
    store = SQLiteAuditStore()
    trace = new_trace_id()
    store.append(
        AuditRecord(
            trace_id=trace,
            request_id="req-001",
            timestamp="2026-11-25T10:00:00",
            user_id="u-1",
            scenario="ticket_extract",
            provider="qwen",
            model="qwen-plus",
            status="success",
            http_status=200,
            error_type="",
            error_message="",
            retry_count=1,
            fallback_used=False,
            input_tokens=1000,
            output_tokens=200,
            latency_ms=850.0,
            cost_yuan=1.2,
            request_digest=sanitize("api_key=secret-123, 系统 cyclone"),
            response_digest='{"system_name": "cyclone"}',
        )
    )
    print("按 trace 查到记录数：", len(store.find_by_trace(trace)))
    print(format_report(build_daily_report(store.all_records())))
    collector = MetricsCollector()
    collector.record(
        RequestMetric("qwen", 850.0, 120.0, True, 200, 1000, 200, False)
    )
    snapshot = collector.snapshot()
    print(
        f"指标：成功率={snapshot.success_rate:.0%} "
        f"p95={snapshot.p95_latency_ms:.1f}ms "
        f"TTFT-p50={snapshot.ttft_p50_ms:.1f}ms"
    )


async def demo() -> None:
    await demo_breaker()
    await demo_retry()
    demo_audit_cost_metrics()


if __name__ == "__main__":
    asyncio.run(demo())
