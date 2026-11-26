"""
第 10 周 · 工程层示范：精排、超时降级、故障降级
================================================================
【对应知识点】文档第 10 周：Top-50 → Top-5 + 超时降级链

【周次学习要点】
  - 同一批候选跑三次：正常精排、超时降级、故障降级，对比前 5 名顺序。
  - 降级时返回的 still 是 top_k 条，只是顺序回到首阶段——请求不会失败。
  - 教学延迟 20ms / 超时 1ms；真实 800ms 边界由生产配置决定。

【易忽略细节 / 对照文档补足】
  1. 候选文本是教学模拟数据，非真实业务内容。
  2. 首阶段分数越高越靠前，降级后候选顺序应与输入顺序一致。
  3. reason 字段供日志与指标聚合，演示里一并打印，便于核对。

【示例用途】可运行：`python -m week10.engineering.engineering_demo`
             测试见 tests/week10/test_engineering.py
"""
from __future__ import annotations

import asyncio

from week10.engineering.fallback import rerank_with_fallback
from week10.engineering.models import RerankCandidate
from week10.engineering.reranker import DeterministicReranker, RerankerConfig

QUERY = "SGCC-4012 巡检周期"


def _candidates() -> list[RerankCandidate]:
    """首阶段顺序：stage_score 从高到低。"""
    texts = [
        ("d1", "断路器通用巡检流程", 0.95),
        ("d2", "SGCC-4012 型号说明书", 0.91),
        ("d3", "SGCC-4012 巡检周期与温度阈值", 0.88),
        ("d4", "ERR_4012 错误码通信超时", 0.80),
        ("d5", "变电站冬季防冻巡检要点", 0.72),
        ("d6", "设备巡检工单审批规则", 0.65),
    ]
    return [
        RerankCandidate(chunk_id, text, score, "manual")
        for chunk_id, text, score in texts
    ]


async def demo() -> None:
    candidates = _candidates()
    print(f"查询：{QUERY}，首阶段顺序：{[c.chunk_id for c in candidates]}")
    scenarios = [
        ("正常精排", RerankerConfig()),
        ("超时降级", RerankerConfig(delay_ms=20)),
        ("故障降级", RerankerConfig(fail=True)),
    ]
    for label, config in scenarios:
        result = await rerank_with_fallback(
            QUERY,
            candidates,
            top_k=5,
            timeout_ms=1 if label == "超时降级" else 800,
            reranker=DeterministicReranker(config),
        )
        print(
            f"  {label}: top5={[c.chunk_id for c in result.candidates]} "
            f"degraded={result.degraded} reason={result.reason or '-'}"
        )
    print("精排把专名文档顶上去；降级保住首阶段顺序，请求始终有结果")


if __name__ == "__main__":
    asyncio.run(demo())
