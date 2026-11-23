# uv 速查（结合 AI-learn 项目）

> 面向 Java 背景的 Python 学习者。uv 是 Astral 用 Rust 写的单一二进制工具，统一了 Python 版本、虚拟环境、依赖、锁文件、脚本运行和打包发布。本项目已是 uv 原生工程（`pyproject.toml` + `uv.lock` + `.venv`）。

## 一、本项目当前工作流

项目配置全在 `pyproject.toml` 一处：`[project]` 声明依赖、`[dependency-groups]` 放开发依赖、`[tool.ruff]` / `[tool.mypy]` / `[tool.pytest.ini_options]` 分别配置三件套。

```powershell
uv sync                       # 按 uv.lock 同步依赖，自动建/更新 .venv
uv lock --check               # CI 中校验 lock 是否过期
uv run ruff check .           # lint
uv run ruff format .          # 格式化
uv run mypy                   # 类型检查（files 已在 pyproject 配好）
uv run pytest -q              # 跑测试（asyncio_mode=auto）
uv run python week01/xxx.py   # 在隔离环境运行脚本，无需手动 activate
```

新增依赖的正确姿势：直接改 `pyproject.toml` 后 `uv sync`，或者用命令让 uv 自动维护两处：

```powershell
uv add openpyxl                       # 加到 [project].dependencies
uv add --dev ruff pytest              # 加到 [dependency-groups].dev
uv add "pydantic>=2.0,<3"             # 带版本约束
uv remove openpyxl                    # 同时更新 pyproject.toml + uv.lock
```

## 二、命令速查表

| 场景 | uv 命令 | 被替代的旧命令 |
|---|---|---|
| 初始化项目 | `uv init` | `mkdir` + 手写 pyproject |
| 同步依赖 | `uv sync` | `pip install -r requirements.txt` |
| 安装单个包 | `uv add <pkg>` | `pip install` + 手改 pyproject |
| 创建环境 | `uv venv --python 3.12` | `python -m venv .venv` |
| 运行脚本 | `uv run python main.py` | `source .venv/bin/activate && python` |
| 临时运行 CLI | `uvx ruff check .` | `pipx run` / `npx` 思路 |
| 锁定依赖 | `uv lock` | `pip-compile` / `poetry lock` |
| 编译 requirements | `uv pip compile in -o out` | `pip-compile` |
| 精确同步 | `uv pip sync requirements.txt` | `pip-sync` |
| 装 Python 版本 | `uv python install 3.12` | `pyenv install` |
| 固定项目版本 | `uv python pin 3.12` | `pyenv local` |
| 查看依赖树 | `uv pip tree` | `pipdeptree` |
| 构建/发布 | `uv build` / `uv publish` | `python -m build` / `twine` |
| 查看缓存目录 | `uv cache dir` | — |
| 清理缓存 | `uv cache clean` / `uv cache prune` | — |
| 自升级 | `uv self update` | `pip install -U uv` |

## 三、几个高频配方

单文件脚本带依赖声明（PEP 723），无需建项目：

```python
# /// script
# dependencies = ["requests>=2.25", "rich>=13"]
# ///
import requests
```

```powershell
uv run demo.py    # uv 自动建临时隔离环境并装好依赖
```

指定 Python 版本临时跑：

```powershell
uv run --python 3.10 --with pytest pytest -q
uv run --no-dev python main.py       # 不装开发依赖组
uv sync --group dev                  # 只装指定依赖组
uv export --no-dev -o requirements.txt  # 导出 requirements 给不支持 uv 的部署方
```

## 四、Poetry → uv 迁移对照

`pyproject.toml` 的结构变化（Poetry 私有格式 → PEP 621 标准）：

```toml
# 迁移前（Poetry）
[tool.poetry]
name = "ai-learn"
version = "0.1.0"
description = "..."
authors = ["Kyle <k@example.com>"]

[tool.poetry.dependencies]
python = "^3.12"
openpyxl = "^3.1.5"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

```toml
# 迁移后（uv / PEP 621）
[project]
name = "ai-learn"
version = "0.1.0"
description = "..."
requires-python = ">=3.12"
dependencies = ["openpyxl>=3.1.5,<4"]

[dependency-groups]
dev = ["pytest>=8.3"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

版本约束写法差异：`^1.2`（Poetry）→ `>=1.2,<2`（PEP 508）；`~1.2` → `>=1.2,<1.3`。

命令映射：`poetry install` → `uv sync`；`poetry add` → `uv add`；`poetry run` → `uv run`；`poetry lock` → `uv lock`；`poetry build` → `uv build`。`[tool.poetry.scripts]` → `[project.scripts]`。

迁移步骤：改 `pyproject.toml` → 删 `poetry.lock` → `uv lock` 重新生成 → `uv sync` → 跑一遍 `uv run pytest` 验证。注意 `uv.lock` 与 `poetry.lock` 不兼容，不能复用；迁移后依赖解析结果可能有细微差异，务必验证测试。

## 五、Windows 环境排坑（本机实测）

uv 装到 `%USERPROFILE%\.local\bin\uv.exe`，是独立二进制，**不依赖 Python**，所以 `python -m uv` 会报 `No module named uv`（本机 `python` 还被 LibreOffice 自带的解释器抢了 PATH 顺序）。

若从 DeskGo 桌面管理器启动 VS Code，VS Code 会继承 DeskGo 常驻进程的旧 PATH，导致终端找不到 uv。已在 `settings.json` 注入解决：

```json
"terminal.integrated.env.windows": {
  "PATH": "${env:PATH};C:\\Users\\kyle\\.local\\bin"
}
```

排查 PATH 继承链时用：

```powershell
Get-Command uv | Format-List Source
$p = Get-CimInstance Win32_Process -Filter "Name='Code.exe'" | Select-Object -First 1
Get-CimInstance Win32_Process -Filter "ProcessId=$($p.ParentProcessId)" | Select-Object Name, CreationDate
```

## 六、选型边界（uv 不是万能）

- 纯 Python 项目：直接 uv，2026 年新项目的默认答案。
- 非 Python 二进制依赖（CUDA、GDAL、C 库）：仍用 conda / mamba / pixi，uv 不管理这类系统级依赖。
- 受限环境不能装第三方工具：Python 自带的 `venv` 永远可用。
- 已有稳定运行的 Poetry 项目：不必强迁；要迁就按上面第四节走。
- uv 至今未发 1.0（本机 0.12.7），生产环境把版本固定下来更稳。
