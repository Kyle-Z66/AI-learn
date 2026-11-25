"""
第 6 周单元测试 · 交付阶段认知误区
"""
from __future__ import annotations

from week06.pitfalls.extra_gotchas import (
    COVERAGE_KINDS,
    MERMAID_SAMPLE,
    PROBES,
    demo_architecture_diagram,
    demo_coverage_kinds,
    demo_probes,
    demo_rag_boundary,
)
from week06.pitfalls.fastapi_pitfalls import (
    demo_blocking_sleep,
    demo_docker_secret,
    demo_pseudo_streaming,
    demo_schema_boundary,
)


async def test_fastapi_pitfall_demos_runnable() -> None:
    await demo_blocking_sleep()
    demo_schema_boundary()
    demo_pseudo_streaming()
    demo_docker_secret()


def test_extra_gotcha_demos_runnable() -> None:
    assert len(PROBES) == 2
    assert len(COVERAGE_KINDS) == 2
    assert "FastAPI" in MERMAID_SAMPLE
    demo_probes()
    demo_coverage_kinds()
    demo_architecture_diagram()
    demo_rag_boundary()
