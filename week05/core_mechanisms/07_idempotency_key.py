"""
第 5 周 · 核心机制 07：幂等键与非幂等重试
================================================================
【对应知识点】文档第 5 周：写库/生成订单等非幂等操作重试要带幂等键

【周次学习要点】
  - 幂等键必须由业务身份决定：同一业务请求重试无数次都得到同一个键。
  - 用请求时间戳或随机 UUID 当键等于没做幂等，每次重试都会新建订单。
  - TTL 去重保证重复请求在有效期内返回第一次的结果。

【易忽略细节】
  1. 键要包含 scope，避免不同业务用同一 payload 撞键。
  2. 全局锁只保证单进程 single-flight；多实例要落 Redis 唯一索引。
  3. 只缓存成功结果：失败要允许重试，不能把失败永久缓存。

【示例用途】可运行：`python -m week05.core_mechanisms.07_idempotency_key`
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

import asyncio

from week05.engineering.retry import IdempotencyGuard, make_idempotency_key


async def demo() -> None:
    payload = {"user_id": "u-1", "ticket": "T-1001", "amount": 100}
    key = make_idempotency_key("order.create", payload)
    reordered = make_idempotency_key(
        "order.create",
        {"amount": 100, "ticket": "T-1001", "user_id": "u-1"},
    )
    bad_key = make_idempotency_key("order.create", {**payload, "ts": "now"})
    print("相同业务载荷得到相同键：", key == reordered)
    print("加入时间戳后变成不同键：", key != bad_key, "（错误做法）")

    now = [0.0]
    guard = IdempotencyGuard(ttl=60.0, clock=lambda: now[0])
    executed = 0

    async def create_order() -> str:
        nonlocal executed
        executed += 1
        await asyncio.sleep(0.01)
        return "order-2026-0001"

    first = await guard.run(key, create_order)
    second = await guard.run(key, create_order)
    print(f"同键两次调用：{first} / {second}，实际执行 {executed} 次，命中 {guard.hits} 次")
    now[0] = 61.0
    await guard.run(key, create_order)
    print(f"TTL 过期后再次调用，实际执行 {executed} 次")


if __name__ == "__main__":
    asyncio.run(demo())
