"""
第 6 周 · 工程层：依赖注入容器（把前五周组件组装成服务）
================================================================
【对应知识点】文档第 6 周 P1 收尾：可交付的服务形态

【周次学习要点】
  - 容器只负责"组装"，不实现业务逻辑：网关来自第 3 周，熔断/审计/指标来自第 5 周。
  - FastAPI 的 Depends 从容器取实例；测试用 dependency_overrides 换成假实例。
  - 单例容器保证审计库、指标收集器在多次请求间共享。

【易忽略细节 / 对照文档补足】
  1. 文档没提依赖注入 → 补足：全局单例要可重置，否则测试之间会串数据。
  2. 容器里放 SQLiteAuditStore 内存库；生产换成文件库只需改 build_container 一处。
  3. breakers 按配置顺序创建，/readyz 才能逐个读状态。

【示例用途】被 app.py / core_mechanisms/03 引用；测试见 tests/week06/test_engineering.py
"""
from __future__ import annotations

from dataclasses import dataclass

from week03.engineering.gateway_protocol import GatewayConfig
from week03.p1_gateway.gateway import P1Gateway
from week05.engineering.audit import SQLiteAuditStore
from week05.engineering.circuit_breaker import BreakerConfig, CircuitBreaker
from week05.engineering.metrics import MetricsCollector


@dataclass
class ServiceContainer:
    """一次服务生命周期内共享的组件集合。"""

    gateway: P1Gateway
    config: GatewayConfig
    breakers: dict[str, CircuitBreaker]
    audit: SQLiteAuditStore
    metrics: MetricsCollector


def build_container() -> ServiceContainer:
    """组装容器：默认 Mock 模式，无 API Key 即可完整运行。"""
    config = GatewayConfig(use_mock=True)
    return ServiceContainer(
        gateway=P1Gateway(config),
        config=config,
        breakers={
            name: CircuitBreaker(name, BreakerConfig()) for name in config.order
        },
        audit=SQLiteAuditStore(),
        metrics=MetricsCollector(),
    )


_container: ServiceContainer | None = None


def get_container() -> ServiceContainer:
    """FastAPI Depends 的目标函数：第一次调用时惰性创建单例。"""
    global _container
    if _container is None:
        _container = build_container()
    return _container


def reset_container() -> None:
    """测试用：清空单例，避免上一用例的审计/指标污染下一用例。"""
    global _container
    _container = None


__all__ = ["ServiceContainer", "build_container", "get_container", "reset_container"]
