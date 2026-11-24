"""
第 3 周 · 动作 2：模型注册表与降级链（复用第 2 周适配器）
================================================================
【对应知识点】文档第 3 周 P1 v0.1：基于配置切换模型，带降级链
              （DeepSeek 挂了自动切 Qwen）

【周次学习要点】
  - 三个 Provider 直接复用第 2 周 get_provider()：Not reinvent the wheel。
  - 降级链的最小骨架 = 优先级列表 + try/except + 统一响应；仅此而已。
  - 熔断、健康检查、调用审计是第 5 周内容，本周明确不做，避免提前挖坑。

【易忽略细节 / 对照文档补足】
  1. 文档只说"带降级链"，没说失败判据 → 这里以"调用抛异常"为失败信号。
  2. 降级后必须记录实际模型（LLMResponse.model），否则账单无法归因。
  3. 耗时用 perf_counter 而不是 time.time：系统时钟调整会污染结果。
  4. FaultInjectingProvider 只用于演示与测试，不参与真实调用。
  5. 未知模型名属配置错误（get_provider 抛 ValueError），不是降级场景，
     应让它在 try 之外快速失败，不要把所有异常都吞成 RuntimeError。

【示例用途】被 engineering_demo.py / p1_gateway 引用；
             测试见 tests/week03/test_engineering.py / test_p1_gateway.py
"""
from __future__ import annotations

import time
from typing import Any

from week02.engineering.provider_adapters import ChatResponse, LLMProvider, get_provider

from week03.engineering.gateway_protocol import GatewayConfig, LLMResponse, calculate_cost


class FaultInjectingProvider:
    """测试用装饰器：前 fail_times 次调用抛异常，模拟主模型不可用。"""

    def __init__(self, inner: LLMProvider, fail_times: int = 1) -> None:
        self.inner = inner
        self.fail_times = fail_times
        self.calls = 0

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0,
        max_tokens: int = 512,
        **opts: Any,
    ) -> ChatResponse:
        self.calls += 1
        if self.calls <= self.fail_times:
            raise ConnectionError("模拟主模型不可用")
        return await self.inner.chat(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **opts,
        )


class ProviderRegistry:
    """按配置优先级选择模型，失败则自动切换下一个。"""

    def __init__(
        self,
        config: GatewayConfig,
        overrides: dict[str, LLMProvider] | None = None,
    ) -> None:
        self.config = config
        self.overrides: dict[str, LLMProvider] = overrides or {}
        self.last_used: str | None = None

    def _provider(self, name: str) -> LLMProvider:
        """允许注入自定义 Provider（演示故障），生产路径仍走第 2 周工厂。"""
        if name in self.overrides:
            return self.overrides[name]
        return get_provider(name, use_mock=self.config.use_mock)

    async def chat(
        self,
        messages: list[dict[str, str]],
        **opts: Any,
    ) -> LLMResponse:
        """遍历优先级列表；全部失败才抛错，成功则封装统一响应。"""
        errors: list[str] = []
        for name in self.config.order:
            provider = self._provider(name)
            started = time.perf_counter()
            try:
                response = await provider.chat(messages, **opts)
            except Exception as exc:  # 降级链要兜住厂商侧各类异常
                errors.append(f"{name}: {exc}")
                continue

            latency_ms = (time.perf_counter() - started) * 1000
            price_in, price_out = self.config.pricing.get(name, (0.0, 0.0))
            cost = calculate_cost(
                response.input_tokens,
                response.output_tokens,
                price_in,
                price_out,
            )
            self.last_used = name
            return LLMResponse(
                content=response.content,
                model=response.model,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                latency_ms=latency_ms,
                cost_yuan=cost,
            )
        raise RuntimeError("所有模型均不可用：" + "；".join(errors))
