"""Shared helpers for turning a results CSV plus a formatting spec into table cells.

Used by csv_to_apa_docx.py and csv_to_acl_latex.py so both venues format numbers
the same way.
"""

import json
from pathlib import Path

import pandas as pd

MINUS_SIGN = "−"
EM_DASH = "—"
STAR_THRESHOLDS = [(0.001, "***"), (0.01, "**"), (0.05, "*")]


def load_inputs(csv_path: Path, spec_path: Path) -> tuple[pd.DataFrame, dict]:
    """Read the CSV and the JSON spec, and check every spec column exists."""
    data = pd.read_csv(csv_path)
    spec = json.loads(Path(spec_path).read_text())
    missing = [col["source"] for col in spec["columns"] if col["source"] not in data]
    if missing:
        raise SystemExit(f"Spec columns not found in CSV: {missing}")
    return data, spec


def format_number(value: float, column: dict, use_unicode_minus: bool) -> str:
    """Round a number for display, following the column's spec."""
    decimals = column.get("decimals")
    if decimals is None:
        text = str(value)
    elif column.get("thousands_separator", False):
        text = f"{value:,.{decimals}f}"
    else:
        text = f"{value:.{decimals}f}"

    # APA: no leading zero for values that cannot exceed 1 (p, r, proportions)
    if not column.get("leading_zero", True):
        if text.startswith("0."):
            text = text[1:]
        elif text.startswith("-0."):
            text = "-" + text[2:]

    if use_unicode_minus and text.startswith("-"):
        text = MINUS_SIGN + text[1:]
    return text


def significance_stars(p_value: float) -> str:
    """Return *, **, or *** for a p-value, or an empty string."""
    if is_missing(p_value):
        return ""
    for threshold, stars in STAR_THRESHOLDS:
        if p_value < threshold:
            return stars
    return ""


def significance_note_pieces() -> list[tuple[str, bool]]:
    """The standard star legend as (text, is_italic) pieces, e.g. *p < .05."""
    pieces = []
    for threshold, stars in reversed(STAR_THRESHOLDS):
        pieces.append((stars, False))
        pieces.append(("p", True))
        pieces.append((f" < {str(threshold).lstrip('0')}. ", False))
    return pieces


def is_missing(value) -> bool:
    return value is None or (pd.api.types.is_scalar(value) and pd.isna(value))


def best_row_positions(data: pd.DataFrame, column: dict) -> set[int]:
    """Row positions holding the best value (after rounding), so ties are all marked."""
    direction = column.get("bold_best")
    if direction not in ("max", "min"):
        return set()
    values = pd.to_numeric(data[column["source"]], errors="coerce")
    decimals = column.get("decimals")
    if decimals is not None:
        values = values.round(decimals)
    target = values.max() if direction == "max" else values.min()
    return {position for position, value in enumerate(values) if value == target}


def build_cells(data: pd.DataFrame, spec: dict, use_unicode_minus: bool) -> list[list[dict]]:
    """Turn every data row into display cells: {'text', 'bold', 'numeric'}."""
    columns = spec["columns"]
    best_rows = {col["source"]: best_row_positions(data, col) for col in columns}
    rows = []
    for position, (_, record) in enumerate(data.iterrows()):
        row_cells = []
        for column in columns:
            value = record[column["source"]]
            numeric = pd.api.types.is_number(value) and not isinstance(value, bool)
            if is_missing(value):
                text = EM_DASH
            elif numeric:
                text = format_number(float(value), column, use_unicode_minus)
                if "stars_from" in column:
                    text += significance_stars(record[column["stars_from"]])
            else:
                text = str(value)
            row_cells.append(
                {
                    "text": text,
                    "bold": position in best_rows[column["source"]],
                    "numeric": numeric,
                }
            )
        rows.append(row_cells)
    return rows


def check_integrity(data: pd.DataFrame, spec: dict, rows: list[list[dict]]) -> None:
    """Confirm the table has the same rows as the CSV and numbers only changed by rounding."""
    if len(rows) != len(data):
        raise SystemExit(f"Row count mismatch: CSV {len(data)}, table {len(rows)}")
    for row_cells, (_, record) in zip(rows, data.iterrows()):
        for cell, column in zip(row_cells, spec["columns"]):
            decimals = column.get("decimals")
            value = record[column["source"]]
            if not cell["numeric"] or decimals is None or is_missing(value):
                continue
            shown = cell["text"].replace(MINUS_SIGN, "-").replace(",", "").rstrip("*")
            if shown.startswith((".", "-.")):
                shown = shown.replace(".", "0.", 1)
            tolerance = 0.5 * 10 ** (-decimals) + 1e-12
            if abs(float(shown) - float(value)) > tolerance:
                raise SystemExit(f"Value changed beyond rounding: {value} -> {cell['text']}")
    print(f"Integrity check passed: {len(rows)} rows x {len(spec['columns'])} columns.")


def row_group_breaks(data: pd.DataFrame, spec: dict) -> dict[int, str]:
    """Map row position -> group heading, for rows where a new group starts."""
    group_column = spec.get("row_group")
    if not group_column:
        return {}
    breaks = {}
    previous = None
    for position, value in enumerate(data[group_column]):
        if value != previous:
            breaks[position] = str(value)
            previous = value
    return breaks


def split_italics(label: str) -> list[tuple[str, bool]]:
    """Split 'Mean *M* (*SD*)' into (text, is_italic) pieces using * as the marker."""
    pieces = label.split("*")
    return [(piece, index % 2 == 1) for index, piece in enumerate(pieces) if piece]


def refuse_overwrite(output_path: Path, overwrite: bool) -> None:
    if output_path.exists() and not overwrite:
        raise SystemExit(f"{output_path} already exists. Re-run with --overwrite to replace it.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
