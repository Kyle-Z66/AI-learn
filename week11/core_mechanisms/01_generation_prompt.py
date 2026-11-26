"""
第 11 周 · 核心机制 01：生成 Prompt 的角色与边界
================================================================
【对应知识点】文档第 11 周：system（严格基于上下文 + 不确定就拒答）+ context + question

【周次学习要点】
  - system 写规则，user 写证据与问题；证据用 <context> 分隔符与指令隔开。
  - 规则要写清"不得使用外部知识"与"不确定就说信息不足"，不能只写"请准确回答"。
  - 编号规则在 Prompt 里约定，后处理才能把 [n] 映射回 doc_id/标题/页码。

【易忽略细节】
  1. 第 2 周已讲过角色消息与 temperature 原理，这里只复用格式，不重复讲原理。
  2. 上下文要放在 user 消息里，且用显式分隔符：模型更不容易把证据当成新的系统指令。
  3. Java 里习惯拼一个大 String 当 prompt；Python 这里返回消息列表，
     与 OpenAI 兼容接口同形，换厂商时不用改结构。

【示例用途】可运行：`python -m week11.core_mechanisms.01_generation_prompt`
             测试见 tests/week11/test_core_mechanisms.py
"""
from __future__ import annotations

SYSTEM_PROMPT = (
    "你是企业知识库问答助手。\n"
    "1. 严格基于 <context> 中的内容回答，不得使用外部知识或常识补齐；\n"
    "2. 信息不足、上下文不相关或不确定时，明确说“信息不足”，不要猜测；\n"
    "3. 每个结论后用 [编号] 标注来源，编号对应 <context> 中的片段。\n"
)


def build_messages(question: str, context_text: str) -> list[dict[str, str]]:
    """组装两条消息：system 定规则，user 携带带编号上下文与真实问题。"""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"<context>\n{context_text}\n</context>\n\n问题：{question}",
        },
    ]


def demo() -> None:
    context = "[1] 系统 cyclone 的严重级别为 2 级，影响 30 名用户。"
    for message in build_messages("系统 cyclone 影响多少人？", context):
        print(f"--- {message['role']} ---")
        print(message["content"])
    print("提示：证据放在 user 消息并用 <context> 包裹，避免与系统指令混淆。")


if __name__ == "__main__":
    demo()
