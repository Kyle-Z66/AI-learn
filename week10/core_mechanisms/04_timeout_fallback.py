"""
第 10 周 · 核心机制 04：超时降级回首阶段顺序
================================================================
【对应知识点】文档第 10 周：asyncio.wait_for 超时 → candidates[:top_k]

【周次学习要点】
  - 精排是"增益项"，超时时必须能摘掉，不能把整个问答请求拖失败。
  - 降级结果顺序与首阶段完全一致；UI 与下游不需感知发生了什么。
  - degraded / reason 要进日志与指标，否则永远发现不了 rerank 已挂。

【易忽略细节】
  1. TimeoutError 是 Exception 的子类，两个 except 的顺序不能反。
  2. CancelledError 不是 Exception，要继续抛，不能冒充降级。
  3. wait_for 的 timeout 单位是秒；传入毫秒值要除以 1000。

【示例用途】可运行：`python -m week10.core_mechanisms.04_timeout_fallback`
             测试见 tests/week10/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio

from week10.engineering.fallback import rerank_with_fallback
from week10.engineering.models import RerankCandidate, RerankResult
from week10.engineering.reranker import DeterministicReranker, RerankerConfig

CANDIDATES: list[RerankCandidate] = [
    RerankCandidate("d1", "断路器通用巡检流程", 0.95),
    RerankCandidate("d2", "SGCC-4012 巡检周期说明", 0.90),
    RerankCandidate("d3", "ERR_4012 错误码排查", 0.85),
]
QUERY = "SGCC-4012 巡检"


async def run_scenarios() -> list[RerankResult]:
    """跑成功 / 超时 / 故障三种场景，返回可直接断言的结果。"""
    scenarios = [
        RerankerConfig(),
        RerankerConfig(delay_ms=30),
        RerankerConfig(fail=True),
    ]
    results: list[RerankResult] = []
    for config in scenarios:
        results.append(
            await rerank_with_fallback(
                QUERY,
                CANDIDATES,
                top_k=2,
                timeout_ms=1 if config.delay_ms else 800,
                reranker=DeterministicReranker(config),
            )
        )
    return results


async def demo() -> None:
    labels = ("正常", "超时", "故障")
    for label, result in zip(labels, await run_scenarios(), strict=True):
        print(
            f"{label}: top2={[c.chunk_id for c in result.candidates]} "
            f"degraded={result.degraded} reason={result.reason or '-'}"
        )
    print("三条路径都返回 2 条候选；降级保住首阶段顺序，请求不失败")


if __name__ == "__main__":
    asyncio.run(demo())
