"""
第 2 周 · 模型 API 原理 08：模型路由（Model Routing）
================================================================
【对应知识点】文档第 2 周「模型 API 原理」第 8 项：模型路由

【周次学习要点】
  - 模型路由：根据任务类型、成本、可用性、能力（是否支持工具调用）选择模型。
  - 降级链：主模型失败（限流/超时）时自动切备用模型，是生产可用性的基础。
  - 本周只做基础开关；第 3 周 P1 网关会把它做成统一的 Provider 抽象 + 完整降级链。

【易忽略细节 / 对照文档补足】
  1. 文档仅列名，这里补足"路由决策"和"降级链"的最小可运行版本，与第 3 周形成递进。
  2. 价格不要硬编码：各厂商随时调价，代码只保存"成本档位"，真实单价从配置外置传入。
  3. 降级时要记录实际使用的模型和成本，否则账单对不上。
  4. 不是所有模型都支持 function calling / JSON 模式，路由前要检查能力位。

【示例用途】可运行：`python week02/api_fundamentals/08_model_routing.py`
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelInfo:
    """模型能力描述。价格用档位而非具体数字，避免厂商调价后代码过时。"""

    name: str
    cost_tier: int  # 1=低 2=中 3=高，仅作相对比较
    supports_tools: bool
    context_window_hint: int  # 参考值，实际以官网为准


MODELS = (
    ModelInfo("deepseek-chat", 1, True, 64_000),
    ModelInfo("qwen-plus", 2, True, 128_000),
    ModelInfo("glm-4-plus", 2, True, 128_000),
)


def route(task: str, available: set[str], need_tools: bool = False) -> str | None:
    """路由：按任务选模型 —— 抽取用低成本，复杂推理用高能力；再按可用性过滤。"""
    preferred = {
        "extract": ["deepseek-chat", "qwen-plus", "glm-4-plus"],
        "reasoning": ["qwen-plus", "glm-4-plus", "deepseek-chat"],
    }.get(task, ["qwen-plus"])

    for name in preferred:
        if name not in available:
            continue
        model = next(m for m in MODELS if m.name == name)
        if need_tools and not model.supports_tools:
            continue
        return name
    return None


def fallback_chain(primary: str, available: set[str]) -> list[str]:
    """构造降级链：主模型排第一，其余按成本从低到高作为后备。"""
    chain = [primary]
    backups = sorted(
        (m.name for m in MODELS if m.name in available and m.name != primary),
        key=lambda name: next(m.cost_tier for m in MODELS if m.name == name),
    )
    return chain + backups


def main() -> None:
    print("=== 02 模型 API 原理 08：模型路由 ===")
    available = {"deepseek-chat", "qwen-plus", "glm-4-plus"}

    for task in ("extract", "reasoning", "unknown"):
        print(f"  {task:<10} → 路由到 {route(task, available)}")

    print(f"  主模型 deepseek-chat 的降级链：{fallback_chain('deepseek-chat', available)}")
    print("  路由结果和降级过程要打日志（实际用了哪个模型、成本多少），否则账单无法对账")
    print("  上下文窗口仅是参考值；价格与能力以各厂商官网为准（第 3 周做统一 Provider 抽象）")


if __name__ == "__main__":
    main()
