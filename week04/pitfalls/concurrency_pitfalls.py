"""
第 4 周 · 本周特有坑（对齐第 1 周 six_pitfalls.py 的组织形式）
================================================================
【对应知识点】文档第 4 周三大任务的认知误区 + 文档标准写法缺陷

【周次学习要点】
  1. Token 混淆：本周 access_token 是访问凭证，第 2 周 token 是分词单位。
  2. 文档代码缺陷：_lock=None 与 get_event_loop() 都不能直接抄。
  3. 无限并发：裸 gather 会把厂商配额打满（429），必须配 Semaphore。
  4. TaskGroup 异常：要用 except* 捕获 ExceptionGroup，普通 except 无效。
  5. 安全余量过大：短有效期凭证留太大余量会退化成每次都刷新。

【易忽略细节】
  - 这些不是语法坑，而是"把 Java 可靠性经验平移到 asyncio"时的翻译坑。
  - 文档给的令牌桶写法有真实运行时错误，本工程给修正版。

【示例用途】可运行：`python -m week04.pitfalls.concurrency_pitfalls`
             测试见 tests/week04/test_pitfalls.py
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass

from week04.engineering.token_cache import MemoryBackend, TokenCache, TokenInfo

PITFALLS = [
    ("Token 混淆", "access_token（会过期的凭证）≠ LLM token（分词单位）"),
    ("文档代码缺陷", "_lock=None 会报 TypeError；get_event_loop 应换 get_running_loop"),
    ("无限并发", "裸 gather 会打满厂商 QPS → 必须配 Semaphore"),
    ("TaskGroup 异常", "要用 except* 捕获 ExceptionGroup，普通 except 抓不到"),
    ("安全余量过大", "30 秒凭证留 60 秒余量 → 每次请求都刷新"),
]


async def demo_token_confusion() -> None:
    """用同一份缓存对象说明两种 Token 的职责差异。"""
    cache = TokenCache(MemoryBackend(), safety_margin=60)
    print("access_token：", repr(TokenInfo("sk-xxx", 3600).access_token))
    print("LLM token：文本被分词后的单位，见 week02/api_fundamentals/01_tokenization.py")
    print("缓存对象：", type(cache).__name__, "只管凭证，不管分词")


def demo_rate_limiter_flaw() -> None:
    """复现文档原写法的缺陷：async with 一个 None 锁会报错。"""

    @dataclass
    class DocVersion:
        rate: float = 1.0
        _lock: asyncio.Lock = None  # type: ignore[assignment]  # 文档原写法

    broken = DocVersion()

    async def try_lock() -> None:
        async with broken._lock:  # type: ignore[attr-defined]
            pass

    try:
        asyncio.run(try_lock())
    except TypeError as exc:
        print("文档原写法报错：", type(exc).__name__, "-", exc)
    print("修正版见 engineering/rate_limiter.py：field(default_factory=asyncio.Lock)")


def demo_all_pitfalls() -> None:
    for name, desc in PITFALLS:
        print(f"{name:<16} → {desc}")


if __name__ == "__main__":
    demo_all_pitfalls()
    asyncio.run(demo_token_confusion())
    demo_rate_limiter_flaw()
