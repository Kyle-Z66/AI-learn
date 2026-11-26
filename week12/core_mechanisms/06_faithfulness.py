"""
第 12 周 · 核心机制 06：Faithfulness（答案是否被上下文支持）
================================================================
【对应知识点】文档第 12 周：生成侧 Faithfulness 指标

【周次学习要点】
  - 复用第 11 周的答案数字抽取与实体校验：答案里的可核验声明逐条回查上下文。
  - 比例值便于跨配置比较；失败的具体声明由第 11 周 GuardResult 提供解释。
  - 无数字/实体时返回 1.0 并明确标注"无可核验声明"，不能假装做了深度语义判断。

【易忽略细节】
  1. 这是粗实现：改写、同义替换、上下文有误都会让它失真，
     生产应叠加 NLI 模型或人工抽检，别把它当裁判。
  2. [1][2] 引用编号必须在抽取时剔除（第 11 周已实现），否则指标虚高。
  3. Java 里常用规则引擎逐条评估；这里用函数式抽取 + 比例，
     逻辑与守卫同源，避免"评测说通过、线上守卫却拦下"的分裂。

【示例用途】可运行：`python -m week12.core_mechanisms.06_faithfulness`
             测试见 tests/week12/test_core_mechanisms.py
"""
from __future__ import annotations

from week12.engineering.metrics import faithfulness

CONTEXT = "系统 cyclone 的严重级别为 2 级，影响 30 名用户，负责人为张伟。"


def demo() -> None:
    answers = (
        "级别为 2 级，影响 30 名用户，负责人张伟 [1]。",
        "级别为 5 级，影响 30 名用户，负责人李四 [1]。",
        "信息不足，无法基于给定上下文回答。",
    )
    for answer in answers:
        score = faithfulness(answer, CONTEXT, entities=("张伟", "李四"))
        print(f"{score:.3f} ← {answer}")
    print("第三句没有可核验声明，按口径记 1.000，但绝不能说它'回答完整'。")


if __name__ == "__main__":
    demo()
