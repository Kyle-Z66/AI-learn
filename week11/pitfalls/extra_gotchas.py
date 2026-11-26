"""
第 11 周 · 补足要点：生成环节的认知边界
================================================================
【对应知识点】文档第 11 周：生成 Prompt / 引用溯源 / 幻觉抑制（文档未展开的判断）

【周次学习要点】
  - 答案质量上限由检索决定：先修检索，再修生成，顺序反了会白调 Prompt。
  - 引用是 RAG 与普通 LLM 调用的关键差别：没有可追溯 [n] 就不算 RAG 交付。
  - 拒答率是健康指标：上升可能意味着检索变差，也可能意味着业务问题超范围。

【易忽略细节】
  1. "生成看起来变好了"常常只是切分/召回改了；做生成实验前要冻结检索配置。
  2. 引用编号只是指针，元数据（doc_id / 标题 / 页码）才是可审计资产。
  3. Java 团队常用"接口返回 code=0"判成功；RAG 要额外看 refused 与 guard，
     否则"成功返回的幻觉答案"会被当成正确结果入库。

【示例用途】可运行：`python -m week11.pitfalls.extra_gotchas`
             测试见 tests/week11/test_pitfalls.py
"""
from __future__ import annotations

FIX_ORDER: tuple[str, ...] = (
    "先确认正确片段是否进入 Top-K（检索侧）",
    "再确认预算是否把证据切掉（组装侧）",
    "最后才调 Prompt 与温度（生成侧）",
)

CITATION_VS_PLAIN: tuple[tuple[str, str, str], ...] = (
    ("普通 LLM 调用", "模型凭参数化知识作答", "无法回答'这句话出自哪页'"),
    ("RAG 带引用", "答案每个结论带 [n]", "可回溯到 doc_id / 标题 / 页码"),
)

REFUSAL_SIGNALS: tuple[tuple[str, str], ...] = (
    ("拒答上升 + 检索召回下降", "检索退化，先修检索"),
    ("拒答上升 + 召回正常", "问题确实超范围，拒答是正确的"),
    ("拒答为零", "反而可疑：可能预检阈值太松或守卫被绕过"),
)


def demo_fix_retrieval_first() -> None:
    print("排查顺序（不要跳步）：")
    for index, step in enumerate(FIX_ORDER, start=1):
        print(f"  {index}. {step}")


def demo_citation_is_the_difference() -> None:
    for kind, behavior, consequence in CITATION_VS_PLAIN:
        print(f"{kind:<14} | {behavior:<20} | {consequence}")


def demo_refusal_is_success() -> None:
    for signal, meaning in REFUSAL_SIGNALS:
        print(f"{signal:<24} → {meaning}")


def demo() -> None:
    demo_fix_retrieval_first()
    demo_citation_is_the_difference()
    demo_refusal_is_success()


if __name__ == "__main__":
    demo()
