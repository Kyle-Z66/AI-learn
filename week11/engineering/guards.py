"""
第 11 周 · 工程层：生成侧守卫（相关性预检 + 数字实体后校验 + 组合）
================================================================
【对应知识点】文档第 11 周：上下文相关性预检；答案后校验（数字/实体是否在 context）

【周次学习要点】
  - 预检挡"检索结果与问题无关"：这类输入再会写 Prompt 也救不回来，直接拒答最省成本。
  - 后校验挡"答案编了 context 里没有的数字/实体"：这是幻觉检测的粗实现，可解释、可测试。
  - 组合守卫把两道闸串起来：预检失败就不必调模型；后校验失败就不放行答案。

【易忽略细节】
  1. 中文没有空格，不能用 split() 当分词；这里用"单字 + 相邻二元组"的教学版切分，
     再过滤停用词。预检只认长度>=2 的词：单字会在"预算"与"成本计算"、
     "基地"与"基线"之间制造假相关，让无关问题被误放行。
  2. 数字校验要排除答案里的 [1][2] 引用编号，否则引用本身会被误判成幻觉数字。
  3. Java 里爱用抛异常表达失败；这里守卫返回 GuardResult 值对象，
     调用方自己决定是换文案、重试还是记指标，控制流更清晰。

【示例用途】被 generator.py / answer_lab/__main__.py / core_mechanisms 04、06、10 引用；
             测试见 tests/week11/test_engineering.py
"""
from __future__ import annotations

import re
from collections.abc import Sequence

from week11.engineering.models import ContextBundle, GuardResult

REFUSAL_TEMPLATE = "信息不足，无法基于给定上下文回答：{reason}"

# 教学版停用词：问题里的"多少/什么"不该被当成检索相关的证据。
STOP_TERMS: frozenset[str] = frozenset({
    "的", "了", "和", "是", "在", "有", "为", "与", "及", "请", "吗",
    "什么", "多少", "怎么", "如何", "关于", "文档", "相关", "关键",
    "结论", "说明", "规定", "要求", "范围", "参数", "项目", "公司",
})


def text_terms(text: str) -> frozenset[str]:
    """中英混合切分：ASCII 取小写词，CJK 取单字与相邻二元组（确定性、无第三方依赖）。"""
    terms: set[str] = set(re.findall(r"[a-z0-9]+", text.lower()))
    for run in re.findall(r"[\u4e00-\u9fff]+", text):
        terms.update(run)
        terms.update(run[i : i + 2] for i in range(len(run) - 1))
    return frozenset(terms)


def content_terms(text: str) -> frozenset[str]:
    """去掉停用词后的实词集合，供相关性判断与评测指标复用。"""
    return text_terms(text) - STOP_TERMS


def extract_answer_numbers(answer: str) -> tuple[str, ...]:
    """抽取答案中的业务数字，先剔除 [n] 引用标记，避免把编号本身当幻觉数字。"""
    without_citations = re.sub(r"\[\d+\]", "", answer)
    return tuple(re.findall(r"\d+", without_citations))


def make_refusal(reason: str) -> str:
    """统一拒答文案：措辞固定，便于前端识别与指标统计。"""
    return REFUSAL_TEMPLATE.format(reason=reason)


def relevance_precheck(
    question: str,
    context: ContextBundle,
    min_overlap: int = 1,
) -> GuardResult:
    """检索结果与问题没有实词交集就直接拒答，不把无关证据送进生成。"""
    question_terms = {term for term in content_terms(question) if len(term) >= 2}
    context_terms = {term for term in content_terms(context.text) if len(term) >= 2}
    overlap = question_terms & context_terms
    if len(overlap) < min_overlap:
        return GuardResult(
            passed=False,
            reason="检索结果与问题不相关",
            failed_checks=("relevance",),
        )
    return GuardResult(passed=True, reason="检索结果与问题相关")


def _supported(claim: str, context: str) -> bool:
    """数字按完整数字匹配（避免 3 命中 30），实体按子串匹配。"""
    if claim.isdigit():
        return re.search(rf"(?<!\d){re.escape(claim)}(?!\d)", context) is not None
    return claim in context


def verify_numbers_entities(
    answer: str,
    context: str,
    entities: Sequence[str] = (),
) -> GuardResult:
    """后校验：答案中的每个业务数字、每个给定实体都必须能在上下文里找到。"""
    claims: list[str] = list(extract_answer_numbers(answer))
    claims.extend(entity for entity in entities if entity in answer)
    failed = tuple(claim for claim in claims if not _supported(claim, context))
    if failed:
        return GuardResult(
            passed=False,
            reason=f"答案包含上下文不支持的内容：{','.join(failed)}",
            failed_checks=failed,
        )
    return GuardResult(passed=True, reason="数字与实体均在上下文中得到支持")


def hallucination_guard(
    question: str,
    context: ContextBundle,
    answer: str,
    entities: Sequence[str] = (),
) -> GuardResult:
    """组合两道闸：先预检检索相关性，再后校验答案事实，失败项一次收齐。"""
    pre = relevance_precheck(question, context)
    if not pre.passed:
        return pre.merge(
            GuardResult(
                passed=False,
                reason="跳过后校验：上下文已被预检判定为无关",
                failed_checks=("post_check_skipped",),
            )
        )
    post = verify_numbers_entities(answer, context.text, entities)
    return pre.merge(post)
