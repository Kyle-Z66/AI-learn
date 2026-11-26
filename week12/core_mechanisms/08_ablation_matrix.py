"""
第 12 周 · 核心机制 08：四配置消融矩阵
================================================================
【对应知识点】文档第 12 周：同一查询集跑 BM25/dense/hybrid/hybrid+rerank 画对比表

【周次学习要点】
  - 消融的价值是"归因"：只换检索排序，指标变化就能归因到那一层。
  - 本样例取前 20 条做快速演示；完整 100 条结果见 p2_rag/REPORT.md。
  - 表格由 report.render_markdown_report 渲染，数字来自 runner 实跑。

【易忽略细节】
  1. 不能用同一份数据边调参边报最终数字：那叫测试集泄漏（见 pitfalls）。
  2. 快速演示的 20 条与完整报告口径不同，不要拿演示数字填简历。
  3. Java 里常用 Guava Table 存二维指标；这里用 ConfigResult 列表，
     行顺序固定，报告与门禁都按同一顺序读取。

【示例用途】可运行：`python -m week12.core_mechanisms.08_ablation_matrix`
             测试见 tests/week12/test_core_mechanisms.py
"""
from __future__ import annotations

from week12.engineering.golden_set import load_golden_set
from week12.engineering.report import render_markdown_report
from week12.engineering.runner import run_all_configs

DEMO_CASE_COUNT = 20


def demo() -> None:
    cases = load_golden_set()[:DEMO_CASE_COUNT]
    results = run_all_configs(cases)
    print(f"快速消融演示：仅取前 {len(cases)} 条，完整报告见 p2_rag/REPORT.md\n")
    print(render_markdown_report(results))


if __name__ == "__main__":
    demo()
