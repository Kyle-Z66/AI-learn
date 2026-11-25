"""
第 6 周 · 核心机制 04：StreamingResponse 接 SSE 生成器
================================================================
【对应知识点】文档第 6 周 REST 接口 + 第 4 周 SSE 流式

【周次学习要点】
  - StreamingResponse 接 async 生成器，每 yield 一帧就发一帧，不先攒完整内容。
  - 复用第 4 周 encode_sse()，HTTP 层只负责传输，不重新拼帧格式。
  - media_type="text/event-stream" 让浏览器 EventSource 能直接接。

【易忽略细节】
  1. 生成器里用 await asyncio.sleep 让出事件循环；用 time.sleep 会阻塞其他请求。
  2. 客户端用 aiter_text() 逐块读，再用 SSEDecoder 处理粘包。
  3. done 事件是应用约定，SSE 协议本身没有"结束"字段。

【示例用途】可运行：`python -m week06.core_mechanisms.04_streaming_response`
             测试见 tests/week06/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio

from httpx import ASGITransport, AsyncClient
from week04.engineering.sse import SSEDecoder

from week06.engineering.app import create_app


async def demo() -> None:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/v1/chat/stream", params={"question": "流式响应示例"}
        )
        decoder = SSEDecoder()
        received: list[str] = []
        async for chunk in response.aiter_text():
            received.extend(event.data for event in decoder.feed(chunk))
    print("Content-Type：", response.headers["content-type"])
    print(f"收到 {len(received)} 帧：", received)


if __name__ == "__main__":
    asyncio.run(demo())
