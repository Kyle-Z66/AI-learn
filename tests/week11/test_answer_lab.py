"""
第 11 周单元测试 · 动手项目 answer_lab 四类用例
"""
from __future__ import annotations

from importlib import import_module

from week11.answer_lab.cases import BASE_CHUNKS, LabCase, build_cases
from week11.engineering.context import build_context
from week11.engineering.generator import FakeGenerator

lab = import_module("week11.answer_lab.__main__")


def test_four_cases_shape() -> None:
    cases = build_cases()
    assert len(cases) == 4
    assert {case.category for case in cases} == {"相关", "不相关", "数字幻觉", "实体幻觉"}
    assert all(case.chunks == BASE_CHUNKS and case.question for case in cases)


def test_tamper_is_deterministic() -> None:
    case = build_cases()[2]
    assert case.tamper("影响 30 人") == "影响 500 人"
    assert build_cases()[0].tamper("原文") == "原文"


def test_run_all_verdicts() -> None:
    results = lab.run_all()
    assert len(results) == 4
    assert [result.verdict for result in results] == [
        "按预期放行",
        "符合预期（拒答）",
        "按预期拦下幻觉",
        "按预期拦下幻觉",
    ]
    assert results[0].answer.citations and results[1].answer.refused
    assert "500" in results[2].answer_text
    assert "李四" in results[3].answer_text


def test_self_check_passes() -> None:
    assert lab.self_check() is True


def test_custom_case_can_be_injected() -> None:
    case = LabCase("自定义", "相关", "系统 cyclone 影响多少人？", chunks=BASE_CHUNKS[:1])
    result = lab.run_case(case)
    assert result.verdict == "按预期放行"
    bundle = build_context(list(BASE_CHUNKS))
    assert FakeGenerator().generate(case.question, bundle).guard.passed
