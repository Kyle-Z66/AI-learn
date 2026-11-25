"""
第 6 周 · 工程层：HTTP 边界的请求/响应模型
================================================================
【对应知识点】文档第 6 周 P1 收尾：FastAPI 暴露 REST 接口

【周次学习要点】
  - HTTP 层只定义"外部看到的形状"，内部仍用第 3 周 GatewayRequest / LLMResponse。
  - Pydantic v2 在边界做校验（第 2 周已学），错误由 FastAPI 统一返回 422。
  - 响应模型显式声明，OpenAPI 文档自动可用，避免把内部对象直接吐出去。

【易忽略细节 / 对照文档补足】
  1. 文档只说"暴露 REST 接口"，没说请求/响应要与内部模型分离；这里分离避免内部重构破坏 API。
  2. Field 约束放在边界：question 为空直接 422，不会浪费一次 LLM 调用。
  3. trace_id 返回给调用方，方便用户报障时直接查第 5 周审计表。

【示例用途】被 app.py / core_mechanisms/02 引用；测试见 tests/week06/test_engineering.py
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """对外的聊天请求；只暴露业务字段，不暴露模型/温度等内部参数。"""

    question: str = Field(min_length=1, max_length=2000)
    user_id: str = Field(default="anonymous", max_length=64)
    scenario: str = Field(default="ticket_extract", max_length=64)


class ChatResponse(BaseModel):
    """对外的聊天响应：答案 + 计量信息 + 链路追踪 ID。"""

    answer: str
    provider: str
    latency_ms: float
    cost_yuan: float
    trace_id: str


class HealthResponse(BaseModel):
    """存活/就绪探测响应；就绪态带各 provider 熔断状态。"""

    status: str
    breaker_states: dict[str, str] = Field(default_factory=dict)


class MetricsResponse(BaseModel):
    """指标快照的对外形态（与第 5 周 MetricsSnapshot 字段一一对应）。"""

    count: int
    success_rate: float
    p95_latency_ms: float
    error_429_ratio: float
    total_tokens: int
    cache_hit_rate: float


__all__ = ["ChatRequest", "ChatResponse", "HealthResponse", "MetricsResponse"]
