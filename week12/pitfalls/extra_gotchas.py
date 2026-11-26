"""
第 12 周 · 补足要点：评测体系的认知边界与面试话术
================================================================
【对应知识点】文档第 12 周：评测集累加 / 宁少而精 / 消融价值 / CI 回归

【周次学习要点】
  - 评测集是随项目增值的资产：每次线上坏例都要沉淀成新 case，而不是修完就算。
  - golden set 宁少而精：100 条标清楚的难例胜过 1000 条随手生成的简单题。
  - 消融实验的话术要落到数字与代价，不能只背"混合检索更好"。

【易忽略细节】
  1. CI 回归是护栏不是成绩单：它只挡住退化，不等于"代码质量高"。
  2. 面试讲消融时，必须同时说清质量变化与延迟变化，以及按场景分流的决策。
  3. Java 团队常把测试集当一次性验收物；RAG 评测集要用版本号管理并持续累加。

【示例用途】可运行：`python -m week12.pitfalls.extra_gotchas`
             测试见 tests/week12/test_pitfalls.py
"""
from __future__ import annotations

ASSET_STEPS: tuple[str, ...] = (
    "线上坏例 → 复现问题 → 标注相关片段 → 加入评测集（带 case_id）",
    "每次发版跑同一套 case → 指标趋势可追溯",
    "评测集本身也要版本化，不能只版本化代码",
)

ABLATION_PITCH = (
    "我用同一套查询集做了四配置消融：先验证检索层贡献了多少 Recall，"
    "再看重排层带来的质量变化与延迟代价；最终按场景分流，"
    "而不是一律启用最贵的配置。"
)

GUARD_VS_SCOREBOARD = (
    ("CI 回归", "比较基线与当前，退化超阈值就失败", "护栏：防止变坏"),
    ("评测报告", "看四配置差异与分布", "成绩单：用于归因与选型"),
)


def demo_asset_accumulates() -> None:
    print("评测集是累加资产：")
    for index, step in enumerate(ASSET_STEPS, start=1):
        print(f"  {index}. {step}")


def demo_few_but_gold() -> None:
    print("宁少而精：100 条标注需要有来源、有规则、有难例；")
    print("随手生成 1000 条简单题只会把指标推到 1.000，掩盖真实问题。")


def demo_ablation_pitch() -> None:
    print("消融实验面试话术：", ABLATION_PITCH)
    print("讲的时候把真实数字补进去，并说明这些数字来自本地教学语料。")


def demo_guard_not_scoreboard() -> None:
    for name, behavior, meaning in GUARD_VS_SCOREBOARD:
        print(f"{name:<8} | {behavior:<24} | {meaning}")


def demo() -> None:
    demo_asset_accumulates()
    demo_few_but_gold()
    demo_ablation_pitch()
    demo_guard_not_scoreboard()


if __name__ == "__main__":
    demo()
