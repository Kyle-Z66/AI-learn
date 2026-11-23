"""
第 2 周 · 模型 API 原理 02：上下文窗口（Context Window）
================================================================
【对应知识点】文档第 2 周「模型 API 原理」第 2 项：上下文窗口

【周次学习要点】
  - 上下文窗口 = 单次请求能容纳的 token 上限，**输入 + 输出共享同一个窗口**。
  - 请求时给 `max_tokens`（输出上限），必须为输出预留空间，否则输入把窗口占满会导致错误或截断。
  - 长对话要做裁剪：保留 system 指令 + 最近的对话，丢弃过早的历史。

【易忽略细节 / 对照文档补足】
  1. 文档仅列名，这里补足"输入+输出共享"这一最容易踩的坑。
  2. 各厂商标称的上下文长度会变，代码里不要写死具体数字（与第 1 周"配置外置"一致）。
  3. 超出窗口不一定报错：有的模型会静默截断前文，导致"模型忘了刚才说什么"。
  4. 裁剪历史时不能把 assistant 的回复单独丢掉，否则对话角色序列会断裂。

【示例用途】可运行：`python week02/api_fundamentals/02_context_window.py`
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Message:
    """一条对话消息：role 取 system / user / assistant。"""

    role: str
    content: str


@dataclass(frozen=True)
class ContextWindow:
    """上下文窗口配置。max_tokens 为本模型总窗口（输入+输出共享）。"""

    max_tokens: int


def count_tokens(messages: list[Message]) -> int:
    """粗略估算消息列表的 token 数（沿用 01_tokenization.py 的思路）。"""
    return sum(len(m.content) // 2 + 1 for m in messages)


def can_fit(window: ContextWindow, messages: list[Message], reserve_output: int) -> bool:
    """判断输入 + 预留输出是否仍在窗口内。"""
    return count_tokens(messages) + reserve_output <= window.max_tokens


def trim_messages(messages: list[Message], token_limit: int) -> list[Message]:
    """裁剪历史：system 永远保留，其余从最新往前留，直到接近上限。

    从尾部保留而非头部，是因为最近的对话对当前轮次最有价值。
    """
    system_msgs = [m for m in messages if m.role == "system"]
    history = [m for m in messages if m.role != "system"]

    kept: list[Message] = []
    for msg in reversed(history):
        candidate = [msg, *kept]
        if count_tokens(system_msgs + candidate) > token_limit:
            break
        kept = candidate
    return system_msgs + kept


def main() -> None:
    print("=== 02 模型 API 原理 02：上下文窗口 ===")
    window = ContextWindow(max_tokens=100)

    messages = [
        Message("system", "你是技术文档抽取助手"),
        Message("user", "请抽取系统名和严重级别"),
        Message("assistant", "好的，请提供文档"),
        Message("user", "系统 A 故障，级别 3，影响 100 人"),
    ]
    print(f"  当前输入估算      : {count_tokens(messages)} token / 窗口 {window.max_tokens}")
    print(f"  预留 30 输出后能装 : {can_fit(window, messages, reserve_output=30)}")

    trimmed = trim_messages(messages, token_limit=60)
    print(f"  裁剪后保留消息数  : {len(trimmed)}（原 {len(messages)}）")
    for m in trimmed:
        print(f"    [{m.role}] {m.content}")
    print("  system 指令必须保留；历史从最近往前丢，避免模型丢失当前上下文")


if __name__ == "__main__":
    main()
