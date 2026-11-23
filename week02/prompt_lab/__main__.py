"""
第 2 周 · 动作 3：Prompt 对比实验 —— 可运行入口
================================================================
【对应知识点】文档第 2 周「Prompt 工程实战」：10 个 Prompt 版本对比

【示例用途】从仓库根目录运行：`python -m week02.prompt_lab`
运行后输出各版本的结构校验通过率；结论整理在 prompt_lab/REPORT.md
"""
from __future__ import annotations

import asyncio

from week02.prompt_lab.runner import run_experiment


async def main() -> None:
    print("=== 第 2 周动作 3：10 个 Prompt 版本对比实验 ===")
    print("  任务：从技术文档抽取 system_name / severity / affected_users")
    print("  指标：输出通过 Pydantic schema 校验的比例（越高越稳）")
    print("  样本：3 条 × 每版本 20 次 = 60 次/版本，固定随机种子可复现\n")

    results = await run_experiment(runs_per_sample=20)
    print(f"  {'版本':<14}{'通过率':>8}{'通过/总次数':>14}")
    print(f"  {'-' * 36}")
    for r in results:
        print(f"  {r.version:<14}{r.valid_rate:>7.0%}{f'{r.valid_count}/{r.total}':>14}")

    best = results[0]
    worst = results[-1]
    print(f"\n  最稳：{best.version}（{best.valid_rate:.0%}）")
    print(f"  最差：{worst.version}（{worst.valid_rate:.0%}）")
    print("  详细分析见 prompt_lab/REPORT.md")
    print("  这是教学模拟；换成真实 API 只需替换 runner.py 中的 provider")


if __name__ == "__main__":
    asyncio.run(main())
