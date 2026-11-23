"""
第 2 周 · 模型 API 原理 04：streaming（流式输出）
================================================================
【对应知识点】文档第 2 周「模型 API 原理」第 4 项：streaming

【周次学习要点】
  - 流式输出用 SSE（Server-Sent Events）：服务端逐块推送 `data: {...}` 帧，客户端边收边显示。
  - 用户体验看的是**首 token 延迟**（Time To First Token），不是总耗时；流式能大幅降低前者。
  - 流式响应的最后一帧通常是 `data: [DONE]`，中间帧只带 delta（增量片段）。

【易忽略细节 / 对照文档补足】
  1. 文档仅列名，这里补足 SSE 帧的解析方式 —— 一帧可能跨多个 TCP 包，也可能一包含多帧，需按行切分。
  2. **流式默认不返回 token 用量**：OpenAI 兼容接口需传
     `stream_options={"include_usage": True}` 才给 usage。
  3. 流式下错误处理更难：中途断连时已输出的内容无法撤回，要有降级策略。
  4. 第 1 周的 asyncio 在这里直接用：真实客户端用 `async for chunk in stream` 消费。

【示例用途】可运行：`python week02/api_fundamentals/04_streaming.py`
"""
from __future__ import annotations

import json
import time


def parse_sse_lines(lines: list[str]) -> list[str]:
    """从 SSE 文本行中解析出 data 载荷；忽略注释行与 [DONE] 结束标记。

    真实 HTTP 流按行切分即可（SSE 以 \\n\\n 分帧，每行以 data: 开头）。
    """
    payloads: list[str] = []
    for line in lines:
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if data == "[DONE]":
            break
        payloads.append(data)
    return payloads


def build_sse_lines(tokens: list[str]) -> list[str]:
    """模拟服务端生成 SSE 帧（仅用于本地演示，无网络请求）。"""
    lines = [
        "data: " + json.dumps({"choices": [{"delta": {"content": tok}}]}, ensure_ascii=False)
        for tok in tokens
    ]
    lines.append("data: [DONE]")
    return lines


def demo_latency() -> None:
    """对比非流式（等全部完成）与流式（首块即显示）的感知延迟。"""
    tokens = ["大", "模", "型", " ", "API", " ", "入", "门"]

    start = time.perf_counter()
    _ = "".join(tokens)  # 非流式：所有内容生成完才一次性拿到
    total = time.perf_counter() - start

    start = time.perf_counter()
    first_chunk = tokens[0]  # 流式：第一块立即可用
    first = time.perf_counter() - start

    print(f"  非流式总耗时     : {total:.6f}s（用户要等全部生成）")
    print(f"  流式首 token 延迟: {first:.6f}s（用户立刻看到 '{first_chunk}'）")
    print("  真实场景差距是秒级：LLM 生成一个长回答要几秒，首 token 可能只要几百毫秒")


def main() -> None:
    print("=== 02 模型 API 原理 04：streaming ===")
    lines = build_sse_lines(["你", "好", "，", "世", "界"])
    payloads = parse_sse_lines(lines)
    content = "".join(
        json.loads(p)["choices"][0]["delta"]["content"] for p in payloads
    )
    print(f"  解析 {len(payloads)} 个 data 帧 → 拼接内容：{content}")
    print("  真实代码：async for chunk in stream: ")
    print("  print(chunk.choices[0].delta.content or '', end='')")
    print("  用量统计：传 stream_options={'include_usage': True}，最后一帧带 usage（补足点）")
    demo_latency()


if __name__ == "__main__":
    main()
