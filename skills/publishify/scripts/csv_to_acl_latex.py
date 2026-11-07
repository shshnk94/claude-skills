# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas"]
# ///
"""Convert a results CSV into an ACL-style booktabs LaTeX table snippet.

Usage: uv run csv_to_acl_latex.py data.csv spec.json out.tex [--overwrite]
"""

import argparse
from pathlib import Path

from table_format import (
    EM_DASH,
    STAR_THRESHOLDS,
    build_cells,
    check_integrity,
    load_inputs,
    refuse_overwrite,
    row_group_breaks,
    split_italics,
)

LATEX_SPECIAL_CHARACTERS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape_latex(text: str) -> str:
    return "".join(LATEX_SPECIAL_CHARACTERS.get(character, character) for character in text)


def label_to_latex(label: str) -> str:
    """Escape a label and turn *marked* parts into \\textit{}."""
    pieces = []
    for text, italic in split_italics(label):
        escaped = escape_latex(text)
        pieces.append(f"\\textit{{{escaped}}}" if italic else escaped)
    return "".join(pieces)


def header_text(item: dict, key: str = "label") -> str:
    """Use raw LaTeX if the spec gives it (e.g. math symbols), else escape the label."""
    return item.get(f"{key}_latex") or label_to_latex(item[key])


def cell_to_latex(cell: dict) -> str:
    if cell["text"] == EM_DASH:
        return "--"
    text = escape_latex(cell["text"])
    if cell["text"].startswith("-"):
        text = "$-$" + escape_latex(cell["text"][1:])
    stars = len(text) - len(text.rstrip("*"))
    if stars:
        text = text[:-stars] + f"$^{{{'*' * stars}}}$"
    return f"\\textbf{{{text}}}" if cell["bold"] else text


def build_latex(data, spec: dict) -> str:
    columns = spec["columns"]
    body_rows = build_cells(data, spec, use_unicode_minus=False)
    check_integrity(data, spec, body_rows)
    group_breaks = row_group_breaks(data, spec)
    environment = "table*" if spec.get("wide", False) else "table"
    alignment = "l" + "".join(col.get("align", "r")[0] for col in columns[1:])
    column_count = len(columns)

    lines = [
        "% Requires in the preamble: \\usepackage{booktabs}",
        f"\\begin{{{environment}}}[t]",
        "\\centering",
        "\\small",
        f"\\begin{{tabular}}{{{alignment}}}",
        "\\toprule",
    ]

    spanners = spec.get("spanners", [])
    if spanners:
        sources = [col["source"] for col in columns]
        spanner_cells = []
        rules = []
        next_column = 0
        for spanner in spanners:
            first = sources.index(spanner["columns"][0])
            last = sources.index(spanner["columns"][-1])
            spanner_cells.extend([""] * (first - next_column))
            width = last - first + 1
            spanner_cells.append(f"\\multicolumn{{{width}}}{{c}}{{{header_text(spanner)}}}")
            rules.append(f"\\cmidrule(lr){{{first + 1}-{last + 1}}}")
            next_column = last + 1
        spanner_cells.extend([""] * (column_count - next_column))
        lines.append(" & ".join(spanner_cells) + " \\\\")
        lines.append(" ".join(rules))

    lines.append(" & ".join(header_text(col) for col in columns) + " \\\\")
    lines.append("\\midrule")

    for position, row_cells in enumerate(body_rows):
        if position in group_breaks:
            if position > 0:
                lines.append("\\midrule")
            heading = label_to_latex(f"*{group_breaks[position]}*")
            lines.append(f"\\multicolumn{{{column_count}}}{{l}}{{{heading}}} \\\\")
        lines.append(" & ".join(cell_to_latex(cell) for cell in row_cells) + " \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    caption = spec.get("title_latex") or escape_latex(spec["title"])
    if not caption.rstrip().endswith((".", "?", "!")):
        caption += "."
    if spec.get("note"):
        caption += " " + label_to_latex(spec["note"])
    if spec.get("significance_note"):
        legend = [f"$^{{{stars}}}p<{str(threshold).lstrip('0')}$" for threshold, stars in STAR_THRESHOLDS[::-1]]
        caption += " " + ", ".join(legend) + "."
    # ACL template puts table captions below the table
    lines.append(f"\\caption{{{caption}}}")
    lines.append(f"\\label{{{spec.get('label', 'tab:results')}}}")
    lines.append(f"\\end{{{environment}}}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("spec_path", type=Path)
    parser.add_argument("output_path", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    arguments = parser.parse_args()

    refuse_overwrite(arguments.output_path, arguments.overwrite)
    data, spec = load_inputs(arguments.csv_path, arguments.spec_path)
    arguments.output_path.write_text(build_latex(data, spec))
    print(f"Wrote {arguments.output_path}")


if __name__ == "__main__":
    main()
