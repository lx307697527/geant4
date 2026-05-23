"""JSON and human-readable output formatters."""

from __future__ import annotations

import json
from typing import Any


def output_json(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str, ensure_ascii=False))


def output_table(rows: list[dict], headers: list[str]) -> None:
    if not rows:
        print("(no data)")
        return
    col_widths = {h: len(h) for h in headers}
    for row in rows:
        for h in headers:
            col_widths[h] = max(col_widths[h], len(str(row.get(h, ""))))

    fmt = "  ".join(f"{{:<{col_widths[h]}}}" for h in headers)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * col_widths[h] for h in headers]))
    for row in rows:
        print(fmt.format(*[str(row.get(h, "")) for h in headers]))
