"""
第 2 周 · 动手项目：结构化输出 —— Pydantic 输出 schema
================================================================
【对应知识点】文档第 2 周「结构化输出」标准写法：Pydantic 定义 schema + Field 约束 + extra=forbid

【周次学习要点】
  - Pydantic 把 LLM 返回的文本变成有类型、有约束的 Python 对象，是结构化输出的核心工具。
  - `Field(ge=1, le=5)` 这类约束会在校验时强制执行，比在 prompt 里写"1-5 之间"可靠得多。
  - `extra="forbid"` 禁止模型返回多余字段，避免幻觉字段悄悄混进业务数据。

【易忽略细节 / 对照文档补足】
  1. 文档标准写法里的 `model_config` 配置照搬，其中 `json_schema_extra` 便于兼容 strict 模式。
  2. Pydantic v2 的校验入口是 `model_validate_json()`（v1 是 parse_raw），版本差异要分清。
  3. 校验失败抛 `ValidationError`，其字符串形式可以回灌给模型让它自我修正（见 extractor.py）。
  4. 类型注解 + dataclass 是第 1 周内容，这里不重复讲解，直接用于 schema 定义。

【示例用途】被 extractor.py / prompt_lab/runner.py 引用，不单独运行。
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class TicketExtract(BaseModel):
    """从报障文本中抽取的结构化信息（文档标准写法 + 完整约束）。"""

    system_name: str = Field(description="系统名称")
    severity: int = Field(ge=1, le=5, description="严重级别 1-5")
    affected_users: int = Field(ge=0, description="受影响用户数")

    model_config = {
        "extra": "forbid",  # 禁止多余字段
        "json_schema_extra": {"additionalProperties": False},
    }
