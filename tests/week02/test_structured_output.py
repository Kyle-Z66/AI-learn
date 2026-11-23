"""
第 2 周单元测试 · 动作 4：Pydantic schema 与错误回灌重试
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError
from week02.engineering.provider_adapters import MockProvider
from week02.structured_output.extractor import ProviderError, extract_with_retry, is_retryable
from week02.structured_output.models import TicketExtract


def test_schema_constraints() -> None:
    data = TicketExtract.model_validate_json(
        '{"system_name": "orchestrator", "severity": 4, "affected_users": 100}'
    )
    assert data.severity == 4

    with pytest.raises(ValidationError):
        TicketExtract.model_validate_json(
            '{"system_name": "x", "severity": 9, "affected_users": 1}'
        )
    with pytest.raises(ValidationError):
        TicketExtract.model_validate_json(
            '{"system_name": "x", "severity": 1, "affected_users": 1, "extra": 1}'
        )


def test_error_classification() -> None:
    assert is_retryable(ProviderError(429, "rate limit")) is True
    assert is_retryable(ProviderError(500, "server error")) is True
    assert is_retryable(ProviderError(400, "bad request")) is False
    assert is_retryable(ValueError("other")) is False


async def test_retry_recovers() -> None:
    from week02.engineering.provider_adapters import QWEN_PLUS

    # 注入前 2 次失败，验证第 3 次恢复
    provider = MockProvider(QWEN_PLUS, fail_times=2)
    result = await extract_with_retry(
        "系统 cyclone 故障，级别 5，影响 1000 人", provider, max_retries=3
    )
    assert result.system_name == "cyclone"
    assert provider.calls == 3


async def test_retry_exhausted() -> None:
    from week02.engineering.provider_adapters import QWEN_PLUS

    provider = MockProvider(QWEN_PLUS, fail_times=5)
    with pytest.raises(ValueError, match="结构化输出失败"):
        await extract_with_retry("系统 x 故障，级别 3，影响 1 人", provider, max_retries=2)
