"""
第 10 周 · 本周特有坑：rerank 三个高频翻车点
================================================================
【对应知识点】文档第 10 周：延迟成本 / 超时降级 / 候选预算

【周次学习要点】
  - rerank 超时不降级：一个慢服务把整个问答请求拖到失败。
  - 候选给太多：延迟线性增长，边际收益却递减。
  - 把 rerank 当召回：首阶段没召回的文档，精排永远找不回来。

【易忽略细节】
  1. 降级必须返回首阶段顺序，而不是空列表或异常。
  2. 没有 degraded 标记就无法统计降级率，故障会被指标掩盖。
  3. 真实 reranker 比教学打分慢得多；延迟数字必须实测，不要照抄文档。

【示例用途】可运行：`python -m week10.pitfalls.rerank_pitfalls`
             测试见 tests/week10/test_pitfalls.py
"""
from __future__ import annotations

import importlib
from typing import Any

from week10.engineering.models import RerankCandidate

# 数字开头的模块名只能用 importlib 加载。
_latency_module: Any = importlib.import_module(
    "week10.core_mechanisms.08_latency_model"
)
estimate_latency_ms = _latency_module.estimate_latency_ms

STAGE_ORDER = ["d1", "d2", "d3"]


def demo_timeout_drags_request() -> None:
    print(f"首阶段顺序：{STAGE_ORDER}")
    print("错误：等 rerank 超时 → 整个请求失败 / 用户等到超时")
    print("正确：wait_for 超时 → 返回 STAGE_ORDER[:top_k] 并标记 degraded=True")
    print("Java 侧 Redis / WebSocket 降级链就是这套思路，不必重新发明")


def demo_too_many_candidates() -> None:
    for count in (30, 50, 100, 200):
        print(f"  {count:>3} 个候选 → 教学模型 {estimate_latency_ms(count):>6.0f}ms")
    print("延迟线性涨、收益递减 → 交互式 30~50，批处理才上 100+")


def demo_rerank_as_retrieval() -> None:
    candidates = [
        RerankCandidate("d1", "断路器通用巡检流程", 0.95),
        RerankCandidate("d2", "SGCC-4012 型号说明书", 0.91),
    ]
    missing = "d9"
    pool = {item.chunk_id for item in candidates}
    print(f"候选池：{sorted(pool)}；想找的文档：{missing}")
    print(f"精排后仍在池内：{missing in pool} → rerank 只重排，不新增候选")
    print("召回缺失要先修混合检索（第 9 周），不是加 rerank 能解决的")


def demo_degraded_flag_missing() -> None:
    print("两条请求都返回了 Top-5，但一条精排、一条降级")
    print("没有 degraded 标记 → 指标显示'效果正常'，故障被掩盖")
    print("修复：RerankResult.degraded + reason 进日志与指标聚合")


def demo() -> None:
    demo_timeout_drags_request()
    demo_too_many_candidates()
    demo_rerank_as_retrieval()
    demo_degraded_flag_missing()


if __name__ == "__main__":
    demo()
