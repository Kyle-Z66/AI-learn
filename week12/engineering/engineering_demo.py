"""
第 12 周 · 工程层示范：100 条 golden set 上的四配置真实评测
================================================================
【对应知识点】文档第 12 周：跑基线 + 消融 + CI 化 + Markdown 报告

【周次学习要点】
  - 一次运行完成"校验评测集 → 四配置评测 → 报告渲染 → 门禁比较"全链路。
  - 报告数字直接来自 runner 的 ConfigResult，不手填、不复制文档示意值。
  - 门禁示例用 bm25_only 作基线、hybrid_rerank 作当前，展示退出码语义。

【易忽略细节 / 对照文档补足】
  1. 文档那张四行表明确是结构示意；这里强调"结构照它、数字自己跑"。
  2. 评测集会随运行产生真实的毫秒波动，报告里注明是本地教学测量。
  3. 门禁未通过时退出码 1，但 demo() 本身只打印不 SystemExit，
     便于测试与报告复用；CI 脚本请调用 ci_gate.run_gate()。

【示例用途】可运行：`python -m week12.engineering.engineering_demo`
             测试见 tests/week12/test_engineering.py
"""
from __future__ import annotations

from week12.engineering.ci_gate import compare_to_baseline
from week12.engineering.golden_set import (
    golden_set_summary,
    load_golden_set,
    validate_golden_set,
)
from week12.engineering.report import render_markdown_report
from week12.engineering.runner import run_all_configs


def demo() -> None:
    cases = load_golden_set()
    issues = validate_golden_set(cases)
    print("评测集校验：", issues if issues else "通过")
    print("评测集摘要：", golden_set_summary(cases))

    results = run_all_configs(cases)
    print("\n" + render_markdown_report(results))

    baseline = next(item for item in results if item.config == "bm25_only").scores
    current = next(item for item in results if item.config == "hybrid_rerank").scores
    gate = compare_to_baseline(current, baseline)
    print("门禁示例（hybrid_rerank vs bm25_only）：")
    print(f"  通过={gate.passed} 退化项={gate.regressions} exit_code={gate.exit_code()}")
    print("  Recall@5 变化：", round(gate.deltas["recall_at_k"], 4))


if __name__ == "__main__":
    demo()
