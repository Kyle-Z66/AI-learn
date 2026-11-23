"""
第 1 周 · 动手项目：Excel 批量导出器 —— 数据模型
================================================================
【对应知识点】dataclass（差异点 02）+ 类型注解（差异点 01）+ 可变默认值坑（坑 #1）

【周次学习要点】
  - 用 dataclass 定义数据模型，等价于 Java 的 DTO / POJO，省去手写 __init__。
  - frozen=True 让 ExportRow 不可变（类似 Java record），适合作为数据载体。
  - 列表字段必须用 field(default_factory=list)，绝不能写 rows: list[...] = []。

【易忽略细节】
  - frozen 只是"浅冻结"：内部若有可变对象仍可被修改；此处 ExportRow 全是标量/字符串，安全。
  - 字段类型注解会被 mypy 检查，但运行时不强制（见 01_type_annotations.py）。

【示例用途】被 exporter.py / __main__.py 引用，不单独运行。
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ExportRow:
    """一行待导出的数据。"""

    id: int
    name: str
    department: str
    amount: float
    exported_at: str


@dataclass
class ExportTask:
    """一次导出任务：持有待导出的行数据。

    对应 Java 侧的导出请求对象，这里用 default_factory 避免可变默认参数坑。
    """

    task_id: str
    rows: list[ExportRow] = field(default_factory=list)
