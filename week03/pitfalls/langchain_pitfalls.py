"""
第 3 周 · 版本陷阱与认知误区（对齐第 1 周 six_pitfalls.py 的组织形式）
================================================================
【对应知识点】文档第 3 周「版本陷阱」原文 + 本周补足的 import 三层路径与废弃清单

【周次学习要点】
  - 本周最大的坑不是语法，而是"照着 2024 年的旧博客写代码"。
  - 文档给出结论：简单 Agent 用 create_agent，复杂流程用 StateGraph，
    不要用 AgentExecutor / 旧 LLMChain / 旧 memory 类。
  - 面试加分项：能说清 harness 与 graph 的适用边界。

【易忽略细节 / 对照文档补足】
  1. 文档只给版本数字，没给判据 → 补足五维对照表。
  2. import 分三层：langchain_core（稳定契约）/ langchain（高层）/ community（社区）。
  3. Runnable 是协议，不是可实例化的类，也不是某个具体模型。
  4. 实际安装版本可能与文档基线不同，以 importlib.metadata 读到的为准。

【示例用途】可运行：`python -m week03.pitfalls.langchain_pitfalls`
             测试见 tests/week03/test_pitfalls.py
"""
from __future__ import annotations

import importlib.metadata

DEPRECATED = ["LLMChain", "AgentExecutor", "ConversationBufferMemory"]
IMPORT_LAYERS = {
    "langchain_core": "稳定契约：Runnable / PromptTemplate / OutputParser，优先从这里导入",
    "langchain": "高层封装：create_agent / init_chat_model，1.x 新范式入口",
    "langchain_community": "社区集成：第三方向量库与工具，变动频繁",
}
SELECTION_ROWS = [
    ("适用场景", "单 Agent + 工具调用，线性决策", "多节点/分支/循环/人工审批/持久化"),
    ("上手成本", "低，几行代码可用", "高，要设计状态、节点、边"),
    ("可控性", "框架托管内部循环", "自己掌控每一步流转"),
    ("对应项目", "简单问答机器人", "RPA 流程编排（第 14 周动手）"),
    ("本周动作", "只记边界，不动手", "同左，动手留到第 14 周"),
]


def demo_version() -> None:
    """读真实安装版本；文档基线 2026-10 是 1.4.6 / 1.2.16，会随时间前移。"""
    for package in ("langchain", "langchain-core", "langgraph"):
        print(f"{package}: {importlib.metadata.version(package)}")
    print("结论：以实际安装版本为准，旧教程的 import 路径大概率已失效")


def demo_import_layers() -> None:
    """三层 import 的判据。"""
    for layer, meaning in IMPORT_LAYERS.items():
        print(f"{layer:22} → {meaning}")


def demo_deprecated() -> None:
    """见到这些名字，直接判定为过期教程。"""
    print("废弃清单：", " / ".join(DEPRECATED))
    print("本周正确做法：用 init_chat_model + LCEL；Agent 相关动手留到第 13/14 周")


def demo_selection_boundary() -> None:
    """create_agent（harness）与 StateGraph 的五维对照。"""
    print(f"{'维度':<10}{'create_agent':<34}{'StateGraph'}")
    for row in SELECTION_ROWS:
        print(f"{row[0]:<10}{row[1]:<34}{row[2]}")


def demo_runnable_misconception() -> None:
    """Runnable 是协议，正确用法是包装普通函数或组合现有组件。"""
    from langchain_core.runnables import RunnableLambda, RunnableSequence

    wrapped = RunnableLambda(str.upper)
    print("RunnableLambda 包装结果类型：", type(wrapped).__name__)
    sequence = wrapped | RunnableLambda(len)
    assert isinstance(sequence, RunnableSequence)  # 管道真的构造了新对象
    print("管道组合结果类型：", type(sequence).__name__, "（真的新建了对象）")
    print("误解警示：Runnable() 不是合法用法，它是协议/抽象基类")


if __name__ == "__main__":
    demo_version()
    demo_import_layers()
    demo_deprecated()
    demo_selection_boundary()
    demo_runnable_misconception()
