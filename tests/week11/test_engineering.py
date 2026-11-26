"""
第 11 周单元测试 · 工程层：上下文 / 守卫 / 生成器 / 引用映射
"""
from __future__ import annotations

from week11.engineering.context import (
    build_context,
    citation_from_chunk,
    citation_map,
    count_tokens,
)
from week11.engineering.engineering_demo import SAMPLE_CHUNKS, demo
from week11.engineering.generator import DEFAULT_TEMPERATURE, FakeGenerator
from week11.engineering.guards import (
    REFUSAL_TEMPLATE,
    content_terms,
    extract_answer_numbers,
    hallucination_guard,
    make_refusal,
    relevance_precheck,
    text_terms,
    verify_numbers_entities,
)
from week11.engineering.models import ContextBundle, GuardResult, SourceChunk


def test_models_and_guard_merge() -> None:
    chunk = SourceChunk("DOC-1", "标题", 2, "正文")
    citation = citation_from_chunk(1, chunk)
    assert citation.source == "DOC-1#p2" and citation.number == 1
    first = GuardResult(False, "预检失败", ("relevance",))
    second = GuardResult(True, "后校验通过")
    merged = first.merge(second)
    assert not merged.passed and merged.failed_checks == ("relevance",)


def test_token_count_and_context_bundle() -> None:
    assert count_tokens("") == 0
    assert count_tokens("abcd") == 1
    assert count_tokens("中文") == 2
    bundle = build_context(list(SAMPLE_CHUNKS), max_tokens=50)
    assert isinstance(bundle, ContextBundle)
    assert bundle.truncated and bundle.omitted_count == 2
    assert bundle.sources == ("DOC-001#p3",)
    assert bundle.sources == tuple(chunk.source for chunk in bundle.chunks)
    assert list(citation_map(bundle)) == [1]


def test_terms_and_number_extraction() -> None:
    assert "cyclone" in text_terms("系统 cyclone 级别")
    assert "多少" not in content_terms("影响多少人？")
    assert extract_answer_numbers("级别 2 [1]，影响 30 人") == ("2", "30")


def test_guards() -> None:
    bundle = build_context(list(SAMPLE_CHUNKS), max_tokens=1000)
    assert relevance_precheck("系统 cyclone 级别？", bundle).passed
    assert not relevance_precheck("公司火星基地预算？", bundle).passed
    assert verify_numbers_entities("影响 30 人 [1]", bundle.text).passed
    assert verify_numbers_entities("影响 500 人 [1]", bundle.text).failed_checks == ("500",)
    assert verify_numbers_entities("负责人李四", bundle.text, ("李四",)).failed_checks == ("李四",)
    assert REFUSAL_TEMPLATE.format(reason="x") == make_refusal("x")
    combined = hallucination_guard("系统 cyclone 级别？", bundle, "影响 30 人 [1]")
    assert combined.passed


def test_fake_generator_answer_and_refusal() -> None:
    bundle = build_context(list(SAMPLE_CHUNKS), max_tokens=1000)
    answer = FakeGenerator(temperature=DEFAULT_TEMPERATURE).generate(
        "系统 cyclone 的严重级别是多少？", bundle
    )
    assert not answer.refused and answer.guard.passed
    assert answer.text.startswith("[1]")
    assert [item.number for item in answer.citations] == [1, 2, 3]
    assert answer.temperature == DEFAULT_TEMPERATURE

    injected = FakeGenerator(refuse_on=("无证据问题",)).generate("无证据问题", bundle)
    assert injected.refused and not injected.guard.passed
    assert injected.text.startswith("信息不足")

    empty = build_context([], max_tokens=100)
    assert FakeGenerator().generate("系统 cyclone 级别？", empty).refused


def test_engineering_demo_runs() -> None:
    demo()
