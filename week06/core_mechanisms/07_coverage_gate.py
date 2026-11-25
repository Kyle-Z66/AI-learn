"""
第 6 周 · 核心机制 07：覆盖率口径与门禁
================================================================
【对应知识点】文档第 6 周验收卡：有单测，覆盖率 > 60%

【周次学习要点】
  - pytest-cov 默认统计**行覆盖**；分支覆盖要 `--cov-branch`，两个数字不能混讲。
  - `--cov-fail-under=60` 把覆盖率变成 CI 门禁，低于阈值直接失败。
  - 覆盖率只是"哪些行跑过"，不是"逻辑是否正确"；仍需断言行为。

【易忽略细节】
  1. 文档只写 ">60%"，没说口径 → 本工程明确行覆盖 + 单独报告分支覆盖。
  2. 统计范围要写清（`--cov=week06`），否则把 site-packages 算进去会虚高。
  3. 未覆盖文件用 `--cov-report=term-missing` 定位行号，别凭感觉补测试。

【示例用途】可运行：`python -m week06.core_mechanisms.07_coverage_gate`
             实际门禁命令见 week06/README.md
"""
from __future__ import annotations


def coverage_rate(covered: int, total: int) -> float:
    """覆盖率 = 已执行行 / 可执行行；total=0 时返回 0。"""
    return covered / total if total else 0.0


def demo() -> None:
    example = coverage_rate(183, 250)
    print(f"示例：183/250 行 → 行覆盖率 {example:.1%}（>60% 达标）")
    print("分支覆盖需另加 --cov-branch，分母变成分支数，数值通常更低")
    print("门禁命令：uv run pytest --cov=week06 --cov-report=term-missing "
          "--cov-fail-under=60")


if __name__ == "__main__":
    demo()
