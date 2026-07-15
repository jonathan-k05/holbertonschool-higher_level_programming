"""Statistics computation for datasets stored as lists of row dicts.

CSV uploads store every cell as a string (e.g. "100"), while JSON uploads
store native types (e.g. 100). All numeric coercion is done defensively so
these functions work for both sources.
"""

import math
from typing import Any, Dict, List


def _to_float(value: Any):
    """Coerce a value to float, returning None if not numeric."""
    if value is None or isinstance(value, bool):
        return None
    try:
        val = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(val):
        return None
    return val


def compute_basic_stats(data: List[Dict], column_name: str) -> Dict[str, Any]:
    """Compute count/sum/mean/min/max for a single column.

    Values are coerced to float; non-numeric values are skipped. If no numeric
    values are found, all statistics are returned as zero.
    """
    values = []
    for row in data:
        numeric = _to_float(row.get(column_name))
        if numeric is not None:
            values.append(numeric)

    if not values:
        return {"count": 0, "sum": 0, "mean": 0, "min": 0, "max": 0}

    total = sum(values)
    count = len(values)
    return {
        "count": count,
        "sum": total,
        "mean": total / count,
        "min": min(values),
        "max": max(values),
    }


def compute_summary_stats(data: List[Dict]) -> Dict[str, Dict]:
    """Compute basic stats for every numeric column present in the data.

    All columns across all rows are considered (the union of keys), so numeric
    columns that appear only in later rows are still included. Non-numeric
    columns are skipped. Empty data returns an empty dict.
    """
    if not data:
        return {}

    columns = set()
    for row in data:
        columns.update(row.keys())

    summary: Dict[str, Dict] = {}
    for column in columns:
        stats = compute_basic_stats(data, column)
        if stats["count"] > 0:
            summary[column] = stats
    return summary
