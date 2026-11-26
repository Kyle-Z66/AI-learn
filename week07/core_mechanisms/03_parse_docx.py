"""
第 7 周 · 核心机制 03：Word 解析与标题样式
================================================================
【对应知识点】文档第 7 周：Word 解析（python-docx）

【周次学习要点】
  - python-docx 用 paragraph.style.name 识别 Heading，比正则猜标题更可靠。
  - 表格需要单独遍历 tables，行内单元格用 " | " 拼成 Markdown 风格。
  - 输出仍然是同一个 Document，调用方不需要知道来源格式。

【易忽略细节】
  1. paragraphs 顺序不含表格：只看段落会把"故障码 → 处置建议"对应关系丢掉。
  2. Heading 0 对应 Title 样式，判断时要同时覆盖 Title 与 Heading。
  3. Java 侧常用 POI 逐行读；这里按"段落/表格"两类元素读，思维模型不同但目的相同。

【示例用途】可运行：`python -m week07.core_mechanisms.03_parse_docx`
             测试见 tests/week07/test_core_mechanisms.py
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from week07.engineering.fixtures import write_docx
from week07.engineering.parsers import parse_docx


def parse_generated_docx() -> tuple[str, int, list[str]]:
    """生成临时 Word 并解析，返回 (标题, 表格行数, 标题列表)。"""
    with tempfile.TemporaryDirectory() as directory:
        path = write_docx(Path(directory) / "runbook.docx")
        document = parse_docx(path)
        table_rows = sum(1 for line in document.text.splitlines() if " | " in line)
        return document.title, table_rows, document.sections


def demo() -> None:
    title, table_rows, sections = parse_generated_docx()
    print(f"解析结果：title={title} 表格行数={table_rows}")
    print("标题层级：", " / ".join(sections))
    print("提示：表格单独拼接保证字段对应关系，但会丢失与原段落的相对位置。")


if __name__ == "__main__":
    demo()
