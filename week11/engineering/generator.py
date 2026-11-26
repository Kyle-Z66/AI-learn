"""
第 11 周 · 工程层：FakeGenerator（确定性生成，不接任何 API Key / 网络）
================================================================
【对应知识点】文档第 11 周：生成 Prompt + 引用编号 + 上下文不足时明确拒答

【周次学习要点】
  - 生成器只做一件事：把入选片段原文拼成带 [n] 的答案，因此结果可复现、可断言。
  - 相关性预检失败或显式注入无证据问题时返回统一拒答文案，不编造内容。
  - 温度作为字段保留在结果里，提醒"低温度 + 结构化输出"仍需后校验兜底。

【易忽略细节】
  1. 这是教学替身，不是真实 LLM：真实实现要把 system/user 消息送进模型，
     再对返回做同样的守卫；异常处理与重试在第 2/3 周已讲，此处不重复。
  2. Java 里常用 Mock 框架随机造返回；这里用确定性拼装，测试可以精确断言每个 [n]。
  3. refuse_on 是"可注入无证据问题"的钩子，便于实验台稳定复现拒答分支，
     不把它做成全局变量，避免测试之间互相污染。

【示例用途】被 answer_lab/__main__.py / p2_rag/generation.py / core_mechanisms 05、07 引用；
             测试见 tests/week11/test_engineering.py
"""
from __future__ import annotations

from week11.engineering.context import citation_map
from week11.engineering.guards import (
    hallucination_guard,
    make_refusal,
    relevance_precheck,
)
from week11.engineering.models import ContextBundle, GeneratedAnswer

DEFAULT_TEMPERATURE = 0.1


class FakeGenerator:
    """确定性生成器：答案逐字来自上下文，天然带引用，便于验证守卫逻辑。"""

    def __init__(
        self,
        temperature: float = DEFAULT_TEMPERATURE,
        refuse_on: tuple[str, ...] = (),
    ) -> None:
        self.temperature = temperature
        self.refuse_on = refuse_on

    @staticmethod
    def _compose(context: ContextBundle) -> str:
        """把每个入选片段原文接在 [n] 后面；不引入任何上下文之外的事实。"""
        parts = [
            f"[{number}] {chunk.content.strip().rstrip('。')}"
            for number, chunk in enumerate(context.chunks, start=1)
        ]
        return "；".join(parts) + "。"

    def generate(self, question: str, context: ContextBundle) -> GeneratedAnswer:
        """生成答案：先判拒答条件，再拼装带引用答案，最后统一过一遍组合守卫。"""
        refuse_reason = ""
        if question in self.refuse_on:
            refuse_reason = "问题被显式标记为无证据（实验注入）"
        elif not relevance_precheck(question, context).passed:
            refuse_reason = "检索结果与问题不相关"

        text = make_refusal(refuse_reason) if refuse_reason else self._compose(context)
        guard = hallucination_guard(question, context, text)
        return GeneratedAnswer(
            text=text,
            citations=tuple(citation_map(context).values()),
            refused=bool(refuse_reason),
            guard=guard,
            temperature=self.temperature,
        )
