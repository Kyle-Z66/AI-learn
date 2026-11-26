"""
第 9 周 · 工程层示范：双路召回一次跑通
================================================================
【对应知识点】文档第 9 周：BM25 + 向量双路召回 + RRF 融合 + Top-K

【周次学习要点】
  - 同一查询分别看两路原始分与融合排名，理解"各路独立、融合才比较"。
  - 过滤在召回前生效：加 dept / valid 条件后，结果集里不应再出现被排除的文档。
  - weighted 模式需要先归一化；与 rrf 对比能看到排名差异。

【易忽略细节 / 对照文档补足】
  1. 演示语料是教学用的模拟电网知识库，不对应任何真实业务数据。
  2. 候选的 bm25_score / dense_score 可以为 None：某路没召回该文档就是缺失。
  3. 教学向量用的是第 8 周确定性哈希嵌入，不需要下载模型、不需要网络。

【示例用途】可运行：`python -m week09.engineering.engineering_demo`
             测试见 tests/week09/test_engineering.py
"""
from __future__ import annotations

from week09.engineering.hybrid_retriever import HybridRetriever
from week09.engineering.models import Candidate

DEMO_CORPUS: list[Candidate] = [
    Candidate(
        chunk_id="c-01",
        text="SGCC-4012 型号断路器巡检周期与温度阈值说明",
        source="device_manual",
        dept="运维",
    ),
    Candidate(
        chunk_id="c-02",
        text="ERR_4012 错误码表示通信链路超时，需检查串口连接",
        source="error_codes",
        dept="运维",
    ),
    Candidate(
        chunk_id="c-03",
        text="断路器日常巡检的通用注意事项",
        source="device_manual",
        dept="运维",
    ),
    Candidate(
        chunk_id="c-04",
        text="SGCC-4012 已停用批次的处理办法",
        source="archive",
        dept="运维",
        valid=False,
    ),
    Candidate(
        chunk_id="c-05",
        text="财务报销流程与发票归档要求",
        source="finance",
        dept="财务",
    ),
]


def demo() -> None:
    retriever = HybridRetriever(DEMO_CORPUS)
    query = "SGCC-4012 巡检"
    for mode in ("rrf", "weighted"):
        results = retriever.retrieve(query, top_k=3, mode=mode)  # type: ignore[arg-type]
        print(f"[{mode}] 查询={query}")
        for item in results:
            bm25 = "-" if item.bm25_score is None else f"{item.bm25_score:.3f}"
            dense = "-" if item.dense_score is None else f"{item.dense_score:.3f}"
            fused = "-" if item.fused_score is None else f"{item.fused_score:.5f}"
            print(
                f"  #{item.rank} {item.chunk_id} bm25={bm25} dense={dense} "
                f"fused={fused} :: {item.text}"
            )

    filtered = retriever.retrieve(query, top_k=10, dept="运维", valid_only=True)
    print(f"过滤后（dept=运维, valid_only=True）共 {len(filtered)} 条：")
    print("  " + ", ".join(item.chunk_id for item in filtered))
    print("  已失效的 c-04 与财务文档 c-05 均未进入候选池")


if __name__ == "__main__":
    demo()
