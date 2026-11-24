"""
第 3 周 · 动作 2：网关协议与统一响应对象
================================================================
【对应知识点】文档第 3 周 P1 v0.1 目标：统一 LLM 客户端抽象 + 统一响应对象

【周次学习要点】
  - 这里不是重新定义 LLMProvider，而是把第 1 周 Protocol 与第 2 周适配器接口
    直接拿来用，只在上面补网关层需要的响应结构与成本计算。
  - 统一响应对象让上层业务不必关心"这次实际调了哪家模型"。
  - 成本公式 = 输入token/1000 × 输入单价 + 输出token/1000 × 输出单价。

【易忽略细节 / 对照文档补足】
  1. 单价从配置读，不硬编码：厂商调价时只改配置（第 2 周"配置外置"的延续）。
  2. frozen=True 的 dataclass 里字典字段必须用 field(default_factory=...)，
     否则会踩第 1 周讲过的"可变默认参数"同一个坑。
  3. 文档只说"成本估算"，没给公式；这里补足可执行的计算口径。

【示例用途】被 provider_registry.py / p1_gateway 引用，不单独运行。
             测试见 tests/week03/test_engineering.py
"""
from __future__ import annotations

from dataclasses import dataclass, field

from week02.engineering.provider_adapters import LLMProvider  # 复用第 1/2 周成果


@dataclass(frozen=True)
class LLMResponse:
    """网关统一响应：内容 + 实际模型 + 用量 + 耗时 + 成本。"""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_yuan: float


@dataclass(frozen=True)
class GatewayConfig:
    """网关配置：模型优先级、是否用 Mock、各模型单价（仅教学示意值）。"""

    order: tuple[str, ...] = ("deepseek", "qwen", "glm")
    use_mock: bool = True
    # 示意单价 (输入/千token, 输出/千token)；真实项目从配置或环境变量读
    pricing: dict[str, tuple[float, float]] = field(default_factory=lambda: {
        "qwen": (0.8, 2.0),
        "deepseek": (0.5, 1.0),
        "glm": (0.5, 1.5),
    })


def calculate_cost(
    input_tokens: int,
    output_tokens: int,
    price_in: float,
    price_out: float,
) -> float:
    """按 token 用量与单价计算成本，单位由外部配置决定。"""
    return input_tokens / 1000 * price_in + output_tokens / 1000 * price_out


__all__ = ["GatewayConfig", "LLMProvider", "LLMResponse", "calculate_cost"]
