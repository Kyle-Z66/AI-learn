"""
第 5 周单元测试 · 文档熔断器缺陷与认知误区
"""
from __future__ import annotations

from week05.pitfalls.extra_gotchas import (
    CONCEPTS,
    demo_cost_attribution,
    demo_log_sanitization,
    demo_percentile_definition,
    demo_three_concepts,
)
from week05.pitfalls.resilience_pitfalls import (
    DocCircuitBreaker,
    demo_doc_clock_risk,
    demo_half_open_flood,
    demo_non_idempotent_retry,
    demo_retry_storm,
    demo_timeout_confusion,
)


def test_doc_half_open_allows_flood() -> None:
    breaker = DocCircuitBreaker()
    breaker.state = "half_open"
    assert all(breaker.allow_request() for _ in range(50))


def test_doc_state_machine_still_works() -> None:
    breaker = DocCircuitBreaker(fail_threshold=2)
    for _ in range(2):
        breaker.record_failure()
    assert breaker.state == "open"
    breaker.record_success()
    assert breaker.state == "closed"


def test_pitfall_demos_runnable() -> None:
    demo_doc_clock_risk()
    demo_half_open_flood()
    demo_retry_storm()
    demo_non_idempotent_retry()


async def test_timeout_confusion_demo_runnable() -> None:
    await demo_timeout_confusion()


def test_extra_concepts_demos_runnable() -> None:
    assert len(CONCEPTS) == 3
    names = {item[0] for item in CONCEPTS}
    assert "限流（第4周）" in names and "熔断（本周）" in names
    demo_three_concepts()
    demo_percentile_definition()
    demo_cost_attribution()
    demo_log_sanitization()
