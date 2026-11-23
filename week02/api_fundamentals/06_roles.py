"""
第 2 周 · 模型 API 原理 06：system / user / assistant 角色
================================================================
【对应知识点】文档第 2 周「模型 API 原理」第 6 项：system/user/assistant 角色

【周次学习要点】
  - system：全局指令与行为约束，优先级最高，整段对话只放一条（放最前）。
  - user：用户输入；assistant：模型历史回复。多轮对话就是把二者交替追加进 messages。
  - messages 是按时间顺序排列的列表，顺序错乱会让模型困惑。

【易忽略细节 / 对照文档补足】
  1. 文档仅列名，这里补足多轮对话的拼装方式 —— 后续所有客户端都依赖这个结构。
  2. system 里放"输出格式要求"仍不够可靠，必须配合 schema 约束（见 structured_output/）。
  3. 工具调用回灌时用 role="tool"，不是 user —— 详见 05_function_calling.py。
  4. 不要把整段历史原文塞进每一轮 user 消息，应作为独立 message 追加
     （复用 02_context_window.py 的裁剪）。

【示例用途】可运行：`python week02/api_fundamentals/06_roles.py`
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    """与 02_context_window.py 中的定义一致。

    数字前缀的脚本无法用 import 语句直接导入（Python 语法限制），
    因此每个知识点脚本保持自包含 —— 这也是第 1 周样例的约定。
    """

    role: str
    content: str


def build_messages(system: str, history: list[Message], user_input: str) -> list[Message]:
    """拼装多轮对话 messages：system 在最前，历史按序，本轮 user 在最后。"""
    return [
        Message("system", system),
        *history,
        Message("user", user_input),
    ]


def describe_roles(messages: list[Message]) -> None:
    for i, msg in enumerate(messages):
        role_note = {
            "system": "全局指令（优先级最高）",
            "user": "用户输入",
            "assistant": "模型历史回复",
            "tool": "工具执行结果回灌",
        }.get(msg.role, "未知角色")
        print(f"    [{i}] {msg.role:<9} {role_note:<16} | {msg.content}")


def main() -> None:
    print("=== 02 模型 API 原理 06：消息角色 ===")
    history = [
        Message("user", "从这段文本抽取系统名"),
        Message("assistant", "请提供技术文档内容"),
    ]
    messages = build_messages(
        system="你是技术文档信息抽取助手，只输出 JSON，不要解释",
        history=history,
        user_input="orchestrator 网关响应超时，级别 4",
    )
    describe_roles(messages)
    print("  system 只放一条且必须在最前；历史 user/assistant 交替；本轮 user 在末尾")
    print("  这正是后续 ChatClient.chat(messages=...) 的入参结构（第 1 周 Protocol 模式的复用）")


if __name__ == "__main__":
    main()
