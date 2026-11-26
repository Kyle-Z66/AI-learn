"""
第 11 周 · 工程层：生成侧数据模型（Chunk / 引用 / 守卫结果 / 答案）
================================================================
【对应知识点】文档第 11 周：上下文带编号、答案带 [1][2] 引用、后处理映射回原文

【周次学习要点】
  - SourceChunk 是检索链交到生成链的唯一接口：内容 + doc_id / 标题 / 页码元数据。
  - Citation 把"答案里的 [n]"与"原文出处"绑定，是 RAG 与普通 LLM 调用的分水岭。
  - GuardResult 让"拒答"成为一等公民：它不是异常，而是带原因的正常返回值。

【易忽略细节】
  1. Java 习惯于给每个 DTO 写 getter；Python 用 frozen dataclass 表达不可变值对象，
     字段直接读，少一层样板代码，也避免生成过程中被意外改写。
  2. source 必须是派生属性而不是手工传入的字段，否则 doc_id/page 改了以后引用会漂移。
  3. failed_checks 用 tuple 而非 list：守卫结果跨线程/跨请求传递时不应被中途追加。

【示例用途】被 context.py / guards.py / generator.py 与 core_mechanisms 全部样例引用；
             测试见 tests/week11/test_engineering.py
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceChunk:
    """一个带出处的检索片段（第 7~10 周检索链的产物，本周只消费不重写）。"""

    doc_id: str
    title: str
    page: int
    content: str

    @property
    def source(self) -> str:
        """稳定的出处标识：引用映射与 cited sources 都用它，避免各处拼字符串漂移。"""
        return f"{self.doc_id}#p{self.page}"


@dataclass(frozen=True, slots=True)
class Citation:
    """答案中的一条引用：number 是答案里的 [n]，其余字段指回原文。"""

    number: int
    doc_id: str
    title: str
    page: int
    source: str


@dataclass(frozen=True, slots=True)
class GuardResult:
    """守卫结论：passed 表示可放行；失败时 reason 与 failed_checks 给出可观测原因。"""

    passed: bool
    reason: str
    failed_checks: tuple[str, ...] = ()

    def merge(self, other: GuardResult) -> GuardResult:
        """合并两道守卫：任一失败即整体失败，失败项累加，便于一次看全问题。"""
        failed = self.failed_checks + other.failed_checks
        return GuardResult(
            passed=self.passed and other.passed,
            reason=f"{self.reason}；{other.reason}",
            failed_checks=failed,
        )


@dataclass(frozen=True, slots=True)
class ContextBundle:
    """上下文组装结果：text 进 Prompt，sources 与 chunks 只含真正塞进预算的片段。"""

    text: str
    sources: tuple[str, ...]
    chunks: tuple[SourceChunk, ...]
    truncated: bool
    omitted_count: int


@dataclass(frozen=True, slots=True)
class GeneratedAnswer:
    """一次生成的结果：答案、引用、是否拒答、守卫结论与温度（可复现实验用）。"""

    text: str
    citations: tuple[Citation, ...]
    refused: bool
    guard: GuardResult
    temperature: float
