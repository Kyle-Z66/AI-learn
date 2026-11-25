"""
第 6 周 · 工程层示范：不带端口把 P1 服务跑一遍
================================================================
【对应知识点】文档第 6 周：FastAPI 暴露 REST 接口 + 单测要求

【周次学习要点】
  - httpx.ASGITransport 直接把请求送给 ASGI app，不需要 uvicorn 监听端口。
  - 这也是 CI 里跑接口测试的标准做法：快、稳定、可并发。
  - 响应里 trace_id 可用于回查第 5 周审计记录。

【易忽略细节 / 对照文档补足】
  1. base_url 只是给 httpx 拼 URL 用，不会真的发起网络连接。
  2. 流式响应用 `aiter_text()` 逐块读，再用第 4 周 SSEDecoder 还原事件。
  3. 每次 demo 前 reset_container()，避免上次运行的审计/指标残留。

【示例用途】可运行：`python -m week06.engineering.engineering_demo`
             测试见 tests/week06/test_engineering.py
"""
from __future__ import annotations

import asyncio

from httpx import ASGITransport, AsyncClient
from week04.engineering.sse import SSEDecoder

from week06.engineering.app import create_app
from week06.engineering.dependencies import reset_container


async def demo() -> None:
    reset_container()
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        chat = await client.post(
            "/v1/chat",
            json={
                "question": "系统 cyclone 级别 2 影响 30 人",
                "user_id": "u-1024",
            },
        )
        body = chat.json()
        print(f"POST /v1/chat → {chat.status_code} provider={body['provider']} "
              f"trace={body['trace_id'][:8]}…")
        print("  answer:", body["answer"][:50])

        print("GET /healthz →", (await client.get("/healthz")).json())
        print("GET /readyz →", (await client.get("/readyz")).json())
        print("GET /metrics →", (await client.get("/metrics")).json())

        stream = await client.get(
            "/v1/chat/stream", params={"question": "运维响应示例"}
        )
        decoder = SSEDecoder()
        events: list[str] = []
        async for chunk in stream.aiter_text():
            events.extend(event.data for event in decoder.feed(chunk))
        print(f"GET /v1/chat/stream → {len(events)} 帧，末帧={events[-1]}")


if __name__ == "__main__":
    asyncio.run(demo())
