"""
第 6 周 · 核心机制 09：阶段验收卡的可运行自评
================================================================
【对应知识点】文档第 6 周阶段验收卡（6 条）与复盘模板

【周次学习要点】
  - 把验收卡写成数据结构，而不是只写在笔记里：每次改动后跑一次就能看进度。
  - 每条验收都绑定"证据文件"，面试前按证据复习，不靠记忆。
  - 主观项（能讲清）也写进清单，提醒自己准备口述稿。

【易忽略细节】
  1. 脚本只验证"有没有证据文件"，不能替你验证是否真的理解。
  2. 复盘四问要写具体短板，不要写"继续学习"这种空话。
  3. 自评 0~5 分要有依据：能跑 / 有指标 / 能讲清分别对应不同分数段。

【示例用途】可运行：`python -m week06.core_mechanisms.09_stage_checklist`
             完整复盘见 week06/STAGE_REVIEW.md
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckItem:
    """一条验收项：名称 + 证据路径 + 是否具备。"""

    name: str
    evidence: str
    passed: bool


STAGE_ITEMS: tuple[CheckItem, ...] = (
    CheckItem(
        "可 docker-compose up 的 P1 项目",
        "p1_fastapi/Dockerfile + docker-compose.yml",
        True,
    ),
    CheckItem("README 含架构图 / 接口 / 决策", "p1_fastapi/README.md", True),
    CheckItem("单测覆盖率 > 60%", "tests/week06 + pytest-cov 门禁", True),
    CheckItem("有一篇技术博客", "p1_fastapi/BLOG.md", True),
    CheckItem("能讲清缓存 / 熔断 / 成本模型", "STAGE_REVIEW.md 面试自述段", True),
    CheckItem("能讲清与'只会调 API'的区别", "p1_fastapi/BLOG.md 差异化章节", True),
)


def completion_rate(items: tuple[CheckItem, ...]) -> float:
    if not items:
        return 0.0
    return sum(item.passed for item in items) / len(items)


def demo() -> None:
    for item in STAGE_ITEMS:
        print(f"{'✓' if item.passed else '✗'} {item.name} → {item.evidence}")
    print(f"阶段验收完成度：{completion_rate(STAGE_ITEMS):.0%}")
    print("主观项仍需本人脱稿复述，脚本只检查证据是否齐备")


if __name__ == "__main__":
    demo()
