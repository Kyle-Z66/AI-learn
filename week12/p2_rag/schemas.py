"""
第 12 周 · P2 项目：HTTP 边界模型（Pydantic）
================================================================
【对应知识点】文档第 12 周：P2 项目有 API；第 6 周请求/响应模型分离

【周次学习要点】
  - 请求模型只收 question 与 config；extra=forbid 挡住未知字段。
  - 响应模型把"答案 / 引用 / 拒答 / 守卫 / 延迟"一次给全，前端无需二次请求。
  - HTTP 模型与内部 GeneratedAnswer 分离，内部重构不破坏外部契约（第 6 周决策复用）。

【易忽略细节】
  1. refused=true 仍是 HTTP 200：业务拒答不是系统错误，不能用 5xx 表达。
  2. citations 用 list 而非 tuple 是为 JSON 序列化友好；内部模型仍保持不可变。
  3. Java 的 Bean Validation 注解对应这里的 Field 约束；但 Pydantic 在解析时
     就完成校验，不必等到 controller 里手写 if 判断。

【示例用途】被 app.py / service.py 与 tests/week12/test_p2_rag.py 引用。
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class QueryRequest(BaseModel):
    """查询请求：问题必填，配置默认 hybrid。"""

    question: str = Field(min_length=1, description="用户问题")
    config: str = Field(default="hybrid", description="检索配置名")

    model_config = ConfigDict(extra="forbid")


class CitationItem(BaseModel):
    """可点击引用：编号 + doc_id / 标题 / 页码 / 出处。"""

    number: int
    doc_id: str
    title: str
    page: int
    source: str


class QueryResponse(BaseModel):
    """查询响应：答案与可观测状态一并返回。"""

    answer: str
    citations: list[CitationItem]
    refused: bool
    guard_passed: bool
    config: str
    latency_ms: float


class MetricsResponse(BaseModel):
    """服务轻量指标：请求数 / p95 / 拒答数 / 最近配置。"""

    count: int
    p95_latency_ms: float
    refusal_count: int
    last_config: str


class EvalResponse(BaseModel):
    """评测摘要：golden set 条数 + 四配置 Recall@5，供 /eval 读取。"""

    golden_set_count: int
    configs: list[str]
    recall_at_5: list[float]
    note: str
