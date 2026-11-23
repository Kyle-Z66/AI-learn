"""
第 1 周 · 周末动手项目：Excel 批量导出器（核心逻辑）
================================================================
【对应知识点】文档第 1 周「动手项目」：模拟 Java AsynExcelExportUtil 的
分片 + 线程池 + ZIP 打包逻辑，Python 用 asyncio + ThreadPoolExecutor 实现。

【周次学习要点】
  - 分片（chunk）：把大列表切成小块，对应 Java 的分页/分片导出，避免一次性全量加载。
  - ThreadPoolExecutor：openpyxl 是同步阻塞库，放到线程池并行执行，避免阻塞事件循环。
  - asyncio.gather：并发等待所有分片完成；loop.run_in_executor：把同步函数桥接成协程。
  - ZIP 打包：把多个分片 xlsx 打成一个 zip 返回（与 Java 导出器一致）。

【易忽略细节】
  1. asyncio 本身不加速 CPU 密集任务；这里加速的是"生成多个独立 Excel 文件"的阻塞 IO，
     它们彼此无依赖，交给线程池才能真正并行（GIL 在 IO/IO 交互时会被释放）。
  2. openpyxl 的 Workbook.save() 需要 file-like 对象，用 io.BytesIO 在内存生成，
     避免落临时文件 —— 但超大文件仍应落盘，别无脑全内存。
  3. ThreadPoolExecutor 用 with 管理，退出时确保线程收尾；max_workers 不宜过大（线程切换成本）。

【示例用途】可运行入口：`python -m week01.excel_exporter`
"""
from __future__ import annotations

import asyncio
import io
import zipfile
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor

from openpyxl import Workbook

from week01.excel_exporter.models import ExportRow, ExportTask

DEFAULT_CHUNK_SIZE = 100
DEFAULT_MAX_WORKERS = 4
HEADERS = ("ID", "姓名", "部门", "金额", "导出时间")


def chunk_rows(rows: Sequence[ExportRow], size: int = DEFAULT_CHUNK_SIZE) -> list[list[ExportRow]]:
    """把行数据按 size 分片：对应 Java 的 Lists.partition / 分页导出。"""
    if size <= 0:
        raise ValueError("size 必须为正整数")
    return [list(rows[i : i + size]) for i in range(0, len(rows), size)]


def build_xlsx_bytes(sheet_name: str, rows: Sequence[ExportRow]) -> bytes:
    """在线程池中调用：用 openpyxl 同步生成一个 xlsx 的字节内容。"""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    sheet.append(HEADERS)
    for row in rows:
        sheet.append([row.id, row.name, row.department, row.amount, row.exported_at])

    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def write_chunk(task_id: str, index: int, rows: Sequence[ExportRow]) -> tuple[str, bytes]:
    """单个分片的处理函数（同步）：生成文件名 + xlsx 字节。"""
    filename = f"{task_id}_part{index}.xlsx"
    return filename, build_xlsx_bytes(f"part{index}", rows)


def build_zip(files: Sequence[tuple[str, bytes]]) -> bytes:
    """把多个 (文件名, 字节) 打包成一个 ZIP 的字节内容。"""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for filename, content in files:
            archive.writestr(filename, content)
    return buffer.getvalue()


async def export_excel(
    task: ExportTask,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    max_workers: int = DEFAULT_MAX_WORKERS,
) -> bytes:
    """主流程：分片 → 线程池并行生成 xlsx → ZIP 打包 → 返回 zip 字节。

    这是 Java 侧 AsynExcelExportUtil 的 Python 对应实现：
      - Java: CompletableFuture + 线程池 + ZipOutputStream
      - Python: asyncio + ThreadPoolExecutor + zipfile
    """
    chunks = chunk_rows(task.rows, chunk_size)
    loop = asyncio.get_running_loop()

    # with 确保线程池在退出时被关闭；run_in_executor 把同步函数包装成可 await 的 Future。
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        pending = [
            loop.run_in_executor(executor, write_chunk, task.task_id, index, chunk)
            for index, chunk in enumerate(chunks, start=1)
        ]
        results: list[tuple[str, bytes]] = list(await asyncio.gather(*pending))

    return build_zip(results)
