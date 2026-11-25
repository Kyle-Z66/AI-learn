"""
第 5 周 · 工程层：三层超时预算（connect / read / total）
================================================================
【对应知识点】文档第 5 周加粗要求：必须区分 connect timeout / read timeout / 总超时

【周次学习要点】
  - connect 约束"建连"，read 约束"等响应体"，total 约束整个调用（含重试前置步骤）。
  - 真实 SDK 分别在传输层、读取层、调用层设置；这里用 asyncio.wait_for 模拟三层。
  - 三层的异常类型不同，上层才能决定是重试、降级还是直接报错。

【易忽略细节 / 对照文档补足】
  1. 文档只列名没有落地代码 → 这里补足预算校验与"预算偏紧"提示。
  2. asyncio.wait_for 超时都抛 TimeoutError，封装成子类才能区分发生阶段。
  3. 外层 total 超时会取消内层任务，内层要放行 CancelledError 不能被误包成 ReadTimeout。

【示例用途】被 core_mechanisms/04、pitfalls 引用；
             测试见 tests/week05/test_engineering.py
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass


class ConnectTimeout(TimeoutError):
    """建连阶段超时：通常意味着网络或 DNS 问题。"""


class ReadTimeout(TimeoutError):
    """读到响应体超时：通常是模型生成太慢。"""


class TotalTimeout(TimeoutError):
    """总预算耗尽：兜底，防止多层等待叠加后无限拖延。"""


@dataclass(frozen=True)
class TimeoutBudget:
    """三段预算，单位秒。"""

    connect: float
    read: float
    total: float

    def validate(self) -> None:
        """非法预算要在发请求前发现，否则永远超时还查不出原因。"""
        if self.connect <= 0 or self.read <= 0 or self.total <= 0:
            raise ValueError("三段超时预算都必须 > 0")

    def is_tight(self) -> bool:
        """total 小于两段预算之和：允许，但要显式确认是否刻意压缩。"""
        return self.total < self.connect + self.read


async def request_with_budget(
    budget: TimeoutBudget,
    connect_delay: float,
    read_delay: float,
    *,
    payload: str = "ok",
) -> str:
    """模拟一次请求：建连 → 读响应；外层再套总预算。"""
    budget.validate()

    async def connect() -> None:
        await asyncio.sleep(connect_delay)

    async def read() -> str:
        await asyncio.sleep(read_delay)
        return payload

    async def inner() -> str:
        try:
            await asyncio.wait_for(connect(), timeout=budget.connect)
        except TimeoutError as exc:
            raise ConnectTimeout(f"建连超过 {budget.connect}s") from exc
        try:
            return await asyncio.wait_for(read(), timeout=budget.read)
        except TimeoutError as exc:
            raise ReadTimeout(f"读取响应超过 {budget.read}s") from exc

    try:
        return await asyncio.wait_for(inner(), timeout=budget.total)
    except TimeoutError as exc:
        # 内层已包装成具体阶段，外层不再重复包装
        if isinstance(exc, (ConnectTimeout, ReadTimeout)):
            raise
        raise TotalTimeout(f"总耗时超过 {budget.total}s") from exc


__all__ = [
    "ConnectTimeout",
    "ReadTimeout",
    "TimeoutBudget",
    "TotalTimeout",
    "request_with_budget",
]
