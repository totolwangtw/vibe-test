"""通用 CSV 导入导出工具

为各业务模块提供：
- export_csv(rows, fields)  -> CSV 字符串
- import_csv(text, fields)  -> 解析为 dict 列表

设计原则：
- 字段以 (字段名, 显示列名) 元组传入
- 导入时只识别显示列名或字段名
- 日期统一以 YYYY-MM-DD 字符串保存
- 富文本字段会被去除 HTML 标签后导出
"""
from __future__ import annotations

import csv
import io
import re
from datetime import date, datetime
from typing import Any, Iterable


_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(s: str | None) -> str:
    if not s:
        return ""
    return _TAG_RE.sub("", s).strip()


def _coerce(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.isoformat() if not isinstance(value, datetime) else value.strftime("%Y-%m-%d %H:%M")
    if isinstance(value, (list, dict, set)):
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def export_csv(rows: Iterable[Any], fields: list[tuple[str, str]]) -> str:
    """生成 CSV 字符串（带 BOM 以兼容 Excel 中文）"""
    buf = io.StringIO()
    buf.write("\ufeff")  # UTF-8 BOM，Excel 中文不乱码
    writer = csv.writer(buf, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    writer.writerow([label for _, label in fields])
    for row in rows:
        if hasattr(row, "__dict__") and not isinstance(row, dict):
            data = {}
            for key, _ in fields:
                v = getattr(row, key, None)
                # 富文本字段去标签
                if key.endswith(("_html", "_content")):
                    v = _strip_html(v)
                data[key] = v
        else:
            data = row
        writer.writerow([_coerce(data.get(k)) for k, _ in fields])
    return buf.getvalue()


def parse_csv(text: str, fields: list[tuple[str, str]]) -> list[dict]:
    """解析 CSV 文本，按字段名或列名匹配"""
    # 去 BOM
    if text.startswith("\ufeff"):
        text = text[1:]
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        return []
    header = [h.strip() for h in rows[0]]
    # 建立列索引：先匹配列名，再匹配字段名
    name_to_field = {label: key for key, label in fields}
    name_to_field.update({key: key for key, _ in fields})
    col_index: dict[int, str] = {}
    for i, h in enumerate(header):
        if h in name_to_field:
            col_index[i] = name_to_field[h]
    result: list[dict] = []
    for line in rows[1:]:
        if not any(cell.strip() for cell in line):
            continue
        item: dict[str, Any] = {}
        for i, value in enumerate(line):
            key = col_index.get(i)
            if not key:
                continue
            v = value.strip()
            if not v:
                continue
            # 尝试转日期
            if key.endswith(("_date", "raised_date", "due_date", "request_date", "plan_date", "implement_date", "log_date", "meeting_date")):
                try:
                    item[key] = datetime.strptime(v[:10], "%Y-%m-%d").date()
                except ValueError:
                    pass
            elif key in ("planned_hours", "actual_hours", "hours", "progress", "sort_order"):
                try:
                    item[key] = float(v)
                except ValueError:
                    pass
            elif key in ("is_starred", "collapsed"):
                item[key] = v.lower() in ("true", "1", "yes", "是")
            elif key in ("parent_id", "owner_id", "requester_id", "member_id", "project_id", "meeting_id", "assignee_id"):
                try:
                    item[key] = int(v)
                except ValueError:
                    pass
            else:
                item[key] = v
        result.append(item)
    return result
