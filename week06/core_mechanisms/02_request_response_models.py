"""
第 6 周 · 核心机制 02：HTTP 边界的 Pydantic 模型
================================================================
【对应知识点】文档第 6 周 REST 接口 + 第 2 周 Pydantic schema

【周次学习要点】
  - 边界模型只描述"外部看到的字段"，内部仍用第 3 周 GatewayRequest。
  - Field 约束在进网关之前拦截非法输入，省下一次无谓的 LLM 调用。
  - 响应模型显式声明，FastAPI 会过滤内部字段并生成 OpenAPI。

【易忽略细节】
  1. 第 2 周学过 Pydantic，这里不重复语法，只讲"放在哪一层"。
  2. 校验失败返回 422，不是 500；错误体由 FastAPI 统一生成。
  3. trace_id 必须回传，否则用户报障时无法反查第 5 周审计表。

【示例用途】可运行：`python -m week06.core_mechanisms.02_request_response_models`
             测试见 tests/week06/test_core_mechanisms.py
"""
from __future__ import annotations

from pydantic import ValidationError

from week06.engineering.schemas import ChatRequest, ChatResponse


def demo() -> None:
    request = ChatRequest(question="系统 cyclone 级别 2")
    print("合法请求：", request.model_dump())
    try:
        ChatRequest(question="")
    except ValidationError as exc:
        print("空问题被拦截：", exc.errors()[0]["type"], "（HTTP 422）")
    response = ChatResponse(
        answer="已抽取",
        provider="deepseek",
        latency_ms=12.5,
        cost_yuan=0.001,
        trace_id="abc123",
    )
    print("合法响应 JSON：", response.model_dump_json())


if __name__ == "__main__":
    demo()
