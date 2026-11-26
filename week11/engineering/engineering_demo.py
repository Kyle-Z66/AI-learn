"""
第 11 周 · 工程层示范：一次完整的可信生成链路
================================================================
【对应知识点】文档第 11 周：Prompt 设计 + 引用溯源 + 幻觉抑制与拒答

【周次学习要点】
  - 链路顺序：建上下文（预算/编号）→ 生成（带 [n]）→ 引用映射 → 守卫放行/拒答。
  - 截断与 cited sources 同步：上下文里没有的证据，答案里也不该出现。
  - 同一套守卫既能挡无关检索，也能挡答案里凭空多出的数字。

【易忽略细节 / 对照文档补足】
  1. 文档只给了 build_context 的写法，没说截断后 sources 怎么办 → 本示范用
     ContextBundle 把 text/sources/chunks 绑成同一份不可变快照。
  2. 拒答答案仍保留 citations 字段（可能为空），前端契约稳定，不必分支处理。
  3. 后校验失败时不要"自动改数字"蒙混过关：正确动作是拒答或重新检索。

【示例用途】可运行：`python -m week11.engineering.engineering_demo`
             测试见 tests/week11/test_engineering.py
"""
from __future__ import annotations

from week11.engineering.context import build_context
from week11.engineering.generator import DEFAULT_TEMPERATURE, FakeGenerator
from week11.engineering.guards import verify_numbers_entities
from week11.engineering.models import SourceChunk

SAMPLE_CHUNKS: tuple[SourceChunk, ...] = (
    SourceChunk(
        doc_id="DOC-001",
        title="cyclone 事件处置规范",
        page=3,
        content="系统 cyclone 的严重级别为 2 级，影响 30 名用户，需在 15 分钟内响应。",
    ),
    SourceChunk(
        doc_id="DOC-001",
        title="cyclone 事件处置规范",
        page=4,
        content="负责人为张伟，备用联系人李娜；升级路径为值班经理。",
    ),
    SourceChunk(
        doc_id="DOC-002",
        title="运维值班手册",
        page=8,
        content="值班热线 400-000-0000，工单系统入口位于内网 portal。",
    ),
)


def demo() -> None:
    bundle = build_context(list(SAMPLE_CHUNKS), max_tokens=50)
    print(f"片段 {len(SAMPLE_CHUNKS)} 个 → 入选 {len(bundle.chunks)} 个，"
          f"截断={bundle.truncated}，省略={bundle.omitted_count}")
    print("上下文：", bundle.text)
    print("cited sources：", bundle.sources)

    generator = FakeGenerator(temperature=DEFAULT_TEMPERATURE)
    answer = generator.generate("系统 cyclone 的严重级别是多少？", bundle)
    print(f"\n相关问答 → 拒答={answer.refused} 守卫={answer.guard.passed}")
    print("答案：", answer.text)
    for citation in answer.citations:
        print(f"  [{citation.number}] {citation.title} p.{citation.page} "
              f"source={citation.source}")

    refused = generator.generate("公司火星基地的预算是多少？", bundle)
    print(f"\n无关问答 → 拒答={refused.refused} 原因={refused.guard.reason}")

    tampered = answer.text.replace("30", "500")
    check = verify_numbers_entities(tampered, bundle.text, entities=("张伟",))
    print(f"\n篡改数字 30→500 → 守卫={check.passed} 失败项={check.failed_checks}")


if __name__ == "__main__":
    demo()
