"""
第 3 周 · 核心抽象 03：PromptTemplate（提示模板）
================================================================
【对应知识点】文档第 3 周「LangChain 核心抽象」第 3 项：PromptTemplate

【周次学习要点】
  - PromptTemplate 把变量渲染成消息模板，是第 2 周「Prompt 工程」的框架化形态。
  - from_messages 接收 (role, template) 元组列表，直接产出系统/用户消息。
  - 渲染后得到的仍是 Message 列表，可以无缝喂给 ChatModel —— 这就是可组合性。

【易忽略细节】
  1. 模板里字面量花括号要写 {{ }} 转义，否则被当成变量名导致 KeyError。
  2. 别用字符串拼接造 prompt：转义、变量注入、消息顺序都会失控。
  3. 单变量模板可用 from_template；多角色对话必须用 from_messages。

【示例用途】可运行：`python week03/core_abstractions/03_prompt_template.py`
             测试见 tests/week03/test_core_abstractions.py
"""
from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


def build_chat_prompt() -> ChatPromptTemplate:
    """系统消息固定职责，用户消息带变量；JSON 示例中的花括号需转义。"""
    return ChatPromptTemplate.from_messages([
        ("system", "你是{system_name}的运维助手，只回答相关问题。"),
        ("human", "问题：{question}。请按 {{ \"ok\": true }} 的格式回答。"),
    ])


def demo() -> None:
    """渲染模板，观察变量替换与花括号转义的结果。"""
    prompt = build_chat_prompt()
    messages = prompt.format_messages(system_name="cyclone", question="网关如何限流？")
    for message in messages:
        print(f"[{message.type}] {message.content}")

    # 单变量场景的简写；input_variables 是调试时最常用的自检属性
    simple = PromptTemplate.from_template("请总结：{text}")
    print("input_variables:", simple.input_variables)
    print("rendered:", simple.format(text="LangChain 的 Five abstractions"))


if __name__ == "__main__":
    demo()
