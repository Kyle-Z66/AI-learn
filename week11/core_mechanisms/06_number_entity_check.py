"""
第 11 周 · 核心机制 06：关键数字与实体后校验
================================================================
【对应知识点】文档第 11 周幻觉抑制②：答案后校验（数字/实体是否出现在 context）

【周次学习要点】
  - 抽取答案里的业务数字与指定实体，逐条回查上下文，命中率即粗粒度事实一致性。
  - [1][2] 引用编号必须先剔除，否则引用本身会被当成"编造的数字"。
  - 失败项是具体字符串（如 500、李四），可直接进日志与报告，解释性强。

【易忽略细节】
  1. 数字用完整数字边界匹配："3" 不应被 "30" 命中；实体用子串匹配。
  2. 这是粗实现：改写、同义替换、上下文里没有但正确的常识都会被误判，
     所以它定位为"护栏"而非"裁判"，结果要人工抽检。
  3. 实体清单由业务给出（人名/系统名/产品名），不要试图从答案里自动猜实体，
     否则中文无空格会带来大量噪声。

【示例用途】可运行：`python -m week11.core_mechanisms.06_number_entity_check`
             测试见 tests/week11/test_core_mechanisms.py
"""
from __future__ import annotations

from week11.engineering.guards import extract_answer_numbers, verify_numbers_entities

CONTEXT = "系统 cyclone 的严重级别为 2 级，影响 30 名用户，负责人为张伟。"


def demo() -> None:
    answers = (
        "系统 cyclone 级别为 2 级，影响 30 名用户，负责人张伟 [1]。",
        "系统 cyclone 级别为 5 级，影响 500 名用户，负责人李四 [1]。",
    )
    for answer in answers:
        result = verify_numbers_entities(answer, CONTEXT, entities=("张伟", "李四"))
        print("答案：", answer)
        print("  数字：", extract_answer_numbers(answer))
        print(f"  通过={result.passed} 失败项={result.failed_checks} 原因={result.reason}")


if __name__ == "__main__":
    demo()
