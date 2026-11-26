"""
第 11 周 · 核心机制 08：Pydantic 结构化答案
================================================================
【对应知识点】文档第 11 周：低温度 + 结构化输出（第 2 周 Pydantic schema 的落地）

【周次学习要点】
  - 答案模型只留三个字段：answer / citation_numbers / refused；少字段即少幻觉面。
  - extra="forbid" 拒绝模型擅自添加字段，避免幻觉字段悄悄进入业务数据。
  - model_validate_json() 是 Pydantic v2 入口（v1 用 parse_raw），版本别混。

【易忽略细节】
  1. 第 2 周已讲 schema 约束与校验失败回灌，这里直接复用，不重复讲 Pydantic 原理。
  2. citation_numbers 用 list[int] 且默认空列表；拒答时没有引用是合法状态。
  3. Java 用 DTO + Jackson 反序列化；Pydantic 把"类型 + 约束 + 解析"合一，
     少写一套 getter/setter，但类型注解仍是静态提示，运行时靠校验器兜底。

【示例用途】可运行：`python -m week11.core_mechanisms.08_structured_answer`
             测试见 tests/week11/test_core_mechanisms.py
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class AnswerWithCitations(BaseModel):
    """带引用的结构化答案：字段越少，模型可发挥的幻觉空间越小。"""

    answer: str = Field(description="答案正文，可含 [n] 引用标记")
    citation_numbers: list[int] = Field(default_factory=list, description="使用的引用编号")
    refused: bool = False

    model_config = ConfigDict(extra="forbid")


def validate_answer(payload: str) -> AnswerWithCitations:
    """把模型返回的 JSON 文本校验成 AnswerWithCitations。"""
    return AnswerWithCitations.model_validate_json(payload)


def demo() -> None:
    good = '{"answer":"级别为 2 级 [1]","citation_numbers":[1],"refused":false}'
    parsed = validate_answer(good)
    print("合法输出：", parsed.model_dump())

    with_extra = good[:-1] + ',"confidence":0.99}'
    try:
        validate_answer(with_extra)
    except ValidationError as exc:
        print("多余字段被拒绝：", exc.errors()[0]["type"])
    print("结论：结构化校验把幻觉字段挡在业务层之外。")


if __name__ == "__main__":
    demo()
