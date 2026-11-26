"""
第 11 周 · 核心机制 03：引用编号 [1][2] 的生成与抽取
================================================================
【对应知识点】文档第 11 周：生成时给每段编号，答案里带 [1][2]，后处理映射回原文

【周次学习要点】
  - 编号在上下文组装阶段分配一次，答案与映射表共用，不能生成后另起一套编号。
  - 抽取函数用正则取 [n]，是"答案是否真的带引用"的可测试判据。
  - 编号从 1 开始且连续，便于人工核对与报告展示。

【易忽略细节】
  1. 若先给全部检索结果编号、再按预算截断，就会出现 [3] 指向被切掉片段的漂移；
     正确顺序是"先截断、再编号"。
  2. 正则只认方括号里的整数：[1][2] 可抽取，"第 1 段"这种自由文案不可抽取。
  3. Java 用 Map<Integer, Citation>；Python 用 dict 即可，enumerate 的 start=1
     比手写 i+1 更不容易差一。

【示例用途】可运行：`python -m week11.core_mechanisms.03_citation_numbering`
             测试见 tests/week11/test_core_mechanisms.py
"""
from __future__ import annotations

import re
from collections.abc import Sequence

from week11.engineering.models import SourceChunk

CHUNKS: tuple[SourceChunk, ...] = (
    SourceChunk("DOC-A", "值班规范", 1, "系统 cyclone 级别为 2 级。"),
    SourceChunk("DOC-A", "值班规范", 2, "影响 30 名用户。"),
    SourceChunk("DOC-B", "值班手册", 9, "需在 15 分钟内响应。"),
)


def format_numbered_context(chunks: Sequence[SourceChunk]) -> str:
    """先截断后编号：返回可直接塞进 Prompt 的带编号文本。"""
    return "\n\n---\n\n".join(
        f"[{number}] {chunk.content}" for number, chunk in enumerate(chunks, start=1)
    )


def extract_citation_numbers(text: str) -> tuple[int, ...]:
    """抽取答案中出现的引用编号，按出现顺序返回（可能重复）。"""
    return tuple(int(number) for number in re.findall(r"\[(\d+)\]", text))


def demo() -> None:
    truncated = CHUNKS[:2]  # 模拟预算只放得下前两段
    context = format_numbered_context(truncated)
    print(context)
    answer = "系统 cyclone 级别为 2 级 [1]，影响 30 名用户 [2]。"
    numbers = extract_citation_numbers(answer)
    print("\n答案：", answer)
    print("引用编号：", numbers)
    print("全部编号都在截断后的上下文中：", all(n <= len(truncated) for n in numbers))


if __name__ == "__main__":
    demo()
