"""
第 12 周 · 本周特有坑：评测体系的四个高频翻车点
================================================================
【对应知识点】文档第 12 周：golden set / 指标 / 消融 / CI 化

【周次学习要点】
  - 造数据、拿测试集调参、只看均值、把延迟与质量混谈——四个都会让报告失去可信度。
  - 面试官会追问"评测集怎么来的""标注标准是什么"，诚实标注比漂亮数字更重要。
  - 延迟和质量是两个维度：rerank 提质量却拉高延迟，必须分开报告再谈取舍。

【易忽略细节】
  1. 本仓库 golden set 明确写"教学样例"，就是因为不能伪造真实业务数据。
  2. dev/holdout 划分要按 case_id 做确定性哈希/取模，不能随机到一半再改种子。
  3. Java 侧报表常只给 mean；这里强制输出分布，长尾案例才是优化线索。

【示例用途】可运行：`python -m week12.pitfalls.evaluation_pitfalls`
             测试见 tests/week12/test_pitfalls.py
"""
from __future__ import annotations

from statistics import median

from week12.engineering.golden_set import load_golden_set


def demo_fabricated_data() -> None:
    cases = load_golden_set()
    sources = {case.metadata.get("source", "") for case in cases}
    print("坑 1 · 造数据：")
    print("  本仓库标注来源：", sources)
    print("  教学样例必须标明；冒充真实业务数据会在面试追问下立刻穿帮。")


def demo_leakage() -> None:
    cases = load_golden_set()
    dev = [case for case in cases if int(case.metadata["case_id"][-1]) % 5 != 0]
    holdout = [case for case in cases if int(case.metadata["case_id"][-1]) % 5 == 0]
    print("坑 2 · 测试集泄漏：")
    print(f"  dev={len(dev)} holdout={len(holdout)}；调参只能用 dev，"
          "holdout 上只报一次最终数字。")


def demo_mean_only() -> None:
    stable = (0.7, 0.7, 0.7, 0.7, 0.7)
    skewed = (0.0, 0.0, 0.7, 1.0, 1.0)
    print("坑 3 · 只看平均分：")
    print(f"  均值都是 {sum(stable) / len(stable):.2f}，"
          f"但中位数 {median(stable):.2f} vs {median(skewed):.2f}，"
          f"最小 {min(stable):.2f} vs {min(skewed):.2f}。")


def demo_latency_vs_quality() -> None:
    print("坑 4 · 延迟与质量混谈：")
    print("  配置 A（示意）: Recall=0.80, p95=50ms")
    print("  配置 B（示意）: Recall=0.85, p95=300ms（示意结构，真实数字看 REPORT）")
    print("  质量与延迟必须分列；合成一个'综合分'会让取舍无法复盘。")


def demo() -> None:
    demo_fabricated_data()
    demo_leakage()
    demo_mean_only()
    demo_latency_vs_quality()


if __name__ == "__main__":
    demo()
