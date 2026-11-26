"""
第 10 周 · 工程层：rerank 超时/异常降级到首阶段顺序
================================================================
【对应知识点】文档第 10 周：rerank_with_fallback 容错设计

【周次学习要点】
  - 超时或异常不能让整个请求失败：直接返回 candidates[:top_k]。
  - degraded=True 必须可见，否则指标里分不清"精排"与"降级"两种结果。
  - 思路与 Java 侧 Redis/WebSocket 降级同构：第 5 周熔断链在这里复用认知，不复制代码。

【易忽略细节 / 对照文档补足】
  1. 文档 `except (asyncio.TimeoutError, Exception)` 写法冗余；TimeoutError 本身是 Exception。
  2. asyncio.CancelledError 不是 Exception，不应吞掉——客户端断开要能取消任务。
  3. wait_for 超时会取消内部 gather；打分函数用 await asyncio.sleep 才可被取消。

【示例用途】被 engineering_demo.py / core_mechanisms/04 引用；
             测试见 tests/week10/test_engineering.py
"""
from __future__ import annotations

import asyncio

from week10.engineering.models import RerankCandidate, RerankResult
from week10.engineering.reranker import DeterministicReranker


async def rerank_with_fallback(
    query: str,
    candidates: list[RerankCandidate],
    top_k: int = 5,
    timeout_ms: int = 800,
    reranker: DeterministicReranker | None = None,
) -> RerankResult:
    """精排；超时/异常则降级为首阶段顺序，并标记 degraded 供指标统计。"""
    engine = reranker if reranker is not None else DeterministicReranker()
    try:
        scored = await asyncio.wait_for(
            engine.rerank(query, candidates),
            timeout=timeout_ms / 1000,
        )
    except TimeoutError:
        return RerankResult(
            candidates=candidates[:top_k],
            degraded=True,
            reason="timeout",
        )
    except Exception as exc:  # noqa: BLE001 - 精排服务任何异常都走降级
        return RerankResult(
            candidates=candidates[:top_k],
            degraded=True,
            reason=f"error:{type(exc).__name__}",
        )

    ordered = [candidate for candidate, _ in scored[:top_k]]
    scores = {candidate.chunk_id: score for candidate, score in scored}
    return RerankResult(candidates=ordered, scores=scores)


__all__ = ["rerank_with_fallback"]
