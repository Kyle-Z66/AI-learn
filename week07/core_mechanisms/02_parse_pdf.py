"""
第 7 周 · 核心机制 02：PDF 解析与页码保留
================================================================
【对应知识点】文档第 7 周：PDF 解析（PyMuPDF / pdfplumber）

【周次学习要点】
  - 用 pypdf 真实读取本地生成的两页 PDF，逐页抽文本并拼接换页符。
  - 页码不是装饰：切分后 Chunk.page 要靠它回查原文。
  - 解析器只做"结构保真"，不做切分，职责边界要清楚。

【易忽略细节】
  1. extract_text() 返回 None 或空串是常态，必须兜底，否则整页丢失却不报错。
  2. 不保留换页符时，跨页的条款会被拼成一句，人工看不出来源页在哪。
  3. 教学夹具用 ASCII：内置 Helvetica 字体无法可靠抽取中文，避免假象。

【示例用途】可运行：`python -m week07.core_mechanisms.02_parse_pdf`
             测试见 tests/week07/test_core_mechanisms.py
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from week07.engineering.fixtures import write_pdf
from week07.engineering.models import PAGE_SEPARATOR
from week07.engineering.parsers import parse_pdf


def parse_generated_pdf() -> tuple[str, int, int, int]:
    """生成临时 PDF 并解析，返回 (标题, 字符数, 页边界数, 标题数)。"""
    with tempfile.TemporaryDirectory() as directory:
        path = write_pdf(Path(directory) / "incident.pdf")
        document = parse_pdf(path)
        return (
            document.title,
            len(document.text),
            document.text.count(PAGE_SEPARATOR),
            len(document.sections),
        )


def demo() -> None:
    title, length, breaks, sections = parse_generated_pdf()
    print(f"解析结果：title={title} 字符数={length}")
    print(f"页边界数={breaks}（两页应为 1）抽取到的标题数={sections}")
    print("提示：真实项目应把 page 写进 Chunk，引用环节才能定位原页。")


if __name__ == "__main__":
    demo()
