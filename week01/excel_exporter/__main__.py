"""
第 1 周 · 动手项目：Excel 批量导出器 —— 可运行入口
================================================================
【对应知识点】本周三个动作的综合运用：dataclass / asyncio / 线程池 / 上下文管理器

【示例用途】从仓库根目录运行：`python -m week01.excel_exporter`
运行后会在本目录下生成 output/DEMO-EXPORT.zip，内含多个分片 xlsx。
"""
from __future__ import annotations

import asyncio
import zipfile
from pathlib import Path

from week01.excel_exporter.exporter import export_excel
from week01.excel_exporter.models import ExportRow, ExportTask

OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def build_sample_rows(count: int = 250) -> list[ExportRow]:
    """造一批样例数据（250 行 / 分片 100 → 预期 3 个 xlsx）。"""
    departments = ("研发部", "财务部", "运维部", "市场部")
    return [
        ExportRow(
            id=i,
            name=f"用户{i}",
            department=departments[i % len(departments)],
            amount=round(i * 1.5, 2),
            exported_at="2026-11-23 09:00:00",
        )
        for i in range(1, count + 1)
    ]


async def main() -> None:
    task = ExportTask(task_id="DEMO-EXPORT", rows=build_sample_rows())
    print("=== 第 1 周动手项目：Excel 批量导出器 ===")
    print(f"  任务 {task.task_id}：共 {len(task.rows)} 行，分片大小 100 → 预期 3 个分片")

    zip_bytes = await export_excel(task, chunk_size=100)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{task.task_id}.zip"
    output_path.write_bytes(zip_bytes)
    print(f"  已生成：{output_path}（{len(zip_bytes)} 字节）")

    with zipfile.ZipFile(output_path) as archive:
        print(f"  ZIP 内文件：{archive.namelist()}")
        first = archive.namelist()[0]
        with archive.open(first) as f:
            print(f"  {first} 前 120 字节（xlsx 二进制头）：{f.read(120)[:60]!r}...")


if __name__ == "__main__":
    asyncio.run(main())
