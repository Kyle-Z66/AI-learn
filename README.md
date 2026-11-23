# AI-learn

记录 Python 和大模型功能的学习过程。

本仓库按**周**组织示例工程，配套《大模型应用开发能力补足 —— 20 周可执行学习计划》。每周目录包含该周每个动作的可运行样例代码、中文知识点注释与单元测试。

## 周索引

| 周次    | 主题                                | 目录                           | 状态      |
| ------- | ----------------------------------- | ------------------------------ | --------- |
| 第 1 周 | Python 语法速成（面向 Java 程序员） | [`week01/`](week01/README.md) | ✅ 已完成 |

> 后续周次将按同样结构追加：`week02/`、`week03/` ……

## 快速开始

推荐用 `uv` 管理依赖（学习计划指定的 2026 主流工具）。若你已习惯 Anaconda，两者可共存：**conda 负责解释器，uv 负责项目依赖**。

```bash
# 1. 同步依赖：uv 会自动创建 .venv 虚拟环境（对应"虚拟环境"知识点）
uv sync

# 2. 三件套验收（对应第 1 周验收标准第 1 条）
uv run ruff check .          # 代码规范检查（E/F/I/B/UP/SIM）
uv run mypy                  # 静态类型检查
uv run pytest                # 单元测试

# 3. 运行第 1 周任一知识点的可运行样例
uv run python week01/language_features/01_type_annotations.py
uv run python -m week01.excel_exporter        # 周末动手项目：Excel 批量导出器
```

> 若暂时不想装 uv，也可在已装好依赖的 Python 3.12+ 环境直接运行：
> `python -m pytest`、`python -m ruff check .`、`python -m mypy`。

## 目录结构

```
AI-learn/
├── pyproject.toml              # uv 项目元数据 + ruff/mypy/pytest 统一配置
├── week01/                     # 第 1 周：Python 语法速成（面向 Java 程序员）
│   ├── README.md               # 本周目标 / 动作 / 知识点对照 / 验收标准
│   ├── language_features/      # 动作 1：10 个语言差异点（逐个可运行）
│   ├── pitfalls/               # 文档要求的 6 个坑 + 文档未展开的补足要点
│   ├── engineering/            # 动作 2：工程规范的可运行示范
│   └── excel_exporter/         # 动作 3：Excel 批量导出器（asyncio + 线程池 + ZIP）
└── tests/week01/               # 第 1 周单元测试
```

## 约定

- 每个样例文件头部都有中文文档字符串，标注**对应知识点 / 周次要点 / 易忽略细节 / 示例用途**。
- 关键代码行用中文注释说明「为什么」而不仅是「做什么」，尤其针对 Java → Python 的思维差异。
- `week01/README.md` 的对照表区分「文档原有知识点」与「对照文档补足的内容」，补足项均标注来源。
