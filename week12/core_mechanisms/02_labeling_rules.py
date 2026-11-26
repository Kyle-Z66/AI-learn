"""
第 12 周 · 核心机制 02：标注规则与评测集门禁
================================================================
【对应知识点】文档第 12 周：README 说明标注标准；100 条宁少而精

【周次学习要点】
  - 规则写下来才能执行：来源、答案可核验、片段 ID、unique case_id 四项都要机器可查。
  - 标注质量决定指标可信度：垃圾标注上的 0.95 Recall 没有任何意义。
  - 门禁输出问题清单而不是布尔值，便于一次修完所有标注问题。

【易忽略细节】
  1. "答案里的数字逐字出现在相关片段"是可自动检查的粗规则；语义等价改写仍需人工抽检。
  2. case_id 唯一性保证后续能做 dev/holdout 划分与增量累加，不会重复计数。
  3. Java 常用 AssertJ 硬断言；这里返回问题清单，CI 里判断空元组即可，
     错误信息一次给全，少一轮"修一个再报下一个"。

【示例用途】可运行：`python -m week12.core_mechanisms.02_labeling_rules`
             测试见 tests/week12/test_core_mechanisms.py
"""
from __future__ import annotations

from collections import Counter

from week12.engineering.golden_set import load_golden_set, validate_golden_set
from week12.engineering.models import GoldenCase

LABELING_RULES: tuple[str, ...] = (
    "每条必须标注数据来源（教学样例也要标明，禁止冒充真实业务数据）",
    "答案中的数字与实体逐字出现在 relevant_chunk_ids 指向的片段中",
    "relevant_chunk_ids 至少 1 个，粒度为 doc_id#p页码",
    "case_id 全局唯一，便于 dev/holdout 划分与增量累加",
)


def check_label_rules(cases: list[GoldenCase]) -> tuple[str, ...]:
    """在结构校验之外追加 case_id 唯一性检查。"""
    issues = list(validate_golden_set(cases))
    ids = [case.metadata.get("case_id", "") for case in cases]
    duplicates = [key for key, count in Counter(ids).items() if count > 1]
    if duplicates:
        issues.append(f"case_id 重复 {len(duplicates)} 个")
    return tuple(issues)


def demo() -> None:
    for index, rule in enumerate(LABELING_RULES, start=1):
        print(f"规则 {index}：{rule}")
    issues = check_label_rules(load_golden_set())
    print("\n标注门禁问题数：", len(issues))
    print("结论：", issues if issues else "可直接用于评测")


if __name__ == "__main__":
    demo()
