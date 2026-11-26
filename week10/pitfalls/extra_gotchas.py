"""
第 10 周 · 补足要点：定位、经验平移与预算口径
================================================================
【对应知识点】文档第 10 周容错设计与延迟成本

【周次学习要点】
  - 先修检索再修生成：候选里没有答案，rerank 与 prompt 都救不回来。
  - 降级链与 Java 侧同构：Redis 失败降级本地缓存、WebSocket 断连降级 List。
  - 交互式与批处理的候选预算不同：前者控延迟，后者控质量。

【易忽略细节】
  1. 第 9 周混合检索是本周的前提，不重复讲 BM25/RRF 原理。
  2. 第 12 周才做完整评测体系；这里只做三方轻量指标对比。
  3. 延迟与质量要分开汇报："快但错"和"慢但对"都不是结论。

【示例用途】可运行：`python -m week10.pitfalls.extra_gotchas`
             测试见 tests/week10/test_pitfalls.py
"""
from __future__ import annotations

JAVA_ANALOGY = [
    ("Redis 读失败", "降级本地缓存", "rerank 超时 → 首阶段顺序"),
    ("WebSocket 断连", "降级 Redis List", "精排服务异常 → Top-K 直通"),
    ("固定窗口限流", "令牌桶平滑突发", "Semaphore 限制精排在途数"),
]

BUDGET_RULES = [
    ("交互式对话", "30~50", "用户等不起，超时立刻降级"),
    ("离线批处理", "100+", "无实时用户，用延迟换质量"),
]

DEBUG_ORDER = [
    "先看候选池里有没有答案（第 9 周检索）",
    "再看精排是否把正确候选提前（第 10 周 rerank）",
    "最后才调生成 prompt（第 11 周）",
]


def demo_java_analogy() -> None:
    print("Java 侧经验平移：")
    for source, fallback, target in JAVA_ANALOGY:
        print(f"  {source:<14} → {fallback:<14} ≈ {target}")


def demo_budget_rules() -> None:
    for scene, budget, note in BUDGET_RULES:
        print(f"{scene:<12} 候选预算={budget:<8} | {note}")


def demo_debug_order() -> None:
    for step, description in enumerate(DEBUG_ORDER, start=1):
        print(f"  {step}. {description}")


def demo() -> None:
    demo_java_analogy()
    demo_budget_rules()
    demo_debug_order()


if __name__ == "__main__":
    demo()
