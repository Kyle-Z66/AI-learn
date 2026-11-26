"""
第 9 周 · 动手项目：模拟电网运维知识库语料
================================================================
【对应知识点】文档第 9 周：构造含专有名词的查询，对比混合召回

【周次学习要点】
  - 15 条教学模拟 chunk，覆盖型号、错误码、部门权限与失效条目。
  - 数据完全本地生成，不接真实系统、不引入 API Key、不伪造业务数据。
  - 与第 8 周向量实验语料独立，便于单独观察"专名召回"的增益。

【易忽略细节】
  1. source / dept / valid 都要进 Candidate，才能演示前置过滤。
  2. 同一型号故意放两条（有效 + 失效），用来验证 valid 过滤确实生效。
  3. chunk_id 稳定不变，REPORT 里的数字可复现、可逐条核对。

【示例用途】被 hybrid_lab/__main__.py 与 tests/week09/test_hybrid_lab.py 引用；
             可运行：`python -m week09.hybrid_lab`
"""
from __future__ import annotations

from week09.engineering.models import Candidate

CORPUS: list[Candidate] = [
    Candidate("c-01", "SGCC-4012 断路器巡检周期与温度阈值说明", "manual", "运维"),
    Candidate("c-02", "SGCC-4012 断路器常见机械故障排查流程", "manual", "运维"),
    Candidate("c-03", "SGCC-5200 隔离开关检修周期与操作注意事项", "manual", "运维"),
    Candidate("c-04", "ERR_4012 错误码表示通信链路超时，需检查串口连接", "error_codes", "运维"),
    Candidate("c-05", "ERR_5200 错误码表示传感器校准失败", "error_codes", "运维"),
    Candidate("c-06", "断路器巡检通用流程与现场安全注意事项", "manual", "运维"),
    Candidate("c-07", "变电站冬季防冻巡检要点与温湿度记录", "manual", "运维"),
    Candidate("c-08", "SGCC-4012 停用批次退运处理办法（历史文档）", "archive", "运维", False),
    Candidate("c-09", "国网设备型号命名规则与 SGCC 前缀含义", "glossary", "运维"),
    Candidate("c-10", "ERR_4012 历史工单汇总与重复报障识别", "tickets", "运维", False),
    Candidate("c-11", "设备巡检工单的部门审批流转规则", "process", "运维"),
    Candidate("c-12", "财务差旅报销标准与发票归档要求", "finance", "财务"),
    Candidate("c-13", "SGCC-4012 采购合同与资产登记编号规则", "finance", "财务"),
    Candidate("c-14", "API 网关错误码与重试策略说明", "error_codes", "研发"),
    Candidate("c-15", "WebSocket 连接断开后的消息补偿机制", "design", "研发"),
]


def build_corpus() -> list[Candidate]:
    """返回拷贝，避免实验过程修改共享语料。"""
    return [item.copy_without_scores() for item in CORPUS]


__all__ = ["CORPUS", "build_corpus"]
