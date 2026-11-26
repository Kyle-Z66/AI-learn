"""
第 12 周 · 工程层：Markdown 评测报告渲染
================================================================
【对应知识点】文档第 12 周：输出一份 Markdown 评测报告 + 四配置对比表

【周次学习要点】
  - 报告由程序渲染，数字来自 ConfigResult；手抄错一个格子就是假报告。
  - 表格之外附逐案 recall 的最小值/中位数/最大值，回应"只看平均分"的陷阱。
  - 报告头写明数据来源与延迟口径，读者无需翻代码就知道指标边界。

【易忽略细节】
  1. 文档给的四列表是"结构示意"：本工程补齐 Context Recall、Answer Relevance
     与分布列，但所有数字必须来自本地实跑，不复制示意值。
  2. 延迟单位统一 ms 并保留 1 位小数：p95 受机器负载影响，精确太多位反而误导。
  3. Java 常用模板引擎 + Map 渲染；这里用 f-string 拼表行，
     列顺序与 EvalScores 字段一一对应，增删字段时测试会先失败。

【示例用途】被 engineering_demo.py / core_mechanisms/10 引用；
             实跑输出抄入 p2_rag/REPORT.md
"""
from __future__ import annotations

from collections.abc import Sequence
from statistics import median

from week12.engineering.models import ConfigResult

HEADER = (
    "| 配置 | Recall@5 | MRR@10 | Context Precision | "
    "Context Recall | Faithfulness | Answer Relevance | p95 延迟(ms) |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- |"
)


def _row(result: ConfigResult) -> str:
    score = result.scores
    return (
        f"| {result.config} | {score.recall_at_k:.3f} | {score.mrr:.3f} | "
        f"{score.context_precision:.3f} | {score.context_recall:.3f} | "
        f"{score.faithfulness:.3f} | {score.answer_relevance:.3f} | "
        f"{score.p95_latency_ms:.1f} |"
    )


def render_markdown_report(results: Sequence[ConfigResult]) -> str:
    """把四配置结果渲染成含分布与口径说明的 Markdown 报告。"""
    lines = [
        "# RAG 效果评测报告（本地实跑输出）",
        "",
        "> 数据来源：教学样例 golden_set.json（100 条，非真实业务数据）；"
        "指标由 week12.engineering.runner 本地计算。",
        "> p95 延迟为本地单机教学测量，不代表线上 SLA。",
        "",
        "## 四配置对比表",
        "",
        HEADER,
    ]
    lines.extend(_row(result) for result in results)
    lines.extend([
        "",
        "## 逐案 Recall@5 分布（不看平均分盲区）",
        "",
        "| 配置 | 最小 | 中位 | 最大 |",
        "| --- | --- | --- | --- |",
    ])
    for result in results:
        values = result.per_case_recall
        lines.append(
            f"| {result.config} | {min(values):.3f} | {median(values):.3f} | "
            f"{max(values):.3f} |"
        )
    lines.extend([
        "",
        "## 口径说明",
        "",
        "- Recall@5 分母是标注片段数；Context Precision 分母是 Top-K。",
        "- Faithfulness 检查答案中数字/实体是否被上下文支持；无可核验声明记 1.0。",
        "- Answer Relevance 为问题与答案的实词覆盖率（教学版，非语义向量）。",
        "- dense-only 与 rerank 均为确定性本地替身，生产需替换为真实模型。",
    ])
    return "\n".join(lines) + "\n"
