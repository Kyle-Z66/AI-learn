"""
第 7 周 · 核心机制 08：按标题层级切分
================================================================
【对应知识点】文档第 7 周：策略 C —— Markdown 标题结构 + 标题前缀

【周次学习要点】
  - 遇到标题行就 flush 当前段落，并用栈维护 "章 / 节 / 小节" 的 title_path。
  - 每个 chunk 的正文前拼上 title_path，脱离原文档也能独立检索。
  - 这是文档强调的"低成本高收益"策略：不需要模型，只靠结构。

【易忽略细节】
  1. 更深层级标题出现时要清理栈里的旧深层节点，否则 title_path 会串味。
  2. 标题本身也占 token，子块预算要减去 title_path 长度，避免超限。
  3. Word/PDF 没有 "#" 时，可回退用 Document.sections 里的标题文本识别。

【示例用途】可运行：`python -m week07.core_mechanisms.08_heading_chunking`
             测试见 tests/week07/test_core_mechanisms.py
"""
from __future__ import annotations

from week07.chunking_lab.corpus import build_corpus_document
from week07.engineering.chunkers import markdown_heading


def heading_chunk_samples() -> tuple[int, str]:
    """返回 (chunk 数, 第 2 个 chunk 的标题路径)。"""
    chunks = markdown_heading(build_corpus_document(), chunk_size=512)
    if len(chunks) < 2:
        return len(chunks), ""
    return len(chunks), chunks[1].title_path


def demo() -> None:
    count, path = heading_chunk_samples()
    print(f"标题切分：chunk 数={count}")
    print(f"第 2 个 chunk 的 title_path={path}")
    print("提示：标题前缀让每个 chunk 自带上下文，检索命中后无需回查目录。")


if __name__ == "__main__":
    demo()
