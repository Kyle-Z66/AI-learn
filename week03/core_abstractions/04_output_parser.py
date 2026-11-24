"""
第 3 周 · 核心抽象 04：OutputParser（输出解析器）
================================================================
【对应知识点】文档第 3 周「LangChain 核心抽象」第 4 项：OutputParser

【周次学习要点】
  - OutputParser 把模型的自由文本变成结构化对象，对应 Java 的反序列化 + Bean 校验。
  - 本周直接绑定第 2 周的 TicketExtract schema，不重复定义字段与约束。
  - 作为 Runnable，它能被 | 串进 LCEL 链：prompt | model | parser。

【易忽略细节】
  1. Parser 只负责"解析 + 校验"，不保证模型一定输出合法 JSON。
  2. 解析失败后的错误回灌重试仍走第 2 周 extractor.py 的逻辑，本周不重写。
  3. JsonOutputParser 返回 dict 而非 Pydantic 对象；要对象需再 model_validate。

【示例用途】可运行：`python -m week03.core_abstractions.04_output_parser`
             （复用了第 2 周模块，须从仓库根以 -m 运行；同第 2 周 pitfalls 的做法）
             测试见 tests/week03/test_core_abstractions.py
"""
from __future__ import annotations

from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from week02.structured_output.models import TicketExtract

# 复用第 2 周的 schema：这是与前两周连贯递进的关键，不要重新定义一份
parser = JsonOutputParser(pydantic_object=TicketExtract)


def demo_parse() -> None:
    """直接解析一段合法的模型输出。"""
    raw = '{"system_name": "isc", "severity": 3, "affected_users": 50}'
    parsed = parser.parse(raw)
    print("解析结果：", parsed)
    print("转 Pydantic 对象：", TicketExtract.model_validate(parsed))


def demo_chain() -> None:
    """Parser 作为 Runnable 接入 LCEL 链，LCEL 组合原理见 06_lcel_chain.py。"""
    prompt = ChatPromptTemplate.from_messages([
        ("human", "从报障文本抽取信息，只返回 JSON：{text}"),
    ])
    model = FakeListChatModel(responses=[
        '{"system_name": "cyclone", "severity": 4, "affected_users": 12}',
    ])
    chain = prompt | model | parser
    print("链式抽取：", chain.invoke({"text": "cyclone 故障，级别 4，影响 12 人"}))


if __name__ == "__main__":
    demo_parse()
    demo_chain()
