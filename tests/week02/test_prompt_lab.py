"""
第 2 周单元测试 · 动作 3：10 个 Prompt 对比实验
"""
from __future__ import annotations

from week02.prompt_lab.prompts import PROMPTS
from week02.prompt_lab.runner import PromptLabProvider, run_experiment


def test_ten_prompts() -> None:
    assert len(PROMPTS) == 10
    assert all("{input}" in prompt for prompt in PROMPTS.values())
    assert "v10_综合版" in PROMPTS


def test_quality_score() -> None:
    provider = PromptLabProvider()
    score_bare = provider.quality_score(PROMPTS["v01_裸指令"])
    score_full = provider.quality_score(PROMPTS["v10_综合版"])
    assert score_full > score_bare
    assert 0 <= score_bare <= 1
    assert score_full <= 0.98


async def test_experiment_results() -> None:
    results = await run_experiment(runs_per_sample=5, seed=123)
    assert len(results) == 10
    assert all(0 <= r.valid_rate <= 1 for r in results)
    assert results[0].valid_rate >= results[-1].valid_rate
    assert results[0].version == "v10_综合版"
    assert all(r.total == 15 for r in results)
