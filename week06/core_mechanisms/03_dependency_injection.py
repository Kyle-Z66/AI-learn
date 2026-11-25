"""
第 6 周 · 核心机制 03：Depends 依赖注入与测试替换
================================================================
【对应知识点】文档第 6 周 P1 收尾（文档未展开 DI，本工程补足）

【周次学习要点】
  - get_container() 是单例工厂；FastAPI 在每个请求里通过 Depends 注入。
  - dependency_overrides 可以在测试中换成假容器，不碰真实网关。
  - 单例必须能重置，否则测试之间会共享审计库和指标。

【易忽略细节】
  1. 覆盖依赖要在请求前设置，请求后 clear()，否则污染后续用例。
  2. 注入的是对象引用：假容器里的 metrics 会真实记录本次调用。
  3. 生产可用 lifespan 管理数据库连接，本周先用简单单例讲清原理。

【示例用途】可运行：`python -m week06.core_mechanisms.03_dependency_injection`
             测试见 tests/week06/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio

from httpx import ASGITransport, AsyncClient

from week06.engineering.app import create_app
from week06.engineering.dependencies import build_container, get_container, reset_container


async def demo() -> None:
    reset_container()
    original = get_container()
    fake = build_container()
    app = create_app()
    app.dependency_overrides[get_container] = lambda: fake

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/v1/chat", json={"question": "系统 cyclone"})
    print("请求状态：", response.status_code)
    print("默认容器 id：", id(original), "注入容器 id：", id(fake))
    print("注入容器收到请求数：", fake.metrics.snapshot().count, "（默认容器应为 0）")
    print("默认容器请求数：", original.metrics.snapshot().count)
    app.dependency_overrides.clear()


if __name__ == "__main__":
    asyncio.run(demo())
