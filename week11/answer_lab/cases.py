"""
第 11 周 · 动手项目：四类生成可靠性用例定义
================================================================
【对应知识点】文档第 11 周验收：带引用、不相关拒答、数字/实体幻觉检测粗实现

【周次学习要点】
  - 四类用例覆盖两条防线：不相关 → 预检拒答；数字/实体编造 → 后校验拦截。
  - 用例是数据不是脚本：新增场景只加一条 LabCase，运行器不用改。
  - 幻觉用"替换真实值"注入，保证除目标差异外其它条件完全一致。

【易忽略细节】
  1. replace 用 (原文, 替换) 对而非随机数：实验必须可复现，结果才能进报告。
  2. 相关用例故意不放 inject，用来证明守卫不会误伤正常答案。
  3. Java 里常用 enum + switch 分派场景；这里用 dataclass 数据驱动，
     少一层分支，测试也能直接构造用例。

【示例用途】被 __main__.py 与 tests/week11/test_answer_lab.py 引用；不单独运行。
"""
from __future__ import annotations

from dataclasses import dataclass

from week11.engineering.models import SourceChunk

BASE_CHUNKS: tuple[SourceChunk, ...] = (
    SourceChunk(
        doc_id="DOC-001",
        title="cyclone 事件处置规范",
        page=3,
        content="系统 cyclone 的严重级别为 2 级，影响 30 名用户。",
    ),
    SourceChunk(
        doc_id="DOC-001",
        title="cyclone 事件处置规范",
        page=4,
        content="负责人为张伟，备用联系人李娜。",
    ),
)


@dataclass(frozen=True, slots=True)
class LabCase:
    """一条实验用例：问题 + 上下文 + 可选篡改 + 期望结果。"""

    name: str
    category: str
    question: str
    chunks: tuple[SourceChunk, ...] = BASE_CHUNKS
    replace: tuple[tuple[str, str], ...] = ()
    entities: tuple[str, ...] = ()
    expect_refused: bool = False
    expect_failed_check: tuple[str, ...] = ()

    def tamper(self, answer: str) -> str:
        """把真实值替换成幻觉值；没有替换时原样返回。"""
        for old, new in self.replace:
            answer = answer.replace(old, new)
        return answer


def build_cases() -> tuple[LabCase, ...]:
    """返回相关 / 不相关 / 数字幻觉 / 实体幻觉四类教学用例。"""
    return (
        LabCase(
            name="相关问答",
            category="相关",
            question="系统 cyclone 影响多少人？",
        ),
        LabCase(
            name="超范围问题",
            category="不相关",
            question="公司火星基地的预算是多少？",
            expect_refused=True,
        ),
        LabCase(
            name="数字幻觉",
            category="数字幻觉",
            question="系统 cyclone 影响多少人？",
            replace=(("30", "500"),),
            expect_failed_check=("500",),
        ),
        LabCase(
            name="实体幻觉",
            category="实体幻觉",
            question="系统 cyclone 的负责人是谁？",
            replace=(("张伟", "李四"),),
            entities=("张伟", "李四"),
            expect_failed_check=("李四",),
        ),
    )
