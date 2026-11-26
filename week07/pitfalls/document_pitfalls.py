"""
第 7 周 · 本周特有坑：解析与切分中悄悄丢失的信息
================================================================
【对应知识点】文档第 7 周：文档解析 + 切分策略实验

【周次学习要点】
  - 解析阶段最容易丢三样东西：页码、表格字段对应关系、标题层级。
  - 切分阶段最常见的错误是按固定长度硬切，把"第 N 条"从中间劈开。
  - 这些问题不会抛异常，只会在检索阶段表现为"明明有答案却搜不到"。

【易忽略细节】
  1. PDF 不插换页符时，跨页内容被误当成同页，引用会指向错误页码。
  2. python-docx 若只遍历 paragraphs，表格行完全消失，故障码对照表失效。
  3. 把标题从 chunk 文本里剥掉，单块检索时"这条属于哪个章节"就无从判断。
  4. 固定长度截断条款后，前半句和后半句可能分别命中，却都不足以回答问题。

【示例用途】可运行：`python -m week07.pitfalls.document_pitfalls`
             测试见 tests/week07/test_pitfalls.py
"""
from __future__ import annotations

import re

from week07.chunking_lab.corpus import CORPUS_MARKDOWN
from week07.engineering.chunkers import fixed_size
from week07.engineering.models import PAGE_SEPARATOR, Document

CLAUSE_RE = re.compile(r"第[一二三四五六七八九十百\d]+条")


def pages_preserved(text: str) -> int:
    """统计文本里保留的页边界数量。"""
    return text.count(PAGE_SEPARATOR)


def table_columns_preserved(lines: list[str]) -> int:
    """统计含表格分隔的行数；只看段落时该值为 0。"""
    return sum(1 for line in lines if " | " in line)


def starts_mid_clause(chunk_text: str) -> bool:
    """判断 chunk 是否从条款中间开始（前半条被上一块带走）。"""
    head = chunk_text.lstrip()[:16]
    return "条" in head and not head.startswith("第")


def demo_lost_page() -> None:
    with_marker = f"第一页内容{PAGE_SEPARATOR}第二页内容"
    without_marker = with_marker.replace(PAGE_SEPARATOR, "")
    print(f"保留换页符：{pages_preserved(with_marker)} 个边界；"
          f"直接拼接：{pages_preserved(without_marker)} 个边界（页码信息丢失）")


def demo_lost_table() -> None:
    paragraphs_only = ["故障码对照表如下", "ERR_4012 上游连接超时"]
    with_table = paragraphs_only + ["ERR_4012 | 检查上游健康状态"]
    print(f"只取段落：表格行={table_columns_preserved(paragraphs_only)}；"
          f"补上表格：{table_columns_preserved(with_table)}")


def demo_lost_heading() -> None:
    plain_line = "cyclone 级别 2 表示局部降级"
    titled = "2 告警分级 / 2.1 响应动作\n" + plain_line
    print("无标题块：", plain_line)
    print("有标题块：", titled.replace("\n", " ｜ "))


def demo_fixed_cuts_clause() -> None:
    document = Document(
        doc_id="clause-demo",
        title="条款",
        path="clause.md",
        text=CORPUS_MARKDOWN,
        sections=[],
        page=1,
    )
    chunks = fixed_size(document, chunk_size=120, overlap=0)
    broken = [chunk for chunk in chunks if starts_mid_clause(chunk.text)]
    print(f"固定 120 token 切出 {len(chunks)} 块，其中 {len(broken)} 块从条款中间开始")
    if broken:
        print("  示例：", broken[0].text[:40].replace("\n", " "))


def demo() -> None:
    demo_lost_page()
    demo_lost_table()
    demo_lost_heading()
    demo_fixed_cuts_clause()


if __name__ == "__main__":
    demo()
