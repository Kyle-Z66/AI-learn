"""
第 12 周 · P2 项目：生成层（复用第 11 周工程层）
================================================================
【对应知识点】文档第 11 周生成可靠性 + 第 12 周 P2 可交付项目

【周次学习要点】
  - P2 不重写生成逻辑：直接复用 FakeGenerator（带引用 / 拒答 / 守卫）。
  - 真实接入时把这里换成 LLM 调用，引用的编号规则与守卫保持不变。
  - 生成层只认"已经排好序的 SourceChunk"，与检索配置解耦。

【易忽略细节】
  1. 不能为了"报告好看"把参考答案直接当生成结果：那叫数据泄漏，
     第 12 周评测必须用同一生成器对所有配置一视同仁。
  2. 温度为 0.1 且记录在 GeneratedAnswer 中，报告可追溯生成侧配置。
  3. Java 里常用 FactoryBean 注入生成器；这里用一个函数封装，
     测试可直接替换 FakeGenerator，不需要容器框架。

【示例用途】被 service.py / week12.engineering.runner.py 引用；不单独运行。
"""
from __future__ import annotations

from collections.abc import Sequence

from week11.engineering.context import build_context
from week11.engineering.generator import DEFAULT_TEMPERATURE, FakeGenerator
from week11.engineering.models import GeneratedAnswer, SourceChunk


def generate_answer(question: str, chunks: Sequence[SourceChunk]) -> GeneratedAnswer:
    """用第 11 周确定性生成器产出带引用答案；无证据时按统一模板拒答。"""
    bundle = build_context(list(chunks), max_tokens=2000)
    return FakeGenerator(temperature=DEFAULT_TEMPERATURE).generate(question, bundle)
