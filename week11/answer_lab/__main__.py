"""
第 11 周 · 动手项目入口：四类用例跑出答案、引用与守卫结论
================================================================
【对应知识点】文档第 11 周验收：答案带引用 / 不相关拒答 / 数字实体幻觉粗检测

【周次学习要点】
  - 每条用例都走同一条链路：组装上下文 → 生成 → 注入篡改 → 组合守卫 → 判定。
  - 判定与用例期望解耦：期望写在 cases.py，运行器只负责比对，新增场景零改动。
  - 输出里同时打印答案、引用和 failed_checks，便于人工核对守卫解释性。

【易忽略细节】
  1. 篡改发生在生成之后：模拟"模型写错了"，而不是"上下文错了"，
     这样才能单独验证后校验的能力边界。
  2. 拒答用例的守卫会同时记 relevance 与 post_check_skipped，
     打印全部失败项比只看 passed 更利于排障。
  3. Java 常用 main() 里写一堆 if；这里把每个用例的结果做成 CaseResult 值对象，
     报告与测试可以复用同一份判定逻辑。

【示例用途】可运行：`python -m week11.answer_lab`
             测试见 tests/week11/test_answer_lab.py
"""
from __future__ import annotations

from dataclasses import dataclass

from week11.answer_lab.cases import LabCase, build_cases
from week11.engineering.context import build_context
from week11.engineering.generator import FakeGenerator
from week11.engineering.guards import hallucination_guard
from week11.engineering.models import GeneratedAnswer, GuardResult


@dataclass(frozen=True, slots=True)
class CaseResult:
    """一条用例的运行结果：原始生成 + 展示文本 + 守卫结论 + 判定。"""

    case: LabCase
    answer: GeneratedAnswer
    answer_text: str
    judgment: GuardResult
    verdict: str


def run_case(case: LabCase) -> CaseResult:
    """跑一条用例：先生成，再按用例注入篡改，最后过组合守卫。"""
    bundle = build_context(list(case.chunks), max_tokens=1000)
    answer = FakeGenerator().generate(case.question, bundle)
    answer_text = case.tamper(answer.text)
    judgment = hallucination_guard(
        case.question, bundle, answer_text, entities=case.entities
    )
    if case.expect_refused:
        expected_ok = answer.refused
        verdict = "符合预期（拒答）" if expected_ok else "异常：应当拒答却放行"
    elif case.expect_failed_check:
        expected_ok = not judgment.passed and all(
            item in judgment.failed_checks for item in case.expect_failed_check
        )
        verdict = "按预期拦下幻觉" if expected_ok else "异常：幻觉未被拦下"
    else:
        expected_ok = judgment.passed and not answer.refused
        verdict = "按预期放行" if expected_ok else "异常：正常答案被误拦"
    return CaseResult(case, answer, answer_text, judgment, verdict)


def run_all(cases: tuple[LabCase, ...] | None = None) -> tuple[CaseResult, ...]:
    """跑全部用例；不传 cases 时用 cases.py 的四类样例。"""
    selected = build_cases() if cases is None else cases
    return tuple(run_case(case) for case in selected)


def self_check() -> bool:
    """自检：四类用例的判定必须全部符合预期。"""
    return all(result.verdict.startswith(("按预期", "符合预期")) for result in run_all())


def main() -> None:
    for result in run_all():
        case = result.case
        print(f"【{case.category}】{case.name} · 问题：{case.question}")
        print("  答案：", result.answer_text)
        print("  引用：", [citation.source for citation in result.answer.citations])
        print(f"  拒答={result.answer.refused} 守卫通过={result.judgment.passed} "
              f"失败项={result.judgment.failed_checks}")
        print("  判定：", result.verdict, "\n")
    ok = self_check()
    print("自检：", "通过" if ok else "失败")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
