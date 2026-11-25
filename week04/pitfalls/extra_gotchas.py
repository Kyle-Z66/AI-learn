"""
第 4 周 · 对照文档补足的遗漏点（严格限定第 4 周范畴）
================================================================
【对应知识点】文档第 4 周未展开、但工程实践中高频的 5 个细节：

  A. 击穿 / 穿透 / 雪崩：文档只提击穿，三者常被混为一谈。
  B. 异步生成器提前 break 要 aclose()，否则资源泄漏。
  C. SSE 心跳注释行（以 : 开头）不能当事件解析。
  D. TTL 判定用 monotonic 而非 time.time，避免系统时钟调整误判。
  E. Redis 分布式锁的完整要素（唯一值 / 过期 / 看门狗）是第 5 周内容。

【周次学习要点】
  - 与前三周 pitfalls/extra_gotchas.py 同名同定位：补足文档一笔带过的内容。
  - 这些点都能在本周其它样例找到对应实现，这里只做认知层对照。

【示例用途】可运行：`python -m week04.pitfalls.extra_gotchas`
             测试见 tests/week04/test_pitfalls.py
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

from week04.engineering.sse import SSEDecoder

CACHE_TERMS = {
    "击穿": "热点 key 过期瞬间，大量请求同时回源 → asyncio.Lock + 双重检查",
    "穿透": "查询根本不存在的数据，缓存永远不命中 → 空值缓存 / 布隆过滤器",
    "雪崩": "大量 key 同时过期 → TTL 加随机抖动，错开失效时间",
}


def demo_cache_terms() -> None:
    for name, desc in CACHE_TERMS.items():
        print(f"{name}：{desc}")


async def demo_generator_cleanup() -> None:
    """提前 break 后主动 aclose，避免生成器资源泄漏。"""

    async def numbers() -> AsyncGenerator[int, None]:
        for index in range(5):
            yield index

    generator = numbers()
    async for value in generator:
        if value == 1:
            break
    await generator.aclose()
    print("异步生成器已提前关闭（aclose）")


def demo_sse_heartbeat() -> None:
    """心跳注释行应被忽略，不产生事件。"""
    decoder = SSEDecoder()
    events = decoder.feed(": heartbeat\n\ndata: 真实内容\n\n")
    print("心跳帧被忽略，解出事件数：", len(events), "内容：", events[0].data)


if __name__ == "__main__":
    demo_cache_terms()
    asyncio.run(demo_generator_cleanup())
    demo_sse_heartbeat()
