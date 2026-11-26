"""
第 7 周 · 动手项目 CLI：四种切分策略的同语料对比
================================================================
【对应知识点】文档第 7 周切分实验的四个对比维度

【周次学习要点】
  - 运行 `python -m week07.chunking_lab` 直接得到对比表，不需要装额外工具。
  - 输出 chunk 数、平均 token、结构截断率与人工抽检提示。
  - 数字全部由程序算出，REPORT.md 里的结论复制自实际运行。

【易忽略细节】
  1. 平均长度用 token 估算而非字符数，和 reranker 的输入预算口径一致。
  2. small-to-big 的小块数更多属预期，重点看它是否保住父块上下文。
  3. 截断率是启发式指标，只能提示风险，最终仍要人工看样本。

【示例用途】可运行：`python -m week07.chunking_lab`
"""
from __future__ import annotations

from week07.chunking_lab.corpus import build_corpus_document
from week07.chunking_lab.evaluate import build_results, format_results, manual_review_hints


def main() -> None:
    """打印四种策略的对比结果。"""
    document = build_corpus_document()
    results = build_results(document)
    print(f"语料：{document.title}（{len(document.sections)} 个标题）")
    print(format_results(results))
    print("\n人工抽检提示（每条随机看 10 个样本）：")
    for hint in manual_review_hints():
        print(f"  - {hint}")
    print("\n前两个样本（不同策略）：")
    for result in results:
        for sample in result.samples:
            print(f"  [{result.name}] {sample}")


if __name__ == "__main__":
    main()
