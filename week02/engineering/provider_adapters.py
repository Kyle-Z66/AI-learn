"""
第 2 周 · 动作 2：国内模型接入 —— 三厂商适配器 + Mock 客户端
================================================================
【对应知识点】文档第 2 周「国内模型接入」：通义千问 / DeepSeek / 智谱 GLM 各调一次

【周次学习要点】
  - 三家都提供 OpenAI 兼容接口：只需换 `base_url` + `model` + `api_key`，调用代码完全一致。
  - 用第 1 周 07_protocol.py 学到的 Protocol 定义统一接口 `LLMProvider`，为第 3 周 P1 网关铺垫。
  - MockProvider 让本周所有样例/测试**无 API Key 也能跑**；真实调用只需 `get_provider(name)`。

【易忽略细节 / 对照文档补足】
  1. 文档要求"了解价格与上下文差异"，但价格随时变动 —— 代码只固化接入方式和官网查询入口，
     **不硬编码价格数字**（延续第 1 周"配置外置"思想）。
  2. 价格/上下文窗口的 `*_hint` 字段只是参考，实际以厂商官网为准。
  3. 真实客户端的 messages 参数是 SDK 的 TypedDict 列表，与我们的 dict[str, str] 类型不同，
     用 cast 桥接并注明原因。
  4. MockProvider 可注入 `fail_times`，专门用来验证第 4 个任务的"失败→重试→恢复"链路。
  5. 环境变量名固定：`DASHSCOPE_API_KEY` / `DEEPSEEK_API_KEY` / `ZHIPU_API_KEY`。

【示例用途】被 engineering_demo.py / structured_output / prompt_lab 引用；
             CLI 运行 `python -m week02.engineering.engineering_demo`
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Protocol, cast


@dataclass(frozen=True)
class ModelConfig:
    """模型接入配置。价格不写死，只给出官网查询入口。"""

    name: str
    model_id: str
    base_url: str
    env_key: str
    context_window_hint: int  # 参考值，实际以官网为准
    pricing_url: str


QWEN_PLUS = ModelConfig(
    name="qwen",
    model_id="qwen-plus",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    env_key="DASHSCOPE_API_KEY",
    context_window_hint=128_000,
    pricing_url="https://help.aliyun.com/zh/model-studio/",
)
DEEPSEEK_CHAT = ModelConfig(
    name="deepseek",
    model_id="deepseek-chat",
    base_url="https://api.deepseek.com",
    env_key="DEEPSEEK_API_KEY",
    context_window_hint=64_000,
    pricing_url="https://api-docs.deepseek.com/",
)
GLM_4_PLUS = ModelConfig(
    name="glm",
    model_id="glm-4-plus",
    base_url="https://open.bigmodel.cn/api/paas/v4",
    env_key="ZHIPU_API_KEY",
    context_window_hint=128_000,
    pricing_url="https://open.bigmodel.cn/",
)

CONFIGS = {c.name: c for c in (QWEN_PLUS, DEEPSEEK_CHAT, GLM_4_PLUS)}


@dataclass(frozen=True)
class ChatResponse:
    """统一响应对象：内容 + 实际模型 + 用量 + 结束原因（第 3 周会扩展成本估算）。"""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    finish_reason: str


class LLMProvider(Protocol):
    """统一 LLM 客户端接口 —— 复用第 1 周 07_protocol.py 的 Protocol 模式。"""

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0,
        max_tokens: int = 512,
        **opts: Any,
    ) -> ChatResponse: ...


class MockProvider:
    """无 Key 可跑的模拟客户端：按规则从输入抽取字段，可注入前 N 次失败。"""

    def __init__(self, config: ModelConfig, fail_times: int = 0) -> None:
        self.config = config
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
            # 模拟"模型返回了非法 JSON"，用于验证重试链路
            return ChatResponse("{invalid json", self.config.model_id, 10, 5, "stop")

        user_text = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
        content = self._extract_ticket(user_text)
        return ChatResponse(content, self.config.model_id, len(user_text) // 2, 30, "stop")

    @staticmethod
    def _extract_ticket(text: str) -> str:
        """极简规则抽取：返回与 structured_output/models.py 的 schema 对应的 JSON。"""
        import json

        system_match = re.search(r"系统\s*([A-Za-z0-9_-]+)", text)
        severity_match = re.search(r"级别\s*(\d)", text)
        users_match = re.search(r"(\d+)\s*人", text)
        return json.dumps(
            {
                "system_name": system_match.group(1) if system_match else "unknown",
                "severity": int(severity_match.group(1)) if severity_match else 3,
                "affected_users": int(users_match.group(1)) if users_match else 0,
            },
            ensure_ascii=False,
        )


class OpenAICompatProvider:
    """真实客户端：OpenAI SDK + 各家兼容端点。需配置对应环境变量。"""

    def __init__(self, config: ModelConfig) -> None:
        api_key = os.getenv(config.env_key)
        if not api_key:
            raise ValueError(
                f"请先设置环境变量 {config.env_key}（或 get_provider(..., use_mock=True)）"
            )
        # 延迟导入：Mock 模式不依赖 openai 包，也便于未配置 Key 时运行测试
        from openai import AsyncOpenAI

        self.config = config
        self.client = AsyncOpenAI(api_key=api_key, base_url=config.base_url)

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0,
        max_tokens: int = 512,
        **opts: Any,
    ) -> ChatResponse:
        resp = await self.client.chat.completions.create(
            model=self.config.model_id,
            messages=cast(Any, messages),  # SDK 用 TypedDict 列表，此处结构兼容
            temperature=temperature,
            max_tokens=max_tokens,
            **opts,
        )
        choice = resp.choices[0]
        usage = resp.usage
        return ChatResponse(
            content=choice.message.content or "",
            model=resp.model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            finish_reason=choice.finish_reason or "",
        )


def get_provider(name: str, use_mock: bool = False, fail_times: int = 0) -> LLMProvider:
    """工厂：按名称返回适配器。use_mock=True 时无需任何 API Key。"""
    config = CONFIGS.get(name)
    if config is None:
        raise ValueError(f"未知模型：{name}，可选 {list(CONFIGS)}")
    if use_mock:
        return MockProvider(config, fail_times=fail_times)
    return OpenAICompatProvider(config)
