"""
第 11 周 · 核心机制 09：引用编号映射回 doc_id / 标题 / 页码
================================================================
【对应知识点】文档第 11 周：后处理把 [1][2] 映射回原文

【周次学习要点】
  - 映射表在上下文组装时生成：编号 → Citation(doc_id, title, page, source)。
  - 答案里的 [n] 只负责"指路"，真正的出处信息在映射表里，前端据此渲染可点击引用。
  - 未被答案使用的编号不应出现在最终引用列表里，避免"参考文献堆砌"。

【易忽略细节】
  1. 编号越界（答案写 [9] 但只有 2 段）必须被过滤或报警，不能 KeyError 打崩服务。
  2. source 从 SourceChunk 派生，不另存一份：页码改动后引用自动跟着变。
  3. Java 常用 LinkedHashMap 保序；Python dict 3.7+ 天然有序，
     这里再按答案里编号的出现顺序取值，展示顺序与正文一致。

【示例用途】可运行：`python -m week11.core_mechanisms.09_citation_mapping`
             测试见 tests/week11/test_core_mechanisms.py
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence

from week11.engineering.context import build_context, citation_map
from week11.engineering.models import Citation, SourceChunk

CHUNKS: tuple[SourceChunk, ...] = (
    SourceChunk("DOC-A", "值班规范", 3, "系统 cyclone 级别为 2 级。"),
    SourceChunk("DOC-A", "值班规范", 4, "影响 30 名用户。"),
)


def map_citation_numbers(
    numbers: Iterable[int],
    chunks: Sequence[SourceChunk],
) -> tuple[Citation, ...]:
    """按答案中编号出现顺序映射；越界编号静默忽略，保证服务不崩。"""
    mapping = citation_map(build_context(list(chunks)))
    return tuple(mapping[number] for number in numbers if number in mapping)


def demo() -> None:
    answer = "系统 cyclone 级别为 2 级 [1]，影响 30 名用户 [2]，另见 [9]。"
    numbers = [1, 2, 9]
    print("答案：", answer)
    for citation in map_citation_numbers(numbers, CHUNKS):
        print(f"[{citation.number}] → {citation.doc_id} / {citation.title} "
              f"/ p.{citation.page} / {citation.source}")
    print("\n[9] 越界被忽略：答案里的引用必须能回到入选上下文。")


if __name__ == "__main__":
    demo()
