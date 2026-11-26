"""
第 11 周 · 核心机制 05：拒答模板与拒答的语义
================================================================
【对应知识点】文档第 11 周：上下文不足时必须明确说"信息不足"，而不是编

【周次学习要点】
  - 拒答是正确行为，不是系统故障：它把"不知道"显式化，避免下游拿编造值做决策。
  - 文案统一由模板产出，前端可以按前缀识别，指标也能单独统计拒答率。
  - 三种常见触发：无入选片段、检索不相关、后校验发现答案无证据支撑。

【易忽略细节】
  1. 拒答也要给原因（"信息不足：检索结果与问题不相关"），
     只有一句"抱歉"会让用户反复重试，排障时也没有线索。
  2. 不要把拒答包装成"可能是……"的猜测语气：那等于把幻觉合法化。
  3. Java 里常用自定义异常；这里用普通值 + refused 标志，
     HTTP 层仍是 200（业务拒答），区别于系统错误 5xx。

【示例用途】可运行：`python -m week11.core_mechanisms.05_refusal_template`
             测试见 tests/week11/test_core_mechanisms.py
"""
from __future__ import annotations

from week11.engineering.guards import make_refusal

REFUSAL_REASONS: tuple[str, ...] = (
    "上下文为空，没有任何可引用证据",
    "检索结果与问题不相关",
    "答案中的关键数字未在上下文中出现",
)


def demo() -> None:
    for reason in REFUSAL_REASONS:
        print(make_refusal(reason))
    print("\n共同点：固定前缀“信息不足” + 可观测原因；不输出猜测性结论。")


if __name__ == "__main__":
    demo()
