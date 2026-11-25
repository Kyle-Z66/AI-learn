"""
第 5 周 · 补足要点：可靠性认知边界与统计口径
================================================================
【对应知识点】对照文档第 5 周补足：熔断/限流/降级区别、分位数口径、
              成本归因、日志脱敏

【周次学习要点】
  - 限流管"放多少进来"（第 4 周），熔断管"还敢不敢放"，降级管"换谁来接"。
  - p95 有 nearest-rank 与插值两种口径，不统一就无法对接监控。
  - 缓存命中与降级换模型会让"按首选单价估算"失真。

【易忽略细节】
  1. 平均值不是 p95：10 个请求里 1 个 5 秒，均值仍可能看起来正常。
  2. 审计日志里的密钥/手机号必须脱敏，否则审计库本身成为泄漏点。
  3. 幂等键要来自业务标识，随机 UUID 会破坏去重（见 resilience_pitfalls）。

【示例用途】可运行：`python -m week05.pitfalls.extra_gotchas`
             测试见 tests/week05/test_pitfalls.py
"""
from __future__ import annotations

from week05.engineering.audit import sanitize
from week05.engineering.cost_report import estimate_cost
from week05.engineering.metrics import percentile

CONCEPTS = [
    ("限流（第4周）", "控制单位时间进入的请求数", "令牌桶 / Semaphore", "防止打满配额"),
    ("熔断（本周）", "按失败率暂时拒绝调用", "closed/open/half-open", "防止雪崩扩散"),
    ("降级（本周）", "主模型不可用时切换备用", "按优先级换 provider", "保证有结果返回"),
]


def demo_three_concepts() -> None:
    print("概念       | 解决什么             | 实现手段              | 目的")
    for name, question, tool, goal in CONCEPTS:
        print(f"{name:<10} | {question:<18} | {tool:<20} | {goal}")


def demo_percentile_definition() -> None:
    values = [80, 90, 100, 110, 120, 130, 140, 150, 160, 5000]
    average = sum(values) / len(values)
    print(f"样本={values}")
    print(f"均值={average:.0f}ms（被一个慢请求拉高）p95={percentile(values, 0.95):.0f}ms")
    print("工程约定：nearest-rank，取 ceil(0.95*n)-1 位置")


def demo_cost_attribution() -> None:
    """缓存命中 + 降级都会让按首选模型估算的成本失真。"""
    naive = estimate_cost("qwen", 1000, 200)
    degraded = estimate_cost("deepseek", 1000, 200)
    cached = estimate_cost("qwen", 0, 200)
    print(f"按首选 qwen 估算={naive:.4f} 元")
    print(f"降级到 deepseek 实际={degraded:.4f} 元（账单主体是实际 provider）")
    print(f"缓存命中时仅输出 token 计费={cached:.4f} 元（不等于模型降价）")


def demo_log_sanitization() -> None:
    raw = "api_key=FAKE-KEY-0001, token: FAKE-TOKEN, phone=13812345678"
    print("原文：", raw)
    print("脱敏：", sanitize(raw))


def demo() -> None:
    demo_three_concepts()
    demo_percentile_definition()
    demo_cost_attribution()
    demo_log_sanitization()


if __name__ == "__main__":
    demo()
