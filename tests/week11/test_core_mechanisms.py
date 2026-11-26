"""
第 11 周单元测试 · 10 个核心机制样例均可运行 + 函数级逻辑
"""
from __future__ import annotations

import importlib
import inspect
from typing import Any

import pytest
from pydantic import ValidationError
from week11.engineering.context import build_context
from week11.engineering.generator import DEFAULT_TEMPERATURE
from week11.engineering.guards import (
    hallucination_guard,
    make_refusal,
    relevance_precheck,
    verify_numbers_entities,
)
from week11.engineering.models import SourceChunk

MODULES = (
    "01_generation_prompt",
    "02_context_budget",
    "03_citation_numbering",
    "04_relevance_precheck",
    "05_refusal_template",
    "06_number_entity_check",
    "07_low_temperature",
    "08_structured_answer",
    "09_citation_mapping",
    "10_hallucination_guard",
)


def load(name: str) -> Any:
    return importlib.import_module(f"week11.core_mechanisms.{name}")


async def test_all_core_scripts_runnable() -> None:
    for name in MODULES:
        result: Any = load(name).demo()
        if inspect.isawaitable(result):
            await result


def test_generation_prompt_messages() -> None:
    module = load("01_generation_prompt")
    messages = module.build_messages("问题？", "[1] 证据")
    assert [message["role"] for message in messages] == ["system", "user"]
    assert "严格基于" in messages[0]["content"]
    assert "不确定" in messages[0]["content"]
    assert "<context>" in messages[1]["content"] and "问题？" in messages[1]["content"]


def test_context_budget_truncates_and_syncs() -> None:
    module = load("02_context_budget")
    full = build_context(list(module.CHUNKS), max_tokens=1000)
    tight = build_context(list(module.CHUNKS), max_tokens=25)
    assert not full.truncated and len(full.sources) == 3
    assert tight.truncated and len(tight.chunks) == 1
    assert tight.sources == (module.CHUNKS[0].source,)
    assert "[2]" not in tight.text
    assert module.count_tokens("") == 0


def test_citation_numbering_and_extraction() -> None:
    module = load("03_citation_numbering")
    text = module.format_numbered_context(module.CHUNKS[:2])
    assert text.startswith("[1]") and "[2]" in text and "[3]" not in text
    assert module.extract_citation_numbers("见 [1] 与 [2]，还有 [2]") == (1, 2, 2)
    assert module.extract_citation_numbers("没有引用") == ()


def test_relevance_precheck_blocks_unrelated() -> None:
    module = load("04_relevance_precheck")
    bundle = build_context([module.CHUNK])
    assert relevance_precheck("系统 cyclone 级别是多少？", bundle).passed
    blocked = relevance_precheck("公司火星基地的预算是多少？", bundle)
    assert not blocked.passed and blocked.failed_checks == ("relevance",)
    assert "cyclone" in module.content_terms("系统 cyclone 级别？")


def test_refusal_template() -> None:
    module = load("05_refusal_template")
    assert len(module.REFUSAL_REASONS) == 3
    text = make_refusal("检索结果与问题不相关")
    assert text.startswith("信息不足") and "检索结果与问题不相关" in text


def test_number_entity_check() -> None:
    module = load("06_number_entity_check")
    good = "级别为 2 级，影响 30 名用户，负责人张伟 [1]。"
    bad = "级别为 5 级，影响 500 名用户，负责人李四 [1]。"
    entities = ("张伟", "李四")
    assert verify_numbers_entities(good, module.CONTEXT, entities).passed
    failed = verify_numbers_entities(bad, module.CONTEXT, entities).failed_checks
    assert failed == ("5", "500", "李四")


def test_low_temperature_range() -> None:
    module = load("07_low_temperature")
    assert 0 <= DEFAULT_TEMPERATURE <= 0.2
    assert len(module.LOGITS) == 3


def test_structured_answer_validation() -> None:
    module = load("08_structured_answer")
    good = '{"answer":"级别为 2 级 [1]","citation_numbers":[1],"refused":false}'
    parsed = module.validate_answer(good)
    assert parsed.answer.endswith("[1]") and parsed.citation_numbers == [1]
    with pytest.raises(ValidationError):
        module.validate_answer(good[:-1] + ',"extra":1}')
    empty = module.AnswerWithCitations(answer="信息不足")
    assert empty.citation_numbers == [] and empty.refused is False


def test_citation_mapping_filters_out_of_range() -> None:
    module = load("09_citation_mapping")
    mapped = module.map_citation_numbers([1, 2, 9], module.CHUNKS)
    assert [item.number for item in mapped] == [1, 2]
    assert mapped[0].title == "值班规范" and mapped[1].page == 4
    assert mapped[0].source == "DOC-A#p3"


def test_hallucination_guard_combination() -> None:
    module = load("10_hallucination_guard")
    bundle = build_context([module.CHUNK])
    question = "系统 cyclone 影响多少人？"
    ok = hallucination_guard(question, bundle, "影响 30 名用户 [1]。")
    bad = hallucination_guard(question, bundle, "影响 500 名用户 [1]。")
    assert ok.passed and not bad.passed and bad.failed_checks == ("500",)
    unrelated = hallucination_guard("公司火星基地的预算是多少？", bundle, "未知")
    assert unrelated.failed_checks == ("relevance", "post_check_skipped")


def test_models_source_is_derived() -> None:
    chunk = SourceChunk("DOC-X", "标题", 7, "内容")
    assert chunk.source == "DOC-X#p7"
