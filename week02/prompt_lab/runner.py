"""
第 2 周 · 动作 3：Prompt 对比实验运行器
================================================================
【对应知识点】文档第 2 周「Prompt 工程实战」：10 个版本跑同一任务，看输出质量与稳定性差异

【周次学习要点】
  - 实验方法：固定样本 + 固定随机种子 + 每个版本重复多次 → 统计"校验通过率"。
  - 通过率 = 输出能被 Pydantic schema 接受的比例，是"稳定性"的可量化代理指标。
  - 结果告诉我们的不是"哪个 Prompt 文采好"，而是"哪个写法更可能产出合规结构"。

【易忽略细节 / 对照文档补足】
  1. 真实 LLM 的实验要调 API（有成本）；这里用 PromptLabProvider 按技巧点数量模拟，
     让实验**无 Key 也能跑通且可复现**。要把方法平移到真实 API，只需替换 provider。
  2. 随机种子固定，保证同一份代码每次得到相同结果（第 1 周 random 用法延续）。
  3. 只跑一次不能说明稳定性 —— 必须多样本 + 多重复，这正是文档强调"对比实验"的原因。

【示例用途】被 __main__.py 引用；可运行：`python -m week02.prompt_lab`
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass

from week02.engineering.provider_adapters import ChatResponse, MockProvider, get_provider
from week02.prompt_lab.prompts import PROMPTS
from week02.structured_output.models import TicketExtract

SAMPLES = (
    "系统 orchestrator 响应超时，级别 4，影响 250 名用户",
    "cyclone 数据库主从切换失败，级别 5，影响 1000 人",
    "isc 登录偶发 500，级别 2，影响 15 人",
)


class PromptLabProvider:
    """模拟客户端：Prompt 包含的质量信号越多，输出合规 JSON 的概率越高。

    真实实验换成 get_provider('qwen') 即可，runner 其余逻辑不变。
    """

    def __init__(self, seed: int = 42) -> None:
        self.rng = random.Random(seed)
        self.mock = get_provider("qwen", use_mock=True)

    @staticmethod
    def quality_score(prompt: str) -> float:
        """按 Prompt 中出现的关键技巧累加质量分（仅用于教学模拟）。"""
        score = 0.35  # 裸指令基线
        checks = (
            ("专家", 0.08),
            ("system_name", 0.12),
            ("JSON", 0.15),
            ("禁止", 0.08),
            ("示例", 0.12),
            ("<document>", 0.05),
            ("步骤", 0.05),
        )
        for keyword, weight in checks:
            if keyword in prompt:
                score += weight
        return min(score, 0.98)

    async def chat(self, messages: list[dict[str, str]], **opts: object) -> ChatResponse:
        prompt = messages[0]["content"]
        user_text = messages[-1]["content"]
        score = self.quality_score(prompt)

        if self.rng.random() < score:
            content = MockProvider._extract_ticket(user_text)
        else:
            # 模拟不稳定输出：自然语言、中文数字、多余解释等，均会被 schema 拒绝
            content = self.rng.choice(
                [
                    f"系统信息：{user_text}",
                    "{\"system_name\": \"x\", \"severity\": \"四\", \"affected_users\": 1}",
                    "抱歉，我无法完成该任务。",
                    json.dumps({"system_name": "x", "severity": 9, "affected_users": -1}),
                ]
            )
        return ChatResponse(content, "mock-prompt-lab", len(user_text) // 2, 20, "stop")


@dataclass(frozen=True)
class ExperimentResult:
    version: str
    valid_rate: float
    valid_count: int
    total: int


async def run_experiment(runs_per_sample: int = 20, seed: int = 42) -> list[ExperimentResult]:
    """对 10 个版本 × 3 个样本 × N 次重复跑实验，返回按通过率排序的结果。"""
    provider = PromptLabProvider(seed=seed)
    results: list[ExperimentResult] = []

    for version, template in PROMPTS.items():
        valid = 0
        total = 0
        for sample in SAMPLES:
            prompt = template.format(input=sample)
            for _ in range(runs_per_sample):
                response = await provider.chat(
                    [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": sample},
                    ]
                )
                total += 1
                try:
                    TicketExtract.model_validate_json(response.content)
                    valid += 1
                except Exception:
                    # 实验中把任何解析/校验失败都计为"不稳定"
                    continue
        results.append(ExperimentResult(version, valid / total, valid, total))

    return sorted(results, key=lambda r: r.valid_rate, reverse=True)
