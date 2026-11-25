"""
第 5 周 · 核心机制 04：connect / read / total 三层超时
================================================================
【对应知识点】文档第 5 周加粗要求：必须区分三种超时

【周次学习要点】
  - connect 失败通常是网络/DNS 问题；read 失败通常是模型生成慢；total 是兜底。
  - 三层都抛 TimeoutError 的子类，上层按类型决定"重试"还是"降级"。
  - total 可以小于 connect+read 之和（显式压缩预算），但要能识别出来。

【易忽略细节】
  1. asyncio.wait_for 会取消内层任务，内层不能把 CancelledError 误包成 ReadTimeout。
  2. 非法预算（<=0）必须在发请求前校验，否则排查非常困难。
  3. 真实 SDK 的三层参数名不同，但分层的思路完全一致。

【示例用途】可运行：`python -m week05.core_mechanisms.04_timeout_layers`
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

import asyncio

from week05.engineering.timeouts import (
    ConnectTimeout,
    ReadTimeout,
    TimeoutBudget,
    TotalTimeout,
    request_with_budget,
)


async def demo() -> None:
    cases: list[tuple[str, TimeoutBudget, float, float]] = [
        ("建连超时", TimeoutBudget(0.01, 0.1, 1.0), 0.05, 0.0),
        ("读取超时", TimeoutBudget(0.1, 0.01, 1.0), 0.0, 0.05),
        ("总预算超时", TimeoutBudget(0.1, 0.1, 0.03), 0.01, 0.03),
        ("正常完成", TimeoutBudget(0.1, 0.1, 1.0), 0.01, 0.02),
    ]
    for name, budget, connect_delay, read_delay in cases:
        budget.validate()
        if budget.is_tight():
            print(f"{name}：预算偏紧（total={budget.total} < 两段之和）")
        try:
            result = await request_with_budget(budget, connect_delay, read_delay)
            print(f"{name} → 成功：{result}")
        except TimeoutError as exc:
            stage = {
                ConnectTimeout: "connect",
                ReadTimeout: "read",
                TotalTimeout: "total",
            }.get(type(exc), "unknown")
            print(f"{name} → 超时阶段={stage} 异常={type(exc).__name__}")


if __name__ == "__main__":
    asyncio.run(demo())
