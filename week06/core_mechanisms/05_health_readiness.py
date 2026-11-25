"""
第 6 周 · 核心机制 05：liveness 与 readiness
================================================================
【对应知识点】文档第 6 周可交付服务（文档未提，本工程补足）

【周次学习要点】
  - liveness(/healthz)：进程还活着吗？只查自己，不查下游。
  - readiness(/readyz)：现在能接流量吗？读第 5 周熔断状态，任一 open 就返 503。
  - 容器编排按两者做不同动作：liveness 失败重启，readiness 失败摘流量。

【易忽略细节】
  1. liveness 里查数据库/模型会把下游故障放大成"无限重启"。
  2. readiness 读的是熔断器的当前状态，不需要真的发一次模型调用。
  3. 503 的 detail 带 breaker_states，排障时不用登机器看日志。

【示例用途】可运行：`python -m week06.core_mechanisms.05_health_readiness`
             测试见 tests/week06/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio

from httpx import ASGITransport, AsyncClient

from week06.engineering.app import create_app
from week06.engineering.dependencies import get_container, reset_container


async def demo() -> None:
    reset_container()
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        print("liveness：", (await client.get("/healthz")).json())
        print("readiness（正常）：", (await client.get("/readyz")).json())

        service = get_container()
        breaker = service.breakers["qwen"]
        for _ in range(breaker.config.failure_threshold):
            await breaker.record_failure()
        failed = await client.get("/readyz")
        print(f"readiness（qwen 熔断）：{failed.status_code} {failed.json()['detail']}")


if __name__ == "__main__":
    asyncio.run(demo())
