# /// script
# requires-python = ">=3.10"
# dependencies = ["pandas", "python-pptx", "pillow"]
# ///
"""Create or update one 16:9 slide deck from a manifest of table and image slides.

Usage: uv run build_deck.py manifest.json artifacts/slides/<deck>.pptx

Each slide is tagged with its source path (in the slide's internal name), so
re-running replaces that slide in place and leaves hand-made slides alone.
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

# Number formatting and the integrity check are shared with publishify
sys.path.insert(0, str(Path.home() / ".claude/skills/publishify/scripts"))
from table_format import build_cells, check_integrity, split_italics

SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)
CONTENT_LEFT = Inches(0.5)
CONTENT_TOP = Inches(1.5)
CONTENT_WIDTH = Inches(12.333)
CONTENT_HEIGHT = Inches(5.4)
FOOTER_TOP = Inches(6.95)

ACCENT = RGBColor(0x00, 0x72, 0xB2)
ACCENT_FILL = RGBColor(0xE6, 0xF0, 0xF7)
TEXT_DARK = RGBColor(0x26, 0x26, 0x26)
TEXT_MUTED = RGBColor(0x6E, 0x6E, 0x6E)
RULE_COLOR = "A6A6A6"
NO_STYLE_NO_GRID = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"
TAG_PREFIX = "presentify:"


# ---------- deck handling ----------


def open_deck(deck_path: Path, template_path: str | None) -> Presentation:
    """Open the existing deck, or start one from the template or a blank 16:9 deck."""
    if deck_path.exists():
        return Presentation(deck_path)
    if template_path:
        deck = Presentation(template_path)
        # Templates often ship with example slides; start from none
        for slide_id in list(deck.slides._sldIdLst):
            deck.part.drop_rel(slide_id.rId)
            deck.slides._sldIdLst.remove(slide_id)
        return deck
    deck = Presentation()
    deck.slide_width = SLIDE_WIDTH
    deck.slide_height = SLIDE_HEIGHT
    return deck


def title_only_layout(deck: Presentation):
    for layout in deck.slide_layouts:
        if layout.name.lower() == "title only":
            return layout
    return deck.slide_layouts[5] if len(deck.slide_layouts) > 5 else deck.slide_layouts[-1]


def slide_tag(slide) -> str:
    return slide._element.cSld.get("name", "")


def find_tagged_slide_index(deck: Presentation, tag: str) -> int | None:
    for index, slide in enumerate(deck.slides):
        if slide_tag(slide) == tag:
            return index
    return None


def move_slide(deck: Presentation, old_index: int, new_index: int) -> None:
    slide_ids = deck.slides._sldIdLst
    slide_id = list(slide_ids)[old_index]
    slide_ids.remove(slide_id)
    slide_ids.insert(new_index, slide_id)


def delete_slide(deck: Presentation, index: int) -> None:
    slide_id = list(deck.slides._sldIdLst)[index]
    deck.part.drop_rel(slide_id.rId)
    deck.slides._sldIdLst.remove(slide_id)
    # New slides are named slideN.xml from the slide count, so renumber to avoid clashes
    deck.part.rename_slide_parts([remaining.rId for remaining in deck.slides._sldIdLst])


def new_slide(deck: Presentation, slide_spec: dict, styled: bool):
    """Add a slide with the takeaway title, footer, notes and source tag."""
    slide = deck.slides.add_slide(title_only_layout(deck))
    slide._element.cSld.set("name", TAG_PREFIX + slide_spec["source"])

    title = slide.shapes.title
    title.text = slide_spec["title"]
    if styled:
        title.left, title.top = CONTENT_LEFT, Inches(0.4)
        title.width, title.height = CONTENT_WIDTH, Inches(1.0)
        for paragraph in title.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(slide_spec.get("title_size", 30))
                run.font.bold = True
                run.font.color.rgb = TEXT_DARK

    if slide_spec.get("footer"):
        footer = slide.shapes.add_textbox(CONTENT_LEFT, FOOTER_TOP, CONTENT_WIDTH, Inches(0.4))
        run = footer.text_frame.paragraphs[0].add_run()
        run.text = slide_spec["footer"]
        run.font.size = Pt(14)
        run.font.color.rgb = TEXT_MUTED

    if slide_spec.get("notes"):
        slide.notes_slide.notes_text_frame.text = slide_spec["notes"]
    return slide


# ---------- table slides ----------


def set_cell_lines(cell, top: bool, bottom: bool, fill: RGBColor | None) -> None:
    """Give a cell optional top/bottom rules and a background; no vertical lines."""
    cell_properties = cell._tc.get_or_add_tcPr()
    for child in list(cell_properties):
        cell_properties.remove(child)
    # Order matters in the XML: left, right, top, bottom lines, then fill
    for edge, visible in (("lnL", False), ("lnR", False), ("lnT", top), ("lnB", bottom)):
        line = cell_properties.makeelement(qn(f"a:{edge}"), {"w": "12700" if visible else "0"})
        if visible:
            solid = line.makeelement(qn("a:solidFill"), {})
            color = solid.makeelement(qn("a:srgbClr"), {"val": RULE_COLOR})
            solid.append(color)
            line.append(solid)
        else:
            line.append(line.makeelement(qn("a:noFill"), {}))
        cell_properties.append(line)
    if fill is not None:
        solid = cell_properties.makeelement(qn("a:solidFill"), {})
        solid.append(solid.makeelement(qn("a:srgbClr"), {"val": str(fill)}))
        cell_properties.append(solid)
    else:
        cell_properties.append(cell_properties.makeelement(qn("a:noFill"), {}))


def write_cell(cell, text: str, size: int, bold: bool, color: RGBColor, align_right: bool):
    paragraph = cell.text_frame.paragraphs[0]
    paragraph.alignment = PP_ALIGN.RIGHT if align_right else PP_ALIGN.LEFT
    for piece, italic in split_italics(text) if text else [("", False)]:
        run = paragraph.add_run()
        run.text = piece
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.italic = italic
        run.font.color.rgb = color
    cell.margin_left = cell.margin_right = Inches(0.12)


def select_rows(data: pd.DataFrame, spec: dict) -> pd.DataFrame:
    """Keep only the rows the story needs, in the order given."""
    keep = spec.get("keep_rows")
    if not keep:
        return data.reset_index(drop=True)
    key_column = spec["columns"][0]["source"]
    kept = []
    for value in keep:
        match = data[data[key_column].astype(str) == str(value)]
        if match.empty:
            raise SystemExit(f"keep_rows value not found in '{key_column}': {value}")
        kept.append(match)
    return pd.concat(kept).reset_index(drop=True)


def add_table(slide, slide_spec: dict) -> None:
    spec = slide_spec["spec"]
    data = select_rows(pd.read_csv(slide_spec["csv"]), spec)
    body_rows = build_cells(data, spec, use_unicode_minus=True)
    check_integrity(data, spec, body_rows)

    columns = spec["columns"]
    # Short tables leave lots of empty space, so they get bigger text by default
    size = spec.get("font_size", 24 if len(body_rows) <= 5 else 20)
    key_column = columns[0]["source"]
    highlighted = {str(value) for value in spec.get("highlight_rows", [])}
    # Display names for row labels (e.g. Fine-tuned_BERT -> Fine-tuned BERT); matching uses raw values
    row_labels = spec.get("row_labels", {})
    for row_cells, key_value in zip(body_rows, data[key_column]):
        row_cells[0]["text"] = row_labels.get(str(key_value), row_cells[0]["text"])
    row_height = Inches(0.3 + size / 72 * 0.9)
    table_height = row_height * (len(body_rows) + 1)
    # Rough text width: an average character is about 0.55 em wide
    longest_label = max(len(row_cells[0]["text"]) for row_cells in body_rows)
    first_width = Inches(max(2.6, longest_label * size * 0.55 / 72 + 0.5))
    table_width = min(CONTENT_WIDTH, first_width + Inches(1.9) * (len(columns) - 1))
    left = CONTENT_LEFT + (CONTENT_WIDTH - table_width) // 2
    top = CONTENT_TOP + max(0, (CONTENT_HEIGHT - table_height) // 2)

    shape = slide.shapes.add_table(
        len(body_rows) + 1, len(columns), left, top, table_width, table_height
    )
    table = shape.table
    table._tbl.tblPr.find(qn("a:tableStyleId")).text = NO_STYLE_NO_GRID
    table.first_row = False
    table.horz_banding = False
    table.columns[0].width = first_width
    for column_index in range(1, len(columns)):
        table.columns[column_index].width = (table_width - first_width) // (len(columns) - 1)

    for column_index, column in enumerate(columns):
        cell = table.cell(0, column_index)
        write_cell(cell, column["label"], size, True, TEXT_MUTED, column_index > 0)
        set_cell_lines(cell, top=False, bottom=True, fill=None)

    last_row = len(body_rows)
    for row_index, (row_cells, key_value) in enumerate(zip(body_rows, data[key_column]), start=1):
        is_highlighted = str(key_value) in highlighted
        for column_index, cell_info in enumerate(row_cells):
            cell = table.cell(row_index, column_index)
            color = ACCENT if is_highlighted else TEXT_DARK
            bold = is_highlighted or cell_info["bold"]
            write_cell(cell, cell_info["text"], size, bold, color, column_index > 0)
            fill = ACCENT_FILL if is_highlighted else None
            set_cell_lines(cell, top=False, bottom=row_index == last_row, fill=fill)


# ---------- image slides ----------


def add_image(slide, slide_spec: dict) -> None:
    """Place the image as large as fits in the content area, centred, without stretching."""
    image_path = slide_spec["image"]
    with Image.open(image_path) as image:
        pixel_width, pixel_height = image.size
    scale = min(CONTENT_WIDTH / pixel_width, CONTENT_HEIGHT / pixel_height)
    width, height = int(pixel_width * scale), int(pixel_height * scale)
    left = CONTENT_LEFT + (CONTENT_WIDTH - width) // 2
    top = CONTENT_TOP + (CONTENT_HEIGHT - height) // 2
    slide.shapes.add_picture(image_path, left, top, width, height)


# ---------- main ----------


def build_deck(manifest: dict, deck_path: Path) -> Presentation:
    deck = open_deck(deck_path, manifest.get("template"))
    styled = not manifest.get("template")
    for slide_spec in manifest["slides"]:
        tag = TAG_PREFIX + slide_spec["source"]
        old_index = find_tagged_slide_index(deck, tag)
        slide = new_slide(deck, slide_spec, styled)
        if slide_spec["type"] == "table":
            add_table(slide, slide_spec)
        elif slide_spec["type"] == "image":
            add_image(slide, slide_spec)
        else:
            raise SystemExit(f"Unknown slide type: {slide_spec['type']}")
        if old_index is not None:
            move_slide(deck, len(deck.slides) - 1, old_index)
            delete_slide(deck, old_index + 1)
            print(f"Replaced slide {old_index + 1}: {slide_spec['title']}")
        else:
            print(f"Added slide {len(deck.slides)}: {slide_spec['title']}")
    return deck


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest_path", type=Path)
    parser.add_argument("deck_path", type=Path)
    arguments = parser.parse_args()

    manifest = json.loads(arguments.manifest_path.read_text())
    for slide_spec in manifest["slides"]:
        if "spec_path" in slide_spec:
            slide_spec["spec"] = json.loads(Path(slide_spec["spec_path"]).read_text())
    arguments.deck_path.parent.mkdir(parents=True, exist_ok=True)
    deck = build_deck(manifest, arguments.deck_path)
    deck.save(arguments.deck_path)
    print(f"Saved {arguments.deck_path} ({len(deck.slides)} slides)")


if __name__ == "__main__":
    main()
