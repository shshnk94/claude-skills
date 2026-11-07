# /// script
# requires-python = ">=3.10"
# dependencies = ["python-pptx", "matplotlib"]
# ///
"""Draw an approximate PNG preview of each slide, to check crowding and text size.

Usage: uv run preview_deck.py deck.pptx out_dir/

Not a faithful renderer (no themes or fonts); it shows positions, text and images.
"""

import argparse
from io import BytesIO
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu


def inches(value) -> float:
    return Emu(value).inches


def first_font_size(text_frame, default: float = 18) -> float:
    for paragraph in text_frame.paragraphs:
        for run in paragraph.runs:
            if run.font.size:
                return run.font.size.pt
    return default


def is_bold(text_frame) -> bool:
    return any(run.font.bold for paragraph in text_frame.paragraphs for run in paragraph.runs)


def cell_fill(cell) -> str | None:
    fill = cell._tc.tcPr.find(qn("a:solidFill")) if cell._tc.tcPr is not None else None
    if fill is None:
        return None
    return "#" + fill.find(qn("a:srgbClr")).get("val")


def first_font_color(text_frame) -> str:
    for paragraph in text_frame.paragraphs:
        for run in paragraph.runs:
            if run.font.color and run.font.color.type is not None:
                return f"#{run.font.color.rgb}"
    return "black"


def draw_text(axis, shape, slide_height: float) -> None:
    size = first_font_size(shape.text_frame)
    # Slide titles are bold by default even when the run doesn't say so
    bold = is_bold(shape.text_frame) or shape.is_placeholder
    axis.text(
        inches(shape.left),
        slide_height - inches(shape.top),
        shape.text_frame.text,
        fontsize=size,
        va="top",
        wrap=True,
        fontweight="bold" if bold else "normal",
    )


def draw_table(axis, shape, slide_height: float) -> None:
    table = shape.table
    top = inches(shape.top)
    column_lefts = [inches(shape.left)]
    for column in table.columns:
        column_lefts.append(column_lefts[-1] + inches(column.width))
    for row in table.rows:
        row_height = inches(row.height)
        for column_index, cell in enumerate(row.cells):
            size = first_font_size(cell.text_frame)
            fill = cell_fill(cell)
            if fill:
                cell_width = column_lefts[column_index + 1] - column_lefts[column_index]
                axis.add_patch(
                    plt.Rectangle(
                        (column_lefts[column_index], slide_height - top - row_height),
                        cell_width,
                        row_height,
                        color=fill,
                        lw=0,
                    )
                )
            right_aligned = cell.text_frame.paragraphs[0].alignment == PP_ALIGN.RIGHT
            axis.text(
                column_lefts[column_index + 1] - 0.15
                if right_aligned
                else column_lefts[column_index] + 0.15,
                slide_height - top - row_height / 2,
                cell.text_frame.text,
                fontsize=size,
                color=first_font_color(cell.text_frame),
                fontweight="bold" if is_bold(cell.text_frame) else "normal",
                ha="right" if right_aligned else "left",
                va="center",
            )
        top += row_height
    axis.add_patch(
        plt.Rectangle(
            (inches(shape.left), slide_height - top),
            column_lefts[-1] - inches(shape.left),
            top - inches(shape.top),
            fill=False,
            ls=":",
            ec="grey",
        )
    )


def draw_picture(axis, shape, slide_height: float) -> None:
    image = mpimg.imread(BytesIO(shape.image.blob), format=shape.image.ext)
    left, top = inches(shape.left), inches(shape.top)
    axis.imshow(
        image,
        extent=(
            left,
            left + inches(shape.width),
            slide_height - top - inches(shape.height),
            slide_height - top,
        ),
    )


def preview(deck_path: Path, out_dir: Path) -> None:
    deck = Presentation(deck_path)
    width, height = inches(deck.slide_width), inches(deck.slide_height)
    out_dir.mkdir(parents=True, exist_ok=True)
    for number, slide in enumerate(deck.slides, start=1):
        figure = plt.figure(figsize=(width, height), dpi=72)
        axis = figure.add_axes((0, 0, 1, 1))
        axis.set_xlim(0, width)
        axis.set_ylim(0, height)
        axis.axis("off")
        for shape in slide.shapes:
            if getattr(shape, "has_table", False):
                draw_table(axis, shape, height)
            elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                draw_picture(axis, shape, height)
            elif shape.has_text_frame and shape.text_frame.text:
                draw_text(axis, shape, height)
        output = out_dir / f"slide_{number:02d}.png"
        figure.savefig(output)
        plt.close(figure)
        print(f"Wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck_path", type=Path)
    parser.add_argument("out_dir", type=Path)
    arguments = parser.parse_args()
    preview(arguments.deck_path, arguments.out_dir)


if __name__ == "__main__":
    main()
