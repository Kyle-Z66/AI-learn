"""
第 7 周 · 工程层：本地临时文件夹具
================================================================
【对应知识点】文档第 7 周：解析样例必须真实读文件，但不能依赖外链

【周次学习要点】
  - 夹具在 tempfile 目录里生成 PDF/Word/HTML/Markdown/Excel，再交给真实解析器读回。
  - PDF 用最小合法结构手写字节流，避免引入二进制 fixture 或额外绘图依赖。
  - 不用网络、不用 API Key，测试与离线环境都能跑。

【易忽略细节 / 对照文档补足】
  1. PDF 文本流只放 ASCII，Helvetica 内置字体无法可靠映射中文，避免抽出乱码。
  2. Word 表格行用 " | " 拼接，与 Markdown 表格保持同一视觉结构，便于对比。
  3. Excel 保存前关闭 workbook，Windows 下文件句柄不释放会导致临时目录清理失败。

【示例用途】core_mechanisms/02~05、engineering_demo.py 与测试共用
"""
from __future__ import annotations

from pathlib import Path

from docx import Document as DocxWriter
from openpyxl import Workbook

from week07.chunking_lab.corpus import CORPUS_MARKDOWN, build_corpus_document
from week07.engineering.models import Document

PDF_PAGES: tuple[tuple[str, ...], ...] = (
    (
        "SGCC-4012 Gateway Runbook",
        "1 Scope",
        "Clause 1 This runbook covers deployment and rollback.",
        "Clause 2 ERR_4012 means upstream connection timeout.",
    ),
    (
        "2 Alert Levels",
        "Clause 3 cyclone level 2 needs a response in 30 minutes.",
        "Clause 4 level 3 starts the oncall escalation immediately.",
        "SGCC-4012 and ERR_4012 are the key identifiers.",
    ),
)


def _escape_pdf_text(text: str) -> str:
    """转义 PDF 内容流里的括号与反斜杠。"""
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _content_stream(lines: tuple[str, ...] | list[str]) -> str:
    parts = ["BT", "/F1 12 Tf", "72 720 Td"]
    for line in lines:
        parts.append(f"({_escape_pdf_text(line)}) Tj")
        parts.append("0 -18 Td")
    parts.append("ET")
    return "\n".join(parts) + "\n"


def pdf_bytes(pages: tuple[tuple[str, ...], ...] = PDF_PAGES) -> bytes:
    """拼出最小可用的多页 PDF：目录 + 页树 + 每页内容 + 字体。"""
    count = len(pages)
    font_number = 3 + 2 * count
    kids = " ".join(f"{3 + 2 * index} 0 R" for index in range(count))
    objects: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {count} >>".encode("ascii"),
    ]
    for lines in pages:
        stream = _content_stream(lines)
        page_number = len(objects) + 1
        content_number = page_number + 1
        objects.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 {font_number} 0 R >> >> "
            f"/Contents {content_number} 0 R >>".encode("ascii")
        )
        objects.append(
            f"<< /Length {len(stream)} >>\nstream\n{stream}endstream".encode("ascii")
        )
    objects.append(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    )

    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets: list[int] = []
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{number} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")
    xref_position = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_position}\n%%EOF\n".encode("ascii")
    )
    return bytes(output)


def write_pdf(path: str | Path, pages: tuple[tuple[str, ...], ...] = PDF_PAGES) -> Path:
    """把最小 PDF 写到临时路径并返回该路径。"""
    target = Path(path)
    target.write_bytes(pdf_bytes(pages))
    return target


def write_docx(path: str | Path) -> Path:
    """生成含标题与表格的 Word 文件。"""
    target = Path(path)
    document = DocxWriter()
    document.add_heading("SGCC-4012 网关运维手册", level=0)
    document.add_heading("1 概述", level=1)
    document.add_paragraph("第1条 本规范适用于 SGCC-4012 网关的部署与回滚。")
    document.add_heading("2 故障码", level=1)
    document.add_paragraph("ERR_4012 表示上游连接超时。")
    table = document.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "故障码"
    table.cell(0, 1).text = "处置建议"
    table.cell(1, 0).text = "ERR_4012"
    table.cell(1, 1).text = "检查上游健康状态"
    document.save(str(target))
    return target


def write_html(path: str | Path) -> Path:
    """生成含 script 噪声、h1/h2 与表格的 HTML。"""
    target = Path(path)
    target.write_text(
        """<html><head><title>SGCC-4012 故障手册</title>
<script>NOISE_SCRIPT_SHOULD_BE_REMOVED</script></head>
<body><h1>SGCC-4012 网关</h1><p>第1条 适用范围。</p>
<h2>故障码</h2><p>ERR_4012 上游连接超时。</p>
<table><tr><td>ERR_4012</td><td>检查连接池</td></tr></table>
</body></html>""",
        encoding="utf-8",
    )
    return target


def write_markdown(path: str | Path) -> Path:
    """把内置语料写盘，供 parse_markdown 真实读取。"""
    target = Path(path)
    target.write_text(CORPUS_MARKDOWN, encoding="utf-8")
    return target


def write_excel(path: str | Path) -> Path:
    """生成含两个工作表的 Excel，验证 sheet 名也被保留。"""
    target = Path(path)
    workbook = Workbook()
    alerts = workbook.active
    alerts.title = "告警分级"
    alerts.append(["级别", "响应时限", "说明"])
    alerts.append(["cyclone-2", "30分钟", "局部降级"])
    alerts.append(["cyclone-3", "立即", "核心链路受损"])
    codes = workbook.create_sheet("故障码")
    codes.append(["故障码", "处置建议"])
    codes.append(["ERR_4012", "检查上游健康状态"])
    workbook.save(str(target))
    workbook.close()
    return target


def sample_document() -> Document:
    """直接返回内置语料的 Document，省去一次磁盘往返。"""
    return build_corpus_document()


__all__ = [
    "PDF_PAGES",
    "pdf_bytes",
    "sample_document",
    "write_docx",
    "write_excel",
    "write_html",
    "write_markdown",
    "write_pdf",
]
