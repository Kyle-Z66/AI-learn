"""
第 7 周 · 工程层：五种真实可用的文件解析器
================================================================
【对应知识点】文档第 7 周：PDF / Word / HTML / Markdown / Excel 解析

【周次学习要点】
  - 五个函数签名统一：parse_xxx(path) -> Document，调用方无需关心格式差异。
  - 每个解析器都尽量保留结构：页码、标题或工作表名，而不是只返回裸文本。
  - Excel 解析用 openpyxl（第 1 周已用），对 Java 开发者是 EasyExcel 的思维平移。

【易忽略细节 / 对照文档补足】
  1. PDF 的 extract_text() 不保证跨页连贯，必须用换页符标出边界再切分。
  2. python-docx 遍历 paragraphs 不会把表格按原位置插回文本，需单独拼接表格行。
  3. HTML 若不先移除 script/style，脚本内容会混进正文污染后续 embedding。
  4. Excel 只读模式要显式 close()，否则 Windows 上临时文件无法删除。

【示例用途】core_mechanisms/02~05 与 engineering_demo.py 直接调用；
             测试见 tests/week07/test_engineering.py
"""
from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from openpyxl import load_workbook
from pypdf import PdfReader

from week07.engineering.models import PAGE_SEPARATOR, Document

_HEADING_RE = re.compile(
    r"^(#{1,6}\s+.+|第[一二三四五六七八九十百\d]+[章节条].+|\d+(?:\.\d+)*\s+\S.+)$"
)


def document_id(path: str | Path) -> str:
    """用文件名 stem 作为稳定 doc_id，避免绝对路径进入向量库。"""
    return Path(path).stem


def extract_heading(line: str) -> str | None:
    """从一行纯文本中猜测标题；猜不出返回 None。"""
    stripped = line.strip()
    if not stripped or len(stripped) > 60:
        return None
    if _HEADING_RE.match(stripped):
        return stripped
    return None


def _build(path: str | Path, text: str, sections: list[str], page: int = 1) -> Document:
    """五个解析器共用的 Document 组装函数。"""
    titles = [section for section in sections if section]
    title = titles[0] if titles else document_id(path)
    return Document(
        doc_id=document_id(path),
        title=title,
        path=str(path),
        text=text.strip(),
        sections=titles,
        page=page,
    )


def parse_pdf(path: str | Path) -> Document:
    """逐页抽取 PDF 文本，用换页符保留页码边界。"""
    reader = PdfReader(str(path))
    page_texts: list[str] = []
    sections: list[str] = []
    for number, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        page_texts.append("\n".join(lines))
        for line in lines:
            heading = extract_heading(line)
            if heading:
                sections.append(f"第{number}页 {heading}")
    return _build(path, PAGE_SEPARATOR.join(page_texts), sections)


def parse_docx(path: str | Path) -> Document:
    """抽取 Word 段落与表格；标题样式写入 sections。"""
    document = DocxDocument(str(path))
    lines: list[str] = []
    sections: list[str] = []
    for paragraph in document.paragraphs:
        content = paragraph.text.strip()
        if not content:
            continue
        style = paragraph.style.name if paragraph.style is not None else ""
        if style.startswith("Heading") or style == "Title":
            sections.append(content)
        lines.append(content)
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                lines.append(" | ".join(cells))
    return _build(path, "\n".join(lines), sections)


def parse_html(path: str | Path) -> Document:
    """用 BeautifulSoup 去脚本后抽正文；h1~h3 作为标题层级。"""
    html = Path(path).read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    title_node = soup.find("title")
    title = title_node.get_text(strip=True) if title_node else document_id(path)
    sections = [node.get_text(" ", strip=True) for node in soup.find_all(["h1", "h2", "h3"])]
    text = soup.get_text("\n", strip=True)
    return _build(path, text, sections if sections else [title])


def parse_markdown(path: str | Path) -> Document:
    """按 Markdown 标题行抽取层级，正文原样保留。"""
    text = Path(path).read_text(encoding="utf-8")
    sections: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            section = stripped.lstrip("#").strip()
            if section:
                sections.append(section)
    return _build(path, text, sections)


def parse_excel(path: str | Path) -> Document:
    """逐工作表逐行读取，工作表名为一级结构。"""
    workbook = load_workbook(str(path), read_only=True, data_only=True)
    lines: list[str] = []
    sections: list[str] = []
    try:
        for sheet in workbook.worksheets:
            sections.append(sheet.title)
            lines.append(f"# {sheet.title}")
            for row in sheet.iter_rows(values_only=True):
                cells = ["" if cell is None else str(cell) for cell in row]
                if any(cells):
                    lines.append(" | ".join(cells))
    finally:
        workbook.close()
    return _build(path, "\n".join(lines), sections)


__all__ = [
    "document_id",
    "extract_heading",
    "parse_docx",
    "parse_excel",
    "parse_html",
    "parse_markdown",
    "parse_pdf",
]
