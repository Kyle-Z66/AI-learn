"""
第 7 周单元测试 · 10 个核心机制样例函数级验证
"""
from __future__ import annotations

import importlib
from typing import Any

MODULES = (
    "01_rag_pipeline",
    "02_parse_pdf",
    "03_parse_docx",
    "04_parse_html",
    "05_parse_markdown_excel",
    "06_fixed_chunking",
    "07_recursive_chunking",
    "08_heading_chunking",
    "09_semantic_chunking",
    "10_small_to_big",
)


def load(name: str) -> Any:
    return importlib.import_module(f"week07.core_mechanisms.{name}")


def test_all_core_scripts_runnable() -> None:
    for name in MODULES:
        load(name).demo()


def test_rag_pipeline_io_shape() -> None:
    module = load("01_rag_pipeline")
    assert len(module.PIPELINE_IO) == 9
    assert module.stage_summary(0).startswith("解析：")
    assert "引用" in module.stage_summary(8)
    try:
        module.stage_summary(9)
    except IndexError:
        pass
    else:
        raise AssertionError("越界下标应抛 IndexError")


def test_pdf_parser_keeps_page_break() -> None:
    title, length, breaks, sections = load("02_parse_pdf").parse_generated_pdf()
    assert title and length > 0
    assert breaks == 1
    assert sections >= 2


def test_docx_parser_keeps_table_and_headings() -> None:
    title, table_rows, sections = load("03_parse_docx").parse_generated_docx()
    assert title
    assert table_rows >= 2
    assert "1 概述" in sections


def test_html_parser_removes_script_noise() -> None:
    title, has_noise, section_count = load("04_parse_html").parse_generated_html()
    assert "SGCC-4012" in title
    assert has_noise is False
    assert section_count >= 2


def test_markdown_and_excel_parse_pair() -> None:
    md_title, md_sections, xlsx_title, rows = load("05_parse_markdown_excel").parse_generated_pair()
    assert "SGCC-4012" in md_title
    assert md_sections >= 8
    assert "告警分级" in xlsx_title
    assert rows >= 3


def test_fixed_chunking_stats() -> None:
    count, average, ratio = load("06_fixed_chunking").fixed_chunk_stats()
    assert count >= 2
    assert 0 < average <= 512
    assert 0.0 <= ratio <= 1.0


def test_recursive_chunking_stats() -> None:
    count, average, separators = load("07_recursive_chunking").recursive_chunk_stats()
    assert count >= 2
    assert 0 < average <= 512
    assert separators >= 4


def test_heading_chunking_keeps_title_path() -> None:
    count, path = load("08_heading_chunking").heading_chunk_samples()
    assert count >= 5
    assert " / " in path or path


def test_semantic_chunking_threshold_effect() -> None:
    count, average = load("09_semantic_chunking").semantic_chunk_stats()
    assert count >= 2
    assert 0.0 <= average <= 1.0


def test_small_to_big_stats() -> None:
    count, average, parents = load("10_small_to_big").small_to_big_stats()
    assert count > parents >= 1
    assert 0 < average <= 160
