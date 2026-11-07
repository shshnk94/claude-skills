# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "python-docx"]
# ///
"""Convert a results CSV into an APA 7th edition table in a .docx file.

Usage: uv run csv_to_apa_docx.py data.csv spec.json out.docx [--overwrite]
"""

import argparse
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from table_format import (
    build_cells,
    check_integrity,
    load_inputs,
    refuse_overwrite,
    row_group_breaks,
    significance_note_pieces,
    split_italics,
)


def set_cell_border(cell, edge: str, size: int = 8) -> None:
    """Draw a single horizontal line on one edge ('top' or 'bottom') of a cell."""
    cell_properties = cell._tc.get_or_add_tcPr()
    borders = cell_properties.find(qn("w:tcBorders"))
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        cell_properties.append(borders)
    line = OxmlElement(f"w:{edge}")
    line.set(qn("w:val"), "single")
    line.set(qn("w:sz"), str(size))
    line.set(qn("w:color"), "000000")
    borders.append(line)


def remove_table_borders(table) -> None:
    """Start from a table with no lines at all; APA lines are added per cell."""
    table_properties = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        line = OxmlElement(f"w:{edge}")
        line.set(qn("w:val"), "nil")
        borders.append(line)
    table_properties.append(borders)


def write_runs(paragraph, label: str, font: str, size: float, bold: bool = False) -> None:
    """Add text to a paragraph, italicising *marked* parts."""
    for text, italic in split_italics(label):
        run = paragraph.add_run(text)
        run.italic = italic
        run.bold = bold
        run.font.name = font
        run.font.size = Pt(size)


def fill_cell(cell, label: str, align, font: str, size: float, bold: bool = False) -> None:
    paragraph = cell.paragraphs[0]
    paragraph.alignment = align
    paragraph.paragraph_format.space_after = Pt(0)
    write_runs(paragraph, label, font, size, bold)


def add_caption_paragraph(document, label: str, font: str, size: float, bold: bool) -> None:
    paragraph = document.add_paragraph()
    paragraph.paragraph_format.line_spacing = 2.0
    paragraph.paragraph_format.space_after = Pt(0)
    write_runs(paragraph, label, font, size, bold)


def build_document(data, spec: dict):
    font = spec.get("font", "Times New Roman")
    size = spec.get("font_size", 12)
    columns = spec["columns"]
    spanners = spec.get("spanners", [])
    group_breaks = row_group_breaks(data, spec)
    body_rows = build_cells(data, spec, use_unicode_minus=True)
    check_integrity(data, spec, body_rows)

    document = Document()
    section = document.sections[0]
    if spec.get("landscape", False):
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width, section.page_height = Inches(11), Inches(8.5)
    for margin in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(section, margin, Inches(1))

    add_caption_paragraph(document, f"Table {spec.get('table_number', 1)}", font, size, bold=True)
    # APA titles are italic; wrapping in * reuses the italic marker
    add_caption_paragraph(document, f"*{spec['title']}*", font, size, bold=False)

    header_row_count = 2 if spanners else 1
    total_rows = header_row_count + len(body_rows) + len(group_breaks)
    table = document.add_table(rows=total_rows, cols=len(columns))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    remove_table_borders(table)

    def alignment_for(column_index: int):
        if column_index == 0:
            return WD_ALIGN_PARAGRAPH.LEFT
        return WD_ALIGN_PARAGRAPH.CENTER

    # Spanner row: one merged cell per spanner, with a line under it
    if spanners:
        sources = [col["source"] for col in columns]
        for column_index in range(len(columns)):
            set_cell_border(table.cell(0, column_index), "top")
        for spanner in spanners:
            first = sources.index(spanner["columns"][0])
            last = sources.index(spanner["columns"][-1])
            merged = table.cell(0, first).merge(table.cell(0, last))
            fill_cell(merged, spanner["label"], WD_ALIGN_PARAGRAPH.CENTER, font, size)
            set_cell_border(merged, "bottom")

    header_index = header_row_count - 1
    for column_index, column in enumerate(columns):
        cell = table.cell(header_index, column_index)
        fill_cell(cell, column["label"], alignment_for(column_index), font, size)
        if not spanners:
            set_cell_border(cell, "top")
        set_cell_border(cell, "bottom")

    current_row = header_row_count
    for position, row_cells in enumerate(body_rows):
        if position in group_breaks:
            merged = table.cell(current_row, 0).merge(table.cell(current_row, len(columns) - 1))
            fill_cell(merged, f"*{group_breaks[position]}*", WD_ALIGN_PARAGRAPH.LEFT, font, size)
            current_row += 1
        for column_index, cell_info in enumerate(row_cells):
            cell = table.cell(current_row, column_index)
            paragraph = cell.paragraphs[0]
            paragraph.alignment = alignment_for(column_index)
            paragraph.paragraph_format.space_after = Pt(0)
            # Cell values are plain text; * here are significance stars, not italics
            run = paragraph.add_run(cell_info["text"])
            run.bold = cell_info["bold"]
            run.font.name = font
            run.font.size = Pt(size)
        current_row += 1

    for column_index in range(len(columns)):
        set_cell_border(table.cell(total_rows - 1, column_index), "bottom")

    if spec.get("note") or spec.get("significance_note"):
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.line_spacing = 2.0
        paragraph.paragraph_format.space_before = Pt(6)
        write_runs(paragraph, "*Note.* ", font, size)
        if spec.get("note"):
            write_runs(paragraph, spec["note"] + " ", font, size)
        if spec.get("significance_note"):
            for text, italic in significance_note_pieces():
                run = paragraph.add_run(text)
                run.italic = italic
                run.font.name = font
                run.font.size = Pt(size)
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("spec_path", type=Path)
    parser.add_argument("output_path", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    arguments = parser.parse_args()

    refuse_overwrite(arguments.output_path, arguments.overwrite)
    data, spec = load_inputs(arguments.csv_path, arguments.spec_path)
    document = build_document(data, spec)
    document.save(arguments.output_path)
    print(f"Wrote {arguments.output_path}")


if __name__ == "__main__":
    main()
