"""
第 12 周 · 核心机制 01：golden set 的字段结构
================================================================
【对应知识点】文档第 12 周：每条标注标准答案 + 相关文档片段 ID + metadata

【周次学习要点】
  - 四个字段缺一不可：question / answer / relevant_chunk_ids / metadata。
  - relevant_chunk_ids 用片段 ID（doc_id#p页码）而非文档 ID，保持引用粒度。
  - metadata 记录来源与标注规则，回答"评测集怎么来的"这一必问问题。

【易忽略细节】
  1. 本仓库 golden_set.json 是教学样例，不是真实业务数据；metadata 里显式声明。
  2. 换真实数据时只替换 JSON，不改评测代码——字段契约就是接口。
  3. Java 常用 Lombok 生成 getter；这里用 frozen dataclass + to_dict，
     序列化形状由代码固定，避免每个调用点各写一套 map 结构。

【示例用途】可运行：`python -m week12.core_mechanisms.01_golden_set_schema`
             测试见 tests/week12/test_core_mechanisms.py
"""
from __future__ import annotations

from week12.engineering.golden_set import golden_set_summary, load_golden_set
from week12.engineering.models import GoldenCase


def describe_case(case: GoldenCase) -> dict[str, object]:
    """把一条标注展开成可打印字段，便于人工抽检标注质量。"""
    payload = case.to_dict()
    return {
        "question": case.question,
        "answer": case.answer,
        "relevant_chunk_ids": case.relevant_chunk_ids,
        "metadata_keys": sorted(case.metadata),
        "payload_keys": sorted(payload),
    }


def demo() -> None:
    cases = load_golden_set()
    first = describe_case(cases[0])
    for key, value in first.items():
        print(f"{key}: {value}")
    print("\n评测集摘要：", golden_set_summary(cases))
    print("注意：这是教学样例；真实数据替换步骤见 p2_rag/README.md。")


if __name__ == "__main__":
    demo()
