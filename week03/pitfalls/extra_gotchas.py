"""
第 3 周 · 对照文档补足的遗漏点（严格限定第 3 周范畴）
================================================================
【对应知识点】文档第 3 周未展开、但工程实践中高频的 5 个细节：

  A. PromptTemplate 花括号转义：{ 要写 {{ }}，否则被当成变量。
  B. JsonOutputParser 返回 dict 不是 Pydantic 对象，要再 model_validate。
  C. 字符串拼接造 prompt 会失控：转义、变量注入、消息顺序全靠自己兜。
  D. Retriever 本周只认接口，向量库/切分/Rerank 属第 7~10 周。
  E. 成本单价不硬编码：厂商调价后代码要跟着改，延续第 2 周"配置外置"。

【周次学习要点】
  - 与前两周 pitfalls/extra_gotchas.py 同名同定位：补足文档一笔带过的内容。
  - 这 5 点都能在本周其它样例找到对应实现，这里只做认知层对照。

【易忽略细节】
  - B 与第 2 周「结构化输出」直接相关：Parser 只解析，校验后的对象才是业务数据。

【示例用途】可运行：`python -m week03.pitfalls.extra_gotchas`
             测试见 tests/week03/test_pitfalls.py
"""
from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from week02.structured_output.models import TicketExtract  # 复用第 2 周的 schema


def demo_brace_escape() -> None:
    """花括号转义：字面量 { } 写成 {{ }}，渲染后才是原样。"""
    prompt = ChatPromptTemplate.from_messages([
        ("human", "请输出 JSON：{{ \"ok\": true }}，问题是 {q}"),
    ])
    print("渲染结果：", prompt.format_messages(q="如何限流？")[0].content)


def demo_parser_returns_dict() -> None:
    """Parser 输出是 dict；要带校验的对象得再走一次 model_validate。"""
    from langchain_core.output_parsers import JsonOutputParser

    parser = JsonOutputParser(pydantic_object=TicketExtract)
    parsed = parser.parse('{"system_name": "isc", "severity": 3, "affected_users": 50}')
    print("parse 返回类型：", type(parsed).__name__)
    print("校验后对象：", TicketExtract.model_validate(parsed))


def demo_cost_config() -> None:
    """成本公式固定，单价从配置读；这里用示意值演示，不代表真实价格。"""
    pricing_hint = {"qwen": (0.8, 2.0), "deepseek": (0.5, 1.0)}  # 仅示意，按官网更新

    def cost(model: str, input_tokens: int, output_tokens: int) -> float:
        price_in, price_out = pricing_hint[model]
        return input_tokens / 1000 * price_in + output_tokens / 1000 * price_out

    print("示意成本：", round(cost("qwen", 1200, 300), 4))
    print("真实项目：把 pricing_hint 换成配置/环境变量，不要写死在代码里")


if __name__ == "__main__":
    demo_brace_escape()
    demo_parser_returns_dict()
    demo_cost_config()
