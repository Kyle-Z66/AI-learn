"""
第 2 周 · 动作 2：工程规范示范 —— 三厂商配置与统一客户端
================================================================
【对应知识点】文档第 2 周「国内模型接入」：qwen-plus / deepseek-chat / glm-4-plus

【周次学习要点】
  - 三家 OpenAI 兼容接口仅差 base_url / model_id / api_key，用统一 LLMProvider 抽象屏蔽差异。
  - 配置外置：环境变量存 Key，代码不出现任何密钥；价格与窗口以官网为准，不硬编码。
  - Mock 与真实客户端实现同一 Protocol，测试用 Mock，生产用真实 —— 这是第 1 周鸭子类型的直接应用。

【易忽略细节】
  1. 本文件默认用 Mock，无 Key 可运行。要调真实 API，设置对应环境变量并把 use_mock 改为 False。
  2. 三家价格/上下文窗口随时调整，输出里给出官网入口，让你自己核实差异。
  3. 统一响应对象带 input_tokens/output_tokens/finish_reason，第 3 周会在此基础上加成本估算。

【示例用途】可运行：`python -m week02.engineering.engineering_demo`
"""
from __future__ import annotations

import asyncio

from week02.engineering.provider_adapters import CONFIGS, get_provider


async def main() -> None:
    print("=== 第 2 周动作 2：国内模型接入 ===")
    print("  三家配置（OpenAI 兼容模式）：")
    for config in CONFIGS.values():
        print(f"    {config.model_id:<16} base_url={config.base_url}")
        print(f"      {'':<16} Key 环境变量={config.env_key}")
        print(f"      {'':<16} 上下文参考={config.context_window_hint}")
        print(f"      {'':<16} 价格/窗口以官网为准：{config.pricing_url}")

    print("  用 Mock 客户端各调一次（无需 API Key）：")
    for name in CONFIGS:
        provider = get_provider(name, use_mock=True)
        response = await provider.chat(
            [
                {"role": "system", "content": "从文本抽取结构化信息"},
                {"role": "user", "content": "系统 orchestrator 故障，级别 4，影响 250 人"},
            ]
        )
        print(f"    [{response.model}] {response.content}")
        print(f"      usage: in={response.input_tokens} out={response.output_tokens}")
        print(f"      finish_reason={response.finish_reason}")

    print("  真实调用：设置 DASHSCOPE_API_KEY / DEEPSEEK_API_KEY / ZHIPU_API_KEY 后，")
    print("            改用 get_provider(name) 即可，其余代码完全不变（第 3 周做统一网关）")


if __name__ == "__main__":
    asyncio.run(main())
