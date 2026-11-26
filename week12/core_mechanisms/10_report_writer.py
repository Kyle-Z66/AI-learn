"""
第 12 周 · 核心机制 10：Markdown 报告生成
================================================================
【对应知识点】文档第 12 周：输出一份 Markdown 评测报告（对比表）

【周次学习要点】
  - 报告 = 表头 + 数据行 + 分布 + 口径说明；所有数字来自 ConfigResult。
  - 固定列顺序与 EvalScores 字段一一对应，增删指标时测试先失败而不是报告悄悄错列。
  - 本样例用构造数据演示渲染；正式报告必须实跑 runner 后抄写真实输出。

【易忽略细节】
  1. 文档那张表是结构示意，演示数据也明确标注"示意"，不能抄进简历当成绩。
  2. 只报均值会掩盖长尾，报告额外输出逐案 recall 的最小/中位/最大。
  3. Java 常用模板引擎；这里 f-string 足够，但要统一格式化位数避免列宽漂移。

【示例用途】可运行：`python -m week12.core_mechanisms.10_report_writer`
             测试见 tests/week12/test_core_mechanisms.py
"""
from __future__ import annotations

from week12.engineering.models import ConfigResult, EvalScores
from week12.engineering.report import render_markdown_report


def demo_scores(seed: int) -> EvalScores:
    """构造渲染演示用的示意分数（不是真实评测结果）。"""
    base = 0.60 + seed * 0.05
    return EvalScores(base, base - 0.05, base - 0.02, base, base + 0.1, base - 0.1, 40.0 + seed * 8)


def demo() -> None:
    results = [
        ConfigResult(name, demo_scores(index), (0.8, 0.9, 1.0), 3)
        for index, name in enumerate(("bm25_only", "dense_only", "hybrid", "hybrid_rerank"))
    ]
    print("以下是渲染示意（数字为构造值，正式报告见 p2_rag/REPORT.md）：\n")
    print(render_markdown_report(results))


if __name__ == "__main__":
    demo()
