"""
第 3 周 · 动手项目：P1 网关数据模型
================================================================
【对应知识点】文档第 3 周 P1 v0.1：统一响应对象 + 成本估算

【周次学习要点】
  - 项目层只定义网关自己的请求、调用记录与统计，复用 engineering 层的
    LLMResponse / GatewayConfig，避免把同一份结构复制两遍。
  - 统计对象为调用审计与成本对账留出接口：第 5 周会在这里接可观测能力。

【易忽略细节 / 对照文档补足】
  1. frozen dataclass 里的 list 字段仍是可变的，不要用可变默认值；
     用 field(default_factory=list)，延续第 1 周"可变默认参数"坑的教训。
  2. 文档只要求"内容/token/耗时/成本"，这里补一层调用统计，方便验收时打印。

【示例用途】被 gateway.py / __main__.py 引用，不单独运行。
             测试见 tests/week03/test_p1_gateway.py
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class GatewayRequest:
    """一次网关调用的请求参数。"""

    messages: list[dict[str, str]]
    temperature: float = 0
    max_tokens: int = 512


@dataclass(frozen=True)
class CallRecord:
    """单次调用记录：实际模型、是否成功、耗时、错误原因。"""

    provider: str
    ok: bool
    latency_ms: float
    error: str = ""


@dataclass
class GatewayStats:
    """网关运行统计：请求数、成功数、降级次数、累计成本。"""

    total: int = 0
    succeeded: int = 0
    fallback_used: int = 0
    total_cost: float = 0.0
    records: list[CallRecord] = field(default_factory=list)
