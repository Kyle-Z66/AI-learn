"""
第 8 周 · 动手项目 CLI：相似度 / 过滤 / 持久化 / 召回
================================================================
【对应知识点】文档第 8 周四项验收：度量差异、带过滤检索、索引落地、ANN 取舍

【周次学习要点】
  - 运行 `python -m week08.vector_lab` 一次看完四个实验的真实输出。
  - 输出中的数字由程序计算，REPORT.md 的结论复制自实际运行。
  - 不连接任何数据库与 API：pgvector 以参数化 SQL 的形式在第 05 样例展示。

【易忽略细节】
  1. 度量不同导致排序不同，不代表某种 embedding 更好。
  2. 过滤后 c006（过期）与 dev/platform 文档都不在候选集里。
  3. 召回曲线只用于建立评估意识，不是 ANN 实现。

【示例用途】可运行：`python -m week08.vector_lab`
"""
from __future__ import annotations

from week08.vector_lab.benchmark import (
    compare_metrics,
    persistence_demo,
    recall_curve,
    scalar_filter_demo,
)
from week08.vector_lab.corpus import TODAY


def main() -> None:
    """打印四项实验结果。"""
    print("== 三种相似度（查询相同，只有度量不同）==")
    for metric, hits in compare_metrics().items():
        print(f"{metric:<10} Top-3：{hits}")

    unfiltered, filtered = scalar_filter_demo()
    print("\n== 标量过滤 ==")
    print(f"不过滤命中 {len(unfiltered)} 条：{unfiltered}")
    print(f"dept_id=ops 且 valid_until>{TODAY}：{filtered}")

    consistent, before, after = persistence_demo()
    print("\n== 持久化重载 ==")
    print(f"保存前 {before} 条 / 重载后 {after} 条 / Top-3 一致：{consistent}")

    print("\n== 召回基准（候选子集模拟 ANN）==")
    for ratio, recall in recall_curve():
        print(f"候选占比={ratio:.0%} → recall@3={recall:.0%}")


if __name__ == "__main__":
    main()
