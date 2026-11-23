"""
第 2 周 · LLM 特有的认知误区（8 个坑，对齐第 1 周 six_pitfalls.py 的组织形式）
================================================================
【对应知识点】文档第 2 周学习目标「理解 LLM 的非确定性」及四个任务中隐含的风险点；
              文档未单列"坑"清单，本文件把散落在各处的风险系统化。

【周次学习要点】
  ① temperature=0 ≠ 确定  ② token ≠ 字符  ③ 输入+输出共享窗口
  ④ max_tokens 截断不报错  ⑤ 只靠 prompt 要 JSON 不可靠  ⑥ 重试不回灌错误
  ⑦ 不区分可重试/不可重试错误  ⑧ function calling 当结构化输出

【易忽略细节】
  - 每个坑都给"❌ 错误认知 vs ✅ 正确做法"的可运行对照。
  - 这些坑在第 3 周做 P1 网关时会集中暴露，本周先把认知立住。

【示例用途】可运行：`python -m week02.pitfalls.llm_pitfalls`
             （动态加载包内模块，须从仓库根以 -m 运行）
"""
from __future__ import annotations

import importlib
import json
from typing import Any, cast

# 数字前缀脚本不能用 import 语句直接导入（Python 语法限制），用 importlib 动态加载。
# 这与第 1 周 tests/week01/test_language_features.py 的做法一致。
_nd = cast(Any, importlib.import_module("week02.api_fundamentals.09_non_determinism"))
sample_outputs = _nd.sample_outputs
consistency_report = _nd.consistency_report


def pitfall_1() -> None:
    print("  [坑1 以为 temperature=0 就确定]")
    outputs = sample_outputs("抽取系统名", n=10, temperature=0.0)
    common, ratio = consistency_report(outputs)
    print("    ❌ 错误：设了 0 就跑一次验过没问题")
    print(f"    ✅ 正确：10 次里最常见结果只占 {ratio:.0%} → 仍要 schema 校验 + 重试兜底")


def pitfall_2() -> None:
    text = "大模型应用开发"
    print("  [坑2 token 当字符数]")
    print(f"    ❌ 错误：按 {len(text)} 个字符估算用量")
    print("    ✅ 正确：按 token 计（中文常 1~2 字符/token），见 01_tokenization.py")


def pitfall_3() -> None:
    print("  [坑3 忽略输入+输出共享窗口]")
    print("    ❌ 错误：输入刚好塞满窗口，再要 500 token 输出")
    print("    ✅ 正确：max_tokens 必须为输出预留空间，见 02_context_window.py 的 can_fit()")


def pitfall_4() -> None:
    print("  [坑4 不检查 finish_reason]")
    print("    ❌ 错误：拿到 content 就当完整结果用")
    print("    ✅ 正确：finish_reason='length' 表示被 max_tokens 截断，必须处理")


def pitfall_5() -> None:
    print("  [坑5 只靠 prompt 说'返回 JSON']")
    print("    ❌ 错误：system 里写'只输出 JSON'就信任结果")
    print("    ✅ 正确：response_format + Pydantic schema 双重约束，见 structured_output/")


def pitfall_6() -> None:
    print("  [坑6 重试不回灌错误原因]")
    print("    ❌ 错误：把原始 prompt 原样重发，模型继续犯同样的错")
    print("    ✅ 正确：把 ValidationError 文本拼进下一轮 user 消息（文档标准写法）")


def pitfall_7() -> None:
    print("  [坑7 不区分错误类型]")
    retryable = {429: "限流", 500: "服务端错误", 503: "暂时不可用"}
    non_retryable = {400: "参数错误", 401: "鉴权失败", 404: "模型不存在"}
    print("    ❌ 错误：所有异常一律重试 3 次")
    print(f"    ✅ 正确：可重试 {retryable}；不可重试 {non_retryable}（重试也白费）")


def pitfall_8() -> None:
    tool_schema = {"name": "query_alert_count", "type": "function"}
    print("  [坑8 function calling 当结构化输出]")
    print(f"    工具定义：{json.dumps(tool_schema, ensure_ascii=False)}")
    print("    ❌ 错误：以为两者都是'返回 JSON'就混用")
    print("    ✅ 正确：工具调用要真的执行函数；结构化输出只要符合 schema 的回答")


def main() -> None:
    print("=== 第 2 周：LLM 特有的 8 个认知误区 ===")
    for fn in (
        pitfall_1, pitfall_2, pitfall_3, pitfall_4,
        pitfall_5, pitfall_6, pitfall_7, pitfall_8,
    ):
        fn()


if __name__ == "__main__":
    main()
