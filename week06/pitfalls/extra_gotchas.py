"""
第 6 周 · 补足要点：交付形态与复盘的认知边界
================================================================
【对应知识点】文档第 6 周：README / 技术博客 / 阶段复盘 / RAG 预习

【周次学习要点】
  - 架构图画的是数据流与依赖方向，不是目录树。
  - 决策记录要回答"为什么这么选、放弃了什么、代价是什么"。
  - 覆盖率是护栏不是目标；阶段复盘要写具体短板，不能写空话。

【易忽略细节】
  1. liveness 失败要重启容器，readiness 失败只摘流量，动作不同。
  2. 行覆盖 60% 与分支覆盖 60% 不是一回事，面试时要说清口径。
  3. RAG 预习只列环节，第 7 周才实现解析与切分，别提前越界。

【示例用途】可运行：`python -m week06.pitfalls.extra_gotchas`
             测试见 tests/week06/test_pitfalls.py
"""
from __future__ import annotations

PROBES = [
    ("liveness /healthz", "进程是否存活", "不查下游", "失败 → 重启容器"),
    ("readiness /readyz", "是否可接流量", "读熔断状态", "失败 → 摘除流量"),
]

COVERAGE_KINDS = [
    ("行覆盖", "执行过的语句行 / 可执行行", "pytest-cov 默认口径"),
    ("分支覆盖", "执行过的分支 / 总分支", "需加 --cov-branch"),
]

MERMAID_SAMPLE = """Client
  → FastAPI(边界校验/追踪ID)
  → P1Gateway(第3周: 选模型+降级)
  → Provider(第2周: 三家适配器)
  → Audit/breaker/metrics(第5周)"""


def demo_probes() -> None:
    for name, question, scope, action in PROBES:
        print(f"{name:<20} | {question:<12} | {scope:<12} | {action}")


def demo_coverage_kinds() -> None:
    for name, definition, note in COVERAGE_KINDS:
        print(f"{name}：{definition}（{note}）")
    print("覆盖率说明代码跑过哪些行，不说明断言是否正确")


def demo_architecture_diagram() -> None:
    print("架构图应体现数据流：")
    print(MERMAID_SAMPLE)


def demo_rag_boundary() -> None:
    print("本周 RAG 预习只到名词级；解析 / 切分 / 嵌入实验从第 7 周开始")


def demo() -> None:
    demo_probes()
    demo_coverage_kinds()
    demo_architecture_diagram()
    demo_rag_boundary()


if __name__ == "__main__":
    demo()
