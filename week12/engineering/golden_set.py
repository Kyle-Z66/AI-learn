"""
第 12 周 · 工程层：golden set 读取与标注校验
================================================================
【对应知识点】文档第 12 周：100 条标注问答（标准答案 + 相关文档片段 ID + 标注标准）

【周次学习要点】
  - 评测集是资产：从文件读入、按结构校验、可导出扩充；不硬编码在评测脚本里。
  - 每条样本带 metadata（来源/标注规则/难度），面试追问"数据怎么来的"时有据可查。
  - validate_golden_set() 把"条数够不够、字段全不全、问题是否重复"变成可运行门禁。

【易忽略细节】
  1. 本项目 golden_set.json 是**教学样例**，不是真实业务数据；metadata.source 明确标注，
     替换真实数据时只换 JSON，不改任何评测代码。
  2. 文档原文说"从真实场景造 100 条"，这里不能伪造业务数据，因此提供模板化样例并
     在 README 写清替换步骤；宁少而精的口径由 validate 的期望条数保证。
  3. Java 里常用 Jackson + DTO；Python 用 json.loads + 显式字段构造，
     类型不确定时用 cast 交给 mypy 校验，而不是到处 assert。

【示例用途】被 engineering_demo.py / runner.py / core_mechanisms 01、02 引用；
             测试见 tests/week12/test_engineering.py
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import cast

from week12.engineering.models import GoldenCase

DEFAULT_GOLDEN_SET: Path = Path(__file__).resolve().parents[1] / "p2_rag" / "golden_set.json"
REQUIRED_FIELDS: tuple[str, ...] = ("question", "answer", "relevant_chunk_ids", "metadata")


def load_golden_set(path: Path | None = None) -> list[GoldenCase]:
    """读取 100 条标注样本；默认读 p2_rag/golden_set.json，可传路径做隔离测试。"""
    target = DEFAULT_GOLDEN_SET if path is None else path
    payload: object = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("golden set 顶层必须是数组")
    cases: list[GoldenCase] = []
    for index, item in enumerate(payload, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"第 {index} 条不是对象")
        missing = [field for field in REQUIRED_FIELDS if field not in item]
        if missing:
            raise ValueError(f"第 {index} 条缺少字段：{missing}")
        cases.append(GoldenCase.from_dict(cast(dict[str, object], item)))
    return cases


def validate_golden_set(
    cases: list[GoldenCase],
    expected: int = 100,
) -> tuple[str, ...]:
    """返回问题清单；空元组表示可用于评测。"""
    issues: list[str] = []
    if len(cases) != expected:
        issues.append(f"条数 {len(cases)} != 期望 {expected}")
    duplicates = [q for q, count in Counter(case.question for case in cases).items() if count > 1]
    if duplicates:
        issues.append(f"问题重复 {len(duplicates)} 条")
    for index, case in enumerate(cases, start=1):
        if not case.question.strip() or not case.answer.strip():
            issues.append(f"第 {index} 条问题或答案为空")
        if not case.relevant_chunk_ids:
            issues.append(f"第 {index} 条缺少 relevant_chunk_ids")
        if case.metadata.get("source", "").startswith("教学样例") is False:
            issues.append(f"第 {index} 条未标注数据来源")
    return tuple(issues)


def golden_set_summary(cases: list[GoldenCase]) -> dict[str, object]:
    """输出可打印的统计信息：条数、片段覆盖数、难度与来源分布。"""
    return {
        "count": len(cases),
        "chunks": len({cid for case in cases for cid in case.relevant_chunk_ids}),
        "topics": len({case.metadata.get("topic", "") for case in cases}),
        "sources": dict(Counter(case.metadata.get("source", "") for case in cases)),
    }
