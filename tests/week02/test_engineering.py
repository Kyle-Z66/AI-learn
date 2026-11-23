"""
第 2 周单元测试 · 动作 2：三厂商适配器与 Mock 客户端
"""
from __future__ import annotations

import pytest
from week02.engineering.provider_adapters import (
    CONFIGS,
    DEEPSEEK_CHAT,
    GLM_4_PLUS,
    QWEN_PLUS,
    MockProvider,
    OpenAICompatProvider,
    get_provider,
)
from week02.structured_output.models import TicketExtract


def test_three_providers_configured() -> None:
    assert set(CONFIGS) == {"qwen", "deepseek", "glm"}
    assert QWEN_PLUS.model_id == "qwen-plus"
    assert DEEPSEEK_CHAT.model_id == "deepseek-chat"
    assert GLM_4_PLUS.model_id == "glm-4-plus"
    assert all(c.env_key.endswith("_API_KEY") for c in CONFIGS.values())


def test_unknown_provider() -> None:
    with pytest.raises(ValueError):
        get_provider("not-exist", use_mock=True)


def test_mock_provider_output_valid() -> None:
    mock = get_provider("qwen", use_mock=True)
    assert isinstance(mock, MockProvider)
    assert mock.config.model_id == "qwen-plus"


async def test_mock_chat_injectable_failure() -> None:
    mock = MockProvider(DEEPSEEK_CHAT, fail_times=1)
    messages = [{"role": "user", "content": "系统 isc 故障，级别 3，影响 50 人"}]

    first = await mock.chat(messages)
    assert first.content == "{invalid json"  # 第一次故意失败

    second = await mock.chat(messages)
    parsed = TicketExtract.model_validate_json(second.content)
    assert parsed.system_name == "isc"
    assert parsed.severity == 3
    assert parsed.affected_users == 50


def test_real_provider_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    with pytest.raises(ValueError, match="DASHSCOPE_API_KEY"):
        OpenAICompatProvider(QWEN_PLUS)
