"""
第 7 周 · 工程层示范：解析五种格式并跑通五种切分
================================================================
【对应知识点】文档第 7 周：文档解析 + 切分策略实验的工程化落地

【周次学习要点】
  - 五种解析器统一返回 Document，五种切分器统一消费 Document 返回 Chunk。
  - 临时文件由 fixtures 生成，全程无网络、无 API Key、无二进制 fixture。
  - 同一份语料接不同切分器，参数集中在一处，便于复现实验。

【易忽略细节 / 对照文档补足】
  1. 文档只要求"实装解析"，未要求统一契约；没有契约就无法做公平对照。
  2. 演示里显式打印 sections/页码，方便确认结构保真而不是只看字符数。
  3. small-to-big 返回的小块数最多，不能按月默认"块多=好"。

【示例用途】可运行：`python -m week07.engineering.engineering_demo`
             测试见 tests/week07/test_engineering.py
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from week07.chunking_lab.corpus import build_corpus_document
from week07.engineering.chunkers import (
    estimate_tokens,
    fixed_size,
    markdown_heading,
    recursive,
    semantic,
    small_to_big,
)
from week07.engineering.fixtures import (
    write_docx,
    write_excel,
    write_html,
    write_markdown,
    write_pdf,
)
from week07.engineering.parsers import (
    parse_docx,
    parse_excel,
    parse_html,
    parse_markdown,
    parse_pdf,
)


def demo_parsers() -> None:
    """用真实解析器读取五种临时文件。"""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        documents = (
            parse_pdf(write_pdf(root / "demo_pdf.pdf")),
            parse_docx(write_docx(root / "demo_docx.docx")),
            parse_html(write_html(root / "demo_html.html")),
            parse_markdown(write_markdown(root / "demo_md.md")),
            parse_excel(write_excel(root / "demo_xlsx.xlsx")),
        )
        for document in documents:
            print(
                f"{document.doc_id:<10} 字符={len(document.text):>5} "
                f"标题={len(document.sections):>2} 页码={document.page}"
            )


def demo_chunkers() -> None:
    """同一语料上跑五种切分器。"""
    document = build_corpus_document()
    strategies = (
        ("固定", fixed_size(document, chunk_size=512, overlap=64)),
        ("递归", recursive(document, chunk_size=512, overlap=64)),
        ("标题", markdown_heading(document, chunk_size=512)),
        ("语义", semantic(document, chunk_size=512, threshold=0.05)),
        ("小块大返", small_to_big(document, small_size=160, big_size=512)),
    )
    for name, chunks in strategies:
        average = sum(estimate_tokens(chunk.text) for chunk in chunks) / len(chunks)
        print(f"{name:<6} chunk={len(chunks):>3} 平均token={average:>6.1f}")


def demo() -> None:
    print("== 解析五种格式 ==")
    demo_parsers()
    print("\n== 五种切分策略（同一语料）==")
    demo_chunkers()


if __name__ == "__main__":
    demo()
