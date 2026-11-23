"""
第 2 周 · 动手项目：结构化输出 —— 可运行入口
================================================================
【对应知识点】文档第 2 周「结构化输出」：解析失败 → 回灌错误 → 最多 3 次重试

【示例用途】从仓库根目录运行：`python -m week02.structured_output`
默认用 MockProvider(fail_times=2)：前两次故意返回非法 JSON，第三次恢复，直观展示重试链路。
"""
from __future__ import annotations

import asyncio

from week02.engineering.provider_adapters import get_provider
from week02.structured_output.extractor import extract_with_retry


async def main() -> None:
    print("=== 第 2 周动手项目：Pydantic 结构化输出 + 错误回灌重试 ===")
    text = "系统 orchestrator 响应超时，级别 4，影响 250 名用户"

    # fail_times=2：模拟模型前两次输出非法 JSON，第三次才给合法结果
    provider = get_provider("qwen", use_mock=True, fail_times=2)
    print(f"  输入文本：{text}")
    print("  Mock 设置：前 2 次返回非法 JSON，验证自动重试与错误回灌")

    result = await extract_with_retry(text, provider, max_retries=3, verbose=True)
    print(f"  最终提取结果：{result.model_dump()}")
    print(f"  总共调用模型 {provider.calls} 次（前 2 次失败 + 第 3 次成功）")
    print("  真实场景把 get_provider(..., use_mock=True) 换成 get_provider('qwen') 即可")


if __name__ == "__main__":
    asyncio.run(main())
