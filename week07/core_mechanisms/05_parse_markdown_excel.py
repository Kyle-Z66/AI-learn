"""
第 7 周 · 核心机制 05：Markdown 与 Excel 解析
================================================================
【对应知识点】文档第 7 周：Markdown 解析 + Excel 解析（openpyxl）

【周次学习要点】
  - Markdown 的 "#" 标题天然是层级，直接作为 sections，无需 NLP。
  - Excel 按"工作表 → 行"展开，sheet 名写入 sections，便于按表过滤。
  - 这是 Java 开发者最熟的一环：EasyExcel 的行模型可平移到 openpyxl。

【易忽略细节】
  1. Excel 单元格 None 要转空串再 join，否则 " | ".join 会抛 TypeError。
  2. read_only 模式必须 close()，Windows 临时目录清理会卡在文件句柄上。
  3. Markdown 标题行若也留在正文里，标题切分策略会重复识别，需统一次解析口径。

【示例用途】可运行：`python -m week07.core_mechanisms.05_parse_markdown_excel`
             测试见 tests/week07/test_core_mechanisms.py
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from week07.engineering.fixtures import write_excel, write_markdown
from week07.engineering.parsers import parse_excel, parse_markdown


def parse_generated_pair() -> tuple[str, int, str, int]:
    """生成临时 Markdown 与 Excel，返回 (MD标题, MD标题数, Excel标题, 表行数)。"""
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        markdown = parse_markdown(write_markdown(root / "runbook.md"))
        excel = parse_excel(write_excel(root / "incidents.xlsx"))
        excel_rows = sum(1 for line in excel.text.splitlines() if " | " in line)
        return markdown.title, len(markdown.sections), excel.title, excel_rows


def demo() -> None:
    md_title, md_sections, xlsx_title, rows = parse_generated_pair()
    print(f"Markdown：title={md_title} 标题数={md_sections}")
    print(f"Excel：    title={xlsx_title} 表格行数={rows}")
    print("提示：Excel 的表头行也是数据，后续切分时不要把它误判为正文段落。")


if __name__ == "__main__":
    demo()
