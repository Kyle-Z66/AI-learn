"""
第 2 周 · 模型 API 原理 05：function calling（工具调用）
================================================================
【对应知识点】文档第 2 周「模型 API 原理」第 5 项：function calling

【周次学习要点】
  - function calling：先给模型一组工具的 JSON Schema 定义，模型判断该不该调用、并给出参数。
  - 流程是"模型选工具 → 返回 tool_calls → 你的代码执行函数 → 把结果作为 tool 消息回灌 → 模型总结"。
  - `tool_choice` 可强制调用某个工具 / 自动判断 / 禁止调用。

【易忽略细节 / 对照文档补足】
  1. 文档仅列名，这里补足完整调用闭环 —— 很多人只发工具定义，不回灌执行结果，对话就断了。
  2. **function calling ≠ 结构化输出**：前者让模型"选择并执行工具"（要真的去查数据库/调接口），
     后者只是强制回答符合某个 schema（见 week02/structured_output/）。两者都返回 JSON，但语义不同。
  3. 模型给的参数仍是 LLM 生成的，**必须再用 Pydantic 校验**，不能直接当可信输入。
  4. 第 3 周 P1 网关会做统一工具抽象；本周只建立基本认知。

【示例用途】可运行：`python week02/api_fundamentals/05_function_calling.py`
"""
from __future__ import annotations

import json
from typing import Any


def build_tool_schema() -> dict[str, Any]:
    """构造一个工具定义：查询指定系统的告警数。"""
    return {
        "type": "function",
        "function": {
            "name": "query_alert_count",
            "description": "查询指定系统当前未处理的告警数量",
            "parameters": {
                "type": "object",
                "properties": {
                    "system_name": {"type": "string", "description": "系统名称"},
                },
                "required": ["system_name"],
            },
        },
    }


def mock_model_decision(user_text: str, tools: list[dict[str, Any]]) -> dict[str, Any]:
    """模拟模型决定调用工具（真实场景由 API 返回 tool_calls）。"""
    if not tools or "告警" not in user_text:
        return {"content": "不需要调用工具", "tool_calls": None}
    return {
        "content": None,
        "tool_calls": [
            {
                "id": "call_1",
                "type": "function",
                "function": {
                    "name": "query_alert_count",
                    "arguments": json.dumps({"system_name": "orchestrator"}),
                },
            }
        ],
    }


def execute_tool(name: str, arguments: str) -> str:
    """按模型给出的参数执行真实函数（此处用假数据演示）。"""
    parsed = json.loads(arguments)
    if name != "query_alert_count":
        raise ValueError(f"未知工具：{name}")
    return f"{parsed['system_name']} 当前有 3 条未处理告警"


def main() -> None:
    print("=== 02 模型 API 原理 05：function calling ===")
    tools = [build_tool_schema()]
    print(f"  工具定义     : {json.dumps(tools[0], ensure_ascii=False)[:80]}...")

    decision = mock_model_decision("帮我查一下 orchestrator 的告警", tools)
    if decision["tool_calls"]:
        call = decision["tool_calls"][0]
        result = execute_tool(call["function"]["name"], call["function"]["arguments"])
        print(f"  模型给出参数 : {call['function']['arguments']}")
        print(f"  执行结果     : {result}")
        print("  下一步：把结果作为 role='tool' 的消息回灌，让模型据此生成最终回答")
    else:
        print(f"  模型直接回答 : {decision['content']}")

    print("  与结构化输出的区别：function calling 要真的执行函数；")
    print("  结构化输出只要符合 schema 的 JSON")


if __name__ == "__main__":
    main()
