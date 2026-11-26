"""
第 10 周 · 核心机制 06：并发批量精排（gather + Semaphore）
================================================================
【对应知识点】文档第 10 周：候选多时必须并发；第 4 周并发思维复用

【周次学习要点】
  - 每个候选一次打分， asyncio.gather 并发跑；Semaphore 限制同时在途数量。
  - gather 返回顺序与输入一致，不需要事后按下标重排。
  - 并发上限是保护 rerank 服务的闸门，不是提速越多越好。

【易忽略细节】
  1. 不设上限一次性打 100 个请求，容易把自托管 reranker 直接打爆。
  2. 打分函数必须真的 await（如 asyncio.sleep），否则并发只是假象。
  3. 异常会从 gather 冒出，交给上层 fallback 统一降级，不在批处理里吞。

【示例用途】可运行：`python -m week10.core_mechanisms.06_batch_rerank`
             测试见 tests/week10/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio

from week10.engineering.reranker import DeterministicReranker

QUERY = "SGCC-4012 巡检"
TEXTS = [
    "SGCC-4012 断路器巡检周期",
    "通用断路器巡检流程",
    "ERR_4012 通信超时排查",
    "SGCC-4012 历史工单汇总",
]


async def batch_rerank(
    query: str,
    texts: list[str],
    concurrency: int = 2,
    engine: DeterministicReranker | None = None,
) -> list[float]:
    """并发打分；结果顺序与 texts 一致，并发度由 Semaphore 控制。"""
    if concurrency < 1:
        raise ValueError("并发数必须 >= 1")
    reranker = engine if engine is not None else DeterministicReranker()
    semaphore = asyncio.Semaphore(concurrency)

    async def score_one(text: str) -> float:
        async with semaphore:
            return await reranker.score_async(query, text)

    return list(await asyncio.gather(*(score_one(text) for text in texts)))


async def demo() -> None:
    scores = await batch_rerank(QUERY, TEXTS, concurrency=2)
    for text, score in zip(TEXTS, scores, strict=True):
        print(f"  {score:.4f} :: {text}")
    print("gather 保序 + Semaphore 限流：第 4 周的并发经验直接平移")


if __name__ == "__main__":
    asyncio.run(demo())
