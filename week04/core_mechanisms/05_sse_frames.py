"""
第 4 周 · 核心机制 05：SSE 帧格式与粘包处理
================================================================
【对应知识点】文档第 4 周流式输出：SSE + 前端 EventSource / fetch 接收

【周次学习要点】
  - SSE 帧格式：`data: 内容\\n\\n`，帧间空一行；可选 `event:` / `id:` 字段。
  - 前端两种接收方式：EventSource 自动重连、只支持 GET；fetch 可读流、
    可带自定义请求头，LLM 场景多用 fetch。
  - 服务端按 async 生成器逐帧 yield，不一次性拼完整响应。

【易忽略细节】
  1. 一次网络 read 不等于一帧：可能跨包（半帧），也可能一包多帧。
     SSEDecoder.feed() 用缓冲区按双换行切帧，才是正确做法。
  2. data 含换行要拆成多行 `data:`，客户端再拼回。
  3. 以 `:` 开头的是心跳注释行，不要当事件解析。

【示例用途】可运行：`python -m week04.core_mechanisms.05_sse_frames`
             测试见 tests/week04/test_core_mechanisms.py
"""
from __future__ import annotations

import asyncio

from week04.engineering.sse import SSEDecoder, SSEEvent, encode_sse, sse_stream


def demo_encode() -> None:
    frame = encode_sse(SSEEvent(data="你好", event_id="42"))
    print("编码后的帧：", repr(frame))


def demo_fragments() -> None:
    """模拟 TCP 粘包：把两帧切成任意碎片喂给解码器。"""
    raw = encode_sse(SSEEvent(data="你")) + encode_sse(SSEEvent(data="好"))
    decoder = SSEDecoder()
    for index in range(0, len(raw), 7):  # 每 7 个字符喂一次，故意切在帧中间
        events = decoder.feed(raw[index : index + 7])
        for event in events:
            print("解出事件：", repr(event.data))


async def demo_stream() -> None:
    """模拟服务端逐字吐流：每帧都能直接作为 HTTP 响应体的一块。"""
    print("服务端流：")
    async for frame in sse_stream("你好世界", chunk_size=1, delay=0.005):
        print(repr(frame), end=" ")
    print()


if __name__ == "__main__":
    demo_encode()
    demo_fragments()
    asyncio.run(demo_stream())
