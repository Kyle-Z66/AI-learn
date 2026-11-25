"""
第 4 周 · 工程实现：SSE 帧编码与流式输出
================================================================
【对应知识点】文档第 4 周「流式输出」：SSE + 前端 EventSource/fetch + async 生成器 yield

【周次学习要点】
  - SSE 是单向文本流：服务端按 `data: ...\\n\\n` 逐帧推送，前端用 EventSource 或 fetch 读。
  - async 生成器用 `yield` 逐块产出，配合 `async for` 消费，是流式接口的核心写法。
  - 第 2 周讲过 streaming 的概念，本周落到"帧怎么拼、怎么拆"。

【易忽略细节 / 对照文档补足】
  1. 一帧可能跨多个 TCP 包，一个包也可能含多帧 → 必须按双换行缓冲切帧，不能一次 read 当一帧。
  2. `data:` 可以多行，解析时要拼成一个字符串，多行之间补 \\n。
  3. 注释行（以 `:` 开头）是心跳，不要当事件解析。
  4. 提前 break 消费时应对生成器调用 aclose()，否则资源不释放。

【示例用途】被 core_mechanisms/04~06 引用；测试见 tests/week04/test_engineering.py
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass


@dataclass(frozen=True)
class SSEEvent:
    """一条 SSE 事件：事件类型 + 数据 + 可选 id。"""

    data: str
    event: str = "message"
    event_id: str = ""


def encode_sse(event: SSEEvent) -> str:
    """把事件编码成标准 SSE 帧；每行以 \\n 结尾，帧间空一行。"""
    lines = []
    if event.event_id:
        lines.append(f"id: {event.event_id}")
    if event.event != "message":
        lines.append(f"event: {event.event}")
    # data 含换行时要拆成多行 data:，否则客户端解析会丢行
    for line in event.data.split("\n"):
        lines.append(f"data: {line}")
    return "\n".join(lines) + "\n\n"


class SSEDecoder:
    """增量解码器：feed() 可喂任意碎片，按双换行切出完整事件。"""

    def __init__(self) -> None:
        self._buffer = ""

    def feed(self, chunk: str) -> list[SSEEvent]:
        """追加一块文本，返回本次能完整解析出的事件列表。"""
        self._buffer += chunk
        events: list[SSEEvent] = []
        while "\n\n" in self._buffer:
            frame, self._buffer = self._buffer.split("\n\n", 1)
            event = self._parse_frame(frame)
            if event is not None:
                events.append(event)
        return events

    @staticmethod
    def _parse_frame(frame: str) -> SSEEvent | None:
        data_lines: list[str] = []
        event_type = "message"
        event_id = ""
        for line in frame.split("\n"):
            if not line or line.startswith(":"):  # 空行与心跳注释
                continue
            field, _, value = line.partition(":")
            value = value.lstrip(" ")
            if field == "data":
                data_lines.append(value)
            elif field == "event":
                event_type = value
            elif field == "id":
                event_id = value
        if not data_lines:
            return None
        return SSEEvent(data="\n".join(data_lines), event=event_type, event_id=event_id)


async def stream_tokens(text: str, chunk_size: int = 1, delay: float = 0.0) -> AsyncIterator[str]:
    """模拟模型逐字吐 token 的 async 生成器，供 SSE 层逐块编码。"""
    for start in range(0, len(text), chunk_size):
        if delay:
            await asyncio.sleep(delay)
        yield text[start : start + chunk_size]


async def sse_stream(text: str, chunk_size: int = 1, delay: float = 0.0) -> AsyncIterator[str]:
    """把逐字 token 包装成 SSE 帧字符串，可直接作为 HTTP 响应体迭代。"""
    async for token in stream_tokens(text, chunk_size, delay):
        yield encode_sse(SSEEvent(data=token))
    yield encode_sse(SSEEvent(data="[DONE]", event="end"))
