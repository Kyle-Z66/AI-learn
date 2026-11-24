"""
第 3 周 · 动手项目：P1 多模型统一网关核心逻辑
================================================================
【对应知识点】文档第 3 周 P1 v0.1：同一套代码调通 3 个模型 + 降级链 + 成本打印

【周次学习要点】
  - 网关本身不实现任何厂商协议：选模型、发请求、降级的活交给第 2 周适配器
    与第 3 周 Registry；网关只负责编排 + 统计 + 统一出口。
  - 这就是你 Java 侧"能力网关"的 Python 版本：协议在下、编排在中、统计在上。
  - 熔断、健康检查、调用审计是第 5 周内容，本周骨架不提前实现。

【易忽略细节 / 对照文档补足】
  1. 判断是否降级：比较实际使用的模型与配置首选，而不是靠异常回溯。
  2. 统计在成功/失败两条路径都要更新，否则账单与请求数对不上。
  3. 全部模型失败时向上抛 RuntimeError，由调用方决定重试还是返回降级内容。

【示例用途】被 __main__.py 调用；测试见 tests/week03/test_p1_gateway.py
"""
from __future__ import annotations

from week02.engineering.provider_adapters import LLMProvider

from week03.engineering.gateway_protocol import GatewayConfig, LLMResponse
from week03.engineering.provider_registry import ProviderRegistry
from week03.p1_gateway.models import CallRecord, GatewayRequest, GatewayStats


class P1Gateway:
    """多模型统一网关 v0.1：配置驱动 + 降级 + 统计。"""

    def __init__(
        self,
        config: GatewayConfig,
        overrides: dict[str, LLMProvider] | None = None,
    ) -> None:
        self.config = config
        self.registry = ProviderRegistry(config, overrides)
        self.stats = GatewayStats()

    async def chat(self, request: GatewayRequest) -> LLMResponse:
        """统一入口：上层只认识 GatewayRequest 与 LLMResponse。"""
        self.stats.total += 1
        try:
            response = await self.registry.chat(
                request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )
        except RuntimeError as exc:
            self.stats.records.append(
                CallRecord(provider="all", ok=False, latency_ms=0.0, error=str(exc))
            )
            raise

        provider = self.registry.last_used or "unknown"
        self.stats.succeeded += 1
        self.stats.total_cost += response.cost_yuan
        self.stats.records.append(
            CallRecord(provider=provider, ok=True, latency_ms=response.latency_ms)
        )
        if provider != self.config.order[0]:
            self.stats.fallback_used += 1  # 实际模型与首选不一致 → 发生了降级
        return response

    def report(self) -> str:
        """验收用的一行统计：请求数/成功数/降级次数/累计成本。"""
        return (
            f"请求 {self.stats.total} | 成功 {self.stats.succeeded} | "
            f"降级 {self.stats.fallback_used} | 累计成本 {self.stats.total_cost:.4f}"
        )
