"""
第 5 周单元测试 · 工程层：熔断 / 重试 / 幂等 / 超时 / 审计 / 成本 / 指标
"""
from __future__ import annotations

import asyncio

import pytest
from week05.engineering.audit import AUDIT_FIELDS, AuditRecord, SQLiteAuditStore, sanitize
from week05.engineering.circuit_breaker import (
    BreakerConfig,
    BreakerState,
    CircuitBreaker,
    CircuitOpenError,
)
from week05.engineering.cost_report import build_daily_report, estimate_cost
from week05.engineering.metrics import MetricsCollector, RequestMetric, percentile
from week05.engineering.retry import (
    HttpStatusError,
    IdempotencyGuard,
    NonRetryableError,
    RetryPolicy,
    backoff_delay,
    call_with_retry,
    is_retryable,
    make_idempotency_key,
)
from week05.engineering.timeouts import (
    ConnectTimeout,
    ReadTimeout,
    TimeoutBudget,
    TotalTimeout,
    request_with_budget,
)


async def test_breaker_full_state_cycle() -> None:
    """验收：连续失败 → open → 超时 → half_open → 恢复。"""
    now = [0.0]
    breaker = CircuitBreaker(
        "qwen",
        BreakerConfig(failure_threshold=2, recovery_timeout=10.0, success_threshold=2),
        clock=lambda: now[0],
    )

    async def fail() -> str:
        raise ConnectionError("boom")

    async def ok() -> str:
        return "ok"

    for _ in range(2):
        with pytest.raises(ConnectionError):
            await breaker.guard(fail)
    assert breaker.state is BreakerState.OPEN

    with pytest.raises(CircuitOpenError):
        await breaker.guard(ok)
    now[0] = 11.0
    assert breaker.state is BreakerState.HALF_OPEN

    allowed = await asyncio.gather(*(breaker.allow_request() for _ in range(5)))
    assert sum(allowed) == 1  # 半开只允许一个探针
    await breaker.record_success()
    assert breaker.state is BreakerState.HALF_OPEN
    assert await breaker.allow_request()
    await breaker.record_success()
    assert breaker.state is BreakerState.CLOSED
    assert breaker.snapshot().open_count == 1


async def test_half_open_failure_retrips() -> None:
    now = [0.0]
    breaker = CircuitBreaker(
        "glm",
        BreakerConfig(failure_threshold=1, recovery_timeout=5.0, success_threshold=2),
        clock=lambda: now[0],
    )
    if await breaker.allow_request():
        await breaker.record_failure()
    assert breaker.state is BreakerState.OPEN
    now[0] = 6.0
    assert breaker.state is BreakerState.HALF_OPEN
    assert await breaker.allow_request()
    await breaker.record_failure()
    assert breaker.state is BreakerState.OPEN
    assert breaker.snapshot().open_count == 2


async def test_cancelled_probe_releases_slot() -> None:
    now = [0.0]
    breaker = CircuitBreaker(
        "qwen",
        BreakerConfig(failure_threshold=1, recovery_timeout=5.0),
        clock=lambda: now[0],
    )
    if await breaker.allow_request():
        await breaker.record_failure()
    now[0] = 6.0
    assert breaker.state is BreakerState.HALF_OPEN

    async def blocked() -> str:
        await asyncio.Event().wait()
        return "never"

    task = asyncio.create_task(breaker.guard(blocked))
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert breaker.snapshot().probe_inflight == 0


def test_retryable_classification() -> None:
    assert is_retryable(HttpStatusError(429))
    assert is_retryable(HttpStatusError(503))
    assert not is_retryable(HttpStatusError(400))
    assert not is_retryable(HttpStatusError(401))
    assert is_retryable(TimeoutError("slow"))
    assert is_retryable(ConnectionError("reset"))
    assert not is_retryable(NonRetryableError("bad payload"))
    assert not is_retryable(ValueError("unknown"))  # 未知异常快速失败


def test_backoff_is_capped_and_deterministic() -> None:
    policy = RetryPolicy(base_delay=0.1, multiplier=2.0, max_delay=0.5, jitter=False)
    assert [backoff_delay(i, policy) for i in range(1, 5)] == [0.1, 0.2, 0.4, 0.5]
    assert backoff_delay(1, RetryPolicy(), rng=lambda: 0.0) == 0.0


async def test_retry_honors_retry_after() -> None:
    slept: list[float] = []

    async def fake_sleep(seconds: float) -> None:
        slept.append(seconds)

    attempts = 0

    async def flaky() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise HttpStatusError(429, "限流", retry_after=0.9)
        return "done"

    result = await call_with_retry(
        flaky,
        RetryPolicy(max_attempts=3, base_delay=0.01, jitter=False),
        sleep=fake_sleep,
    )
    assert result == "done" and attempts == 3
    assert slept == [0.9, 0.9]


async def test_non_retryable_stops_immediately() -> None:
    attempts = 0

    async def broken() -> str:
        nonlocal attempts
        attempts += 1
        raise HttpStatusError(401, "鉴权失败")

    with pytest.raises(HttpStatusError):
        await call_with_retry(broken, RetryPolicy(max_attempts=5))
    assert attempts == 1


def test_idempotency_key_is_stable() -> None:
    payload = {"user": "u-1", "ticket": "T-1"}
    assert make_idempotency_key("order.create", payload) == make_idempotency_key(
        "order.create", {"ticket": "T-1", "user": "u-1"}
    )
    assert make_idempotency_key("order.create", payload) != make_idempotency_key(
        "order.cancel", payload
    )


async def test_idempotency_guard_dedupes_and_expires() -> None:
    now = [0.0]
    guard = IdempotencyGuard(ttl=10.0, clock=lambda: now[0])
    executed = 0

    async def operation() -> str:
        nonlocal executed
        executed += 1
        return "order-1"

    assert await guard.run("key", operation) == "order-1"
    assert await guard.run("key", operation) == "order-1"
    assert executed == 1 and guard.hits == 1
    now[0] = 11.0
    await guard.run("key", operation)
    assert executed == 2


async def test_three_timeout_stages_are_distinguishable() -> None:
    with pytest.raises(ConnectTimeout):
        await request_with_budget(TimeoutBudget(0.01, 0.1, 1.0), 0.05, 0.0)
    with pytest.raises(ReadTimeout):
        await request_with_budget(TimeoutBudget(0.1, 0.01, 1.0), 0.0, 0.05)
    with pytest.raises(TotalTimeout):
        await request_with_budget(TimeoutBudget(0.1, 0.1, 0.03), 0.01, 0.03)
    assert await request_with_budget(TimeoutBudget(0.1, 0.1, 1.0), 0.0, 0.0) == "ok"


def test_invalid_timeout_budget() -> None:
    with pytest.raises(ValueError):
        TimeoutBudget(0, 1.0, 1.0).validate()
    assert TimeoutBudget(0.1, 0.1, 0.05).is_tight()


def make_record(
    trace: str, provider: str, day: str, cost: float, status: str = "success"
) -> AuditRecord:
    return AuditRecord(
        trace_id=trace,
        request_id=f"{trace}-01",
        timestamp=f"{day}T10:00:00",
        user_id="u-1",
        scenario="ticket_extract",
        provider=provider,
        model=provider,
        status=status,
        http_status=200,
        error_type="",
        error_message="",
        retry_count=0,
        fallback_used=False,
        input_tokens=1000,
        output_tokens=200,
        latency_ms=500.0,
        cost_yuan=cost,
        request_digest="",
        response_digest="",
    )


def test_audit_has_19_fields_and_sanitizes() -> None:
    assert len(AUDIT_FIELDS) == 19
    masked = sanitize("api_key=FAKE-KEY, phone=13812345678")
    assert "FAKE-KEY" not in masked and "13812345678" not in masked


def test_audit_store_query_by_trace_and_date() -> None:
    store = SQLiteAuditStore()
    store.append(make_record("t-1", "qwen", "2026-11-25", 1.0))
    store.append(make_record("t-1", "deepseek", "2026-11-25", 0.5, "error"))
    store.append(make_record("t-2", "glm", "2026-11-26", 0.7))
    assert len(store.find_by_trace("t-1")) == 2
    assert store.find_by_trace("t-1")[0].provider == "qwen"
    assert len(store.find_by_date("2026-11-25")) == 2
    assert len(store.all_records()) == 3


def test_daily_cost_report_filters() -> None:
    records = [
        make_record("t-1", "qwen", "2026-11-25", estimate_cost("qwen", 1000, 200)),
        make_record("t-2", "deepseek", "2026-11-26", estimate_cost("deepseek", 1000, 200)),
    ]
    all_rows = build_daily_report(records)
    assert len(all_rows) == 2
    assert all_rows[0].provider == "qwen"
    assert len(build_daily_report(records, provider="deepseek")) == 1
    assert len(build_daily_report(records, day="2026-11-26")) == 1


def test_percentile_and_metrics_snapshot() -> None:
    assert percentile([], 0.95) == 0.0
    assert percentile([10, 20, 30, 40, 50], 0.95) == 50
    with pytest.raises(ValueError):
        percentile([1, 2], 0)
    collector = MetricsCollector()
    collector.record(RequestMetric("qwen", 100, 20, True, 200, 10, 5, False))
    collector.record(RequestMetric("deepseek", 300, None, False, 429, 0, 0, True))
    snapshot = collector.snapshot()
    assert snapshot.count == 2
    assert snapshot.success_rate == 0.5
    assert snapshot.error_429_ratio == 0.5
    assert snapshot.ttft_p50_ms == 20
    assert snapshot.cache_hit_rate == 0.5
    assert collector.by_provider() == {"qwen": 1, "deepseek": 1}
