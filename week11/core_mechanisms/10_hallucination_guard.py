"""
第 11 周 · 核心机制 10：预检 + 后校验组合守卫
================================================================
【对应知识点】文档第 11 周幻觉抑制：相关性预检 + 答案后校验 + 低温度结构化输出

【周次学习要点】
  - 组合守卫把三道防线收成一个入口：预检挡无关检索，后校验挡编造事实，
    低温度与 schema 降低随机性和字段幻觉。
  - 一次调用返回全部失败项，便于统一记录指标与选择"拒答 / 重检索"策略。
  - 这是第 11 周的收口样例，也是第 12 周 faithfulness 指标复用的核心函数。

【易忽略细节】
  1. 预检失败就跳过后校验：上下文无关时再校验数字没有意义，还浪费 CPU。
  2. 守卫通过 ≠ 答案正确：它只证明"答案里的可核验声明都在上下文里"，
     上下文本身错了仍然会错——这就是第 12 周要先评检索质量的原因。
  3. Java 里常用责任链模式；这里用 GuardResult.merge() 表达同样的串联语义，
     但没有接口与实现类的样板代码。

【示例用途】可运行：`python -m week11.core_mechanisms.10_hallucination_guard`
             测试见 tests/week11/test_core_mechanisms.py
"""
from __future__ import annotations

from week11.engineering.context import build_context
from week11.engineering.generator import FakeGenerator
from week11.engineering.guards import hallucination_guard
from week11.engineering.models import SourceChunk

CHUNK = SourceChunk("DOC-A", "值班规范", 1, "系统 cyclone 级别为 2 级，影响 30 名用户。")


def demo() -> None:
    bundle = build_context([CHUNK])
    generator = FakeGenerator()
    answer = generator.generate("系统 cyclone 影响多少人？", bundle)

    cases = (
        ("原答案", answer.text),
        ("篡改数字", answer.text.replace("30", "500")),
    )
    for label, text in cases:
        result = hallucination_guard(
            "系统 cyclone 影响多少人？", bundle, text, entities=("张伟",)
        )
        print(f"{label} → 通过={result.passed} 失败项={result.failed_checks}")
        print("  原因：", result.reason)

    irrelevant = generator.generate("公司火星基地的预算是多少？", bundle)
    print(f"无关问题 → 拒答={irrelevant.refused} 守卫={irrelevant.guard.passed}")


if __name__ == "__main__":
    demo()
