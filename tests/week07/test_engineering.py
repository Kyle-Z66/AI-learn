"""
第 7 周单元测试 · 工程层：统一模型 / 真实解析 / 五种切分
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from week07.chunking_lab.corpus import build_corpus_document
from week07.engineering.chunkers import (
    estimate_tokens,
    fixed_size,
    lexical_similarity,
    lexical_tokens,
    markdown_heading,
    page_for_offset,
    recursive,
    semantic,
    small_to_big,
    token_units,
)
from week07.engineering.engineering_demo import demo
from week07.engineering.fixtures import (
    write_docx,
    write_excel,
    write_html,
    write_markdown,
    write_pdf,
)
from week07.engineering.models import PAGE_SEPARATOR, Chunk, Document
from week07.engineering.parsers import (
    document_id,
    extract_heading,
    parse_docx,
    parse_excel,
    parse_html,
    parse_markdown,
    parse_pdf,
)


def test_models_have_required_fields() -> None:
    document = Document("d1", "标题", "a.md", "正文", ["标题"], 1)
    chunk = Chunk("d1-c001", "d1", "正文", "标题", 1, "a.md", {"strategy": "fixed"})
    assert document.sections == ["标题"]
    assert chunk.metadata["strategy"] == "fixed"
    assert document_id("path/to/a.md") == "a"


def test_heading_guess() -> None:
    assert extract_heading("## 2 告警分级") is not None
    assert extract_heading("第7条 出现 ERR_4012") is not None
    assert extract_heading("普通正文句子") is None


def test_parsers_read_all_real_formats() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        pdf = parse_pdf(write_pdf(root / "a.pdf"))
        docx = parse_docx(write_docx(root / "b.docx"))
        html = parse_html(write_html(root / "c.html"))
        markdown = parse_markdown(write_markdown(root / "d.md"))
        excel = parse_excel(write_excel(root / "e.xlsx"))
    assert pdf.text.count(PAGE_SEPARATOR) == 1
    assert "ERR_4012" in docx.text
    assert "NOISE_SCRIPT" not in html.text
    assert len(markdown.sections) >= 8
    assert "ERR_4012" in excel.text
    assert "故障码" in excel.sections


def test_token_estimate_counts_cjk_per_char() -> None:
    assert estimate_tokens("系统 cyclone") == 3
    assert len(token_units("a 中")) == 3
    assert page_for_offset(Document("d", "t", "p", f"a{PAGE_SEPARATOR}b"), 2) == 2


def test_fixed_size_keeps_overlap_and_budget() -> None:
    chunks = fixed_size(build_corpus_document(), chunk_size=120, overlap=24)
    assert len(chunks) >= 5
    assert all(estimate_tokens(chunk.text) <= 120 for chunk in chunks)
    assert chunks[0].metadata["strategy"] == "fixed_size"


def test_recursive_keeps_budget() -> None:
    chunks = recursive(build_corpus_document(), chunk_size=160, overlap=16)
    assert len(chunks) >= 3
    assert all(estimate_tokens(chunk.text) <= 170 for chunk in chunks)


def test_markdown_heading_adds_title_prefix() -> None:
    chunks = markdown_heading(build_corpus_document(), chunk_size=512)
    assert len(chunks) >= 5
    assert all(chunk.title_path for chunk in chunks)
    assert any("SGCC-4012" in chunk.title_path for chunk in chunks)
    assert all(" / " in chunk.text or "\n" in chunk.text for chunk in chunks[:2])


def test_lexical_similarity_and_semantic() -> None:
    left = lexical_tokens("ERR_4012 上游连接超时")
    right = lexical_tokens("ERR_4012 检查连接池")
    assert lexical_similarity(left, right) > 0.0
    assert lexical_similarity(set(), right) == 0.0
    chunks = semantic(build_corpus_document(), chunk_size=512, threshold=0.05)
    assert len(chunks) >= 3
    assert all(chunk.metadata["strategy"] == "semantic" for chunk in chunks)


def test_small_to_big_links_parent() -> None:
    chunks = small_to_big(build_corpus_document(), small_size=120, big_size=400)
    assert len(chunks) >= 3
    for chunk in chunks:
        assert chunk.text in chunk.metadata["parent_text"]
        assert chunk.metadata["parent_chunk_id"].startswith("sgcc-runbook-c")


def test_engineering_demo_runnable() -> None:
    demo()
