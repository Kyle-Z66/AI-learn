"""
第 8 周 · 核心机制 06：HNSW 与 IVF 的取舍
================================================================
【对应知识点】文档第 8 周：建 HNSW / IVF 索引，调 ef_search / probes

【周次学习要点】
  - HNSW 是基于图的近似最近邻：召回高、内存大，调 ef_search。
  - IVF 是先聚类再在少数桶里搜：内存省、要调 probes/nprobe。
  - 小数据集用暴力精确检索最划算，别一上来就上 ANN。

【易忽略细节】
  1. ef_search / probes 越大召回越高，但延迟与 CPU 同步上升，要实测曲线。
  2. IVF 的 lists 太小会导致单桶过大，太大则每个桶样本不足。
  3. ANN 是"近似"，必须和暴力精确结果比召回率，不能只看延迟。

【示例用途】可运行：`python -m week08.core_mechanisms.06_hnsw_ivf`
             测试见 tests/week08/test_core_mechanisms.py
"""
from __future__ import annotations

# (索引, 结构, 优势, 代价, 关键参数)
INDEX_TRADEOFFS: tuple[tuple[str, str, str, str, str], ...] = (
    ("精确", "全量扫描", "100% 召回", "O(n) 延迟", "无"),
    ("HNSW", "多层图", "高召回/低延迟", "内存占用大", "ef_search"),
    ("IVF", "聚类倒排", "内存省", "召回受 probes 影响", "probes/nprobe"),
)


def recommend_index(row_count: int, recall_target: float) -> str:
    """按数据规模与召回目标给出索引建议。"""
    if row_count < 100_000:
        return "精确"
    if recall_target >= 0.95:
        return "HNSW"
    return "IVF"


def demo() -> None:
    print("索引    结构        优势            代价              关键参数")
    for name, structure, benefit, cost, parameter in INDEX_TRADEOFFS:
        print(f"{name:<7} {structure:<11} {benefit:<15} {cost:<17} {parameter}")
    for rows, target in ((1_000, 0.99), (1_000_000, 0.98), (1_000_000, 0.85)):
        print(f"行数={rows:>8} 目标召回={target:.2f} → {recommend_index(rows, target)}")


if __name__ == "__main__":
    demo()
