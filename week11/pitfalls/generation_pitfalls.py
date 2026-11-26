"""
第 11 周 · 本周特有坑：生成侧四个高频翻车点
================================================================
【对应知识点】文档第 11 周：生成 Prompt / 引用溯源 / 幻觉抑制

【周次学习要点】
  - 上下文不足时模型会"补全"，工程必须把"不知道"变成显式拒答。
  - 引用编号在截断前分配会漂移；预算截断还可能把唯一证据切掉。
  - 低温度只让错误更稳定地复现，不等于不幻觉。

【易忽略细节】
  1. 后校验"通过"只说明答案里出现的声明都有证据；答案漏掉关键数字时也会通过，
     所以还要检查"该有的证据有没有进上下文"。
  2. 引用漂移不会让程序报错，只会让前端点开引用跳到错误页码，属于静默缺陷。
  3. Java 侧习惯"返回成功就往下走"；RAG 要把 refused / truncated 当作一等状态处理。

【示例用途】可运行：`python -m week11.pitfalls.generation_pitfalls`
             测试见 tests/week11/test_pitfalls.py
"""
from __future__ import annotations

from week11.engineering.context import build_context
from week11.engineering.generator import DEFAULT_TEMPERATURE, FakeGenerator
from week11.engineering.guards import verify_numbers_entities
from week11.engineering.models import SourceChunk

THIN_CHUNK = SourceChunk("DOC-A", "值班规范", 1, "系统 cyclone 级别为 2 级。")
NUMBER_CHUNK = SourceChunk("DOC-A", "值班规范", 2, "影响 30 名用户。")
THIRD_CHUNK = SourceChunk("DOC-B", "值班手册", 9, "需在 15 分钟内响应。")


def demo_fabrication_when_context_thin() -> None:
    context = THIN_CHUNK.content
    answer = "系统 cyclone 级别为 2 级，影响 500 名用户 [1]。"
    result = verify_numbers_entities(answer, context)
    print("坑 1 · 证据不足仍编造：")
    print("  上下文只有级别，答案却多了 500 人 → 后校验失败项：", result.failed_checks)


def demo_citation_drift() -> None:
    all_sources = [c.source for c in (THIN_CHUNK, NUMBER_CHUNK, THIRD_CHUNK)]
    bundle = build_context([THIN_CHUNK, NUMBER_CHUNK, THIRD_CHUNK], max_tokens=18)
    print("坑 2 · 引用编号漂移：")
    print("  截断前编号 [3] 指向：", all_sources[2])
    print("  截断后 sources：", bundle.sources)
    print("  若答案仍写 [3]，映射表查不到 → 前端引用落空；应先截断再编号。")


def demo_budget_cuts_evidence() -> None:
    question = "系统 cyclone 影响多少人？"
    bundle = build_context([THIN_CHUNK, NUMBER_CHUNK], max_tokens=18)
    answer = FakeGenerator().generate(question, bundle)
    check = verify_numbers_entities(answer.text, bundle.text)
    print("坑 3 · 预算把证据切掉：")
    print("  截断=", bundle.truncated, "答案=", answer.text)
    print(f"  后校验通过={check.passed}，但答案根本没回答人数 → 通过≠完整。")


def demo_low_temp_not_enough() -> None:
    fabricated = "系统 cyclone 影响 500 名用户 [1]。"
    result = verify_numbers_entities(fabricated, THIN_CHUNK.content)
    print("坑 4 · 低温度不等于不幻觉：")
    print(f"  temperature={DEFAULT_TEMPERATURE} 只压随机性；"
          f"编造的 500 依然被后校验拦下：{not result.passed}")


def demo() -> None:
    demo_fabrication_when_context_thin()
    demo_citation_drift()
    demo_budget_cuts_evidence()
    demo_low_temp_not_enough()


if __name__ == "__main__":
    demo()
