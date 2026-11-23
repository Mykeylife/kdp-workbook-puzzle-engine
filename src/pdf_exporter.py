import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

from data_loader import load_units_for_puzzles, load_full_units
from puzzle_engine import generate_word_search, generate_crossword

# KDP 8.5 x 11 inches (612 x 792 points) with 0.65-inch safe margins
PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 46.8  # 0.65 inches in points


def draw_page_header(c, title, subtitle):
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - MARGIN - 10, title)
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.darkgray)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - MARGIN - 28, subtitle)
    c.setFillColor(colors.black)


def draw_tracing_page(c, unit_title, unit_items):
    draw_page_header(
        c,
        f"{unit_title} — Trace & Write",
        "Say the word out loud, trace the word, then write it on your own!"
    )

    y_top = PAGE_HEIGHT - MARGIN - 65
    row_height = 78  # Fits all 8 words cleanly on an 8.5x11 page

    for idx, item in enumerate(unit_items):
        en_word = item["en"]
        target_word = item["fr"]
        phonetic = item.get("phonetic", "")

        row_y = y_top - (idx * row_height)

        # Left label: Clue/English word + phonetic pronunciation
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 11)
        # Truncate long definitions slightly if using coding dataset
        display_en = en_word if len(en_word) <= 24 else en_word[:22] + "..."
        c.drawString(MARGIN + 5, row_y - 16, f"{idx + 1}. {display_en}")

        if phonetic:
            c.setFillColor(colors.darkgray)
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(MARGIN + 18, row_y - 32, f"({phonetic})")

        # Right side: Primary handwriting ruled lines
        line_start_x = MARGIN + 165
        line_end_x = PAGE_WIDTH - MARGIN - 5
        top_line_y = row_y - 8
        mid_line_y = row_y - 23
        base_line_y = row_y - 38

        c.setStrokeColor(colors.gray)
        c.setLineWidth(0.8)
        c.setDash([])  # Solid top & bottom lines
        c.line(line_start_x, top_line_y, line_end_x, top_line_y)
        c.line(line_start_x, base_line_y, line_end_x, base_line_y)

        c.setDash(3, 3)  # Dashed midline for lowercase height
        c.line(line_start_x, mid_line_y, line_end_x, mid_line_y)
        c.setDash([])

        # Traceable light-gray target word on the left side of the ruled line
        c.setFillColor(colors.lightgrey)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(line_start_x + 12, base_line_y + 4, target_word)

    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)
    c.showPage()


def draw_word_search_page(c, unit_title, ws_grid, ws_words):
    draw_page_header(
        c,
        f"{unit_title} — Word Search",
        "Find and circle the hidden words below (across or down)!"
    )

    grid_size = len(ws_grid)
    cell_size = 34
    grid_total_w = grid_size * cell_size
    start_x = (PAGE_WIDTH - grid_total_w) / 2
    start_y = PAGE_HEIGHT - MARGIN - 65

    # Draw outer border and grid letters
    c.setLineWidth(1.5)
    c.rect(start_x, start_y - grid_total_w, grid_total_w, grid_total_w)
    c.setFont("Helvetica-Bold", 15)

    for r in range(grid_size):
        for col in range(grid_size):
            x = start_x + col * cell_size + (cell_size / 2)
            y = start_y - r * cell_size - (cell_size * 0.68)
            c.drawCentredString(x, y, ws_grid[r][col])

    # Draw 2-column Word Bank below grid
    bank_y = start_y - grid_total_w - 35
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN + 20, bank_y, "Word Bank:")

    c.setFont("Helvetica", 11)
    col1_x = MARGIN + 20
    col2_x = PAGE_WIDTH / 2 + 10
    for idx, (eng, fr, _) in enumerate(ws_words):
        x = col1_x if idx < 4 else col2_x
        y = bank_y - 25 - ((idx % 4) * 22)
        c.drawString(x, y, f"[ ]  {fr}  ({eng})")

    c.showPage()


def draw_crossword_page(c, unit_title, cw_grid, cw_placed):
    draw_page_header(
        c,
        f"{unit_title} — Crossword",
        "Use the clues below to fill in the boxes!"
    )

    grid_size = len(cw_grid)
    cell_size = 28
    grid_total_w = grid_size * cell_size
    start_x = (PAGE_WIDTH - grid_total_w) / 2
    start_y = PAGE_HEIGHT - MARGIN - 60

    # Map starting coordinates to clue numbers
    start_nums = {}
    for p in cw_placed:
        key = (p["r"], p["c"])
        start_nums.setdefault(key, []).append(str(p["num"]))

    c.setLineWidth(1.2)
    for r in range(grid_size):
        for col in range(grid_size):
            if cw_grid[r][col] != ' ':
                x = start_x + col * cell_size
                y = start_y - (r + 1) * cell_size
                c.rect(x, y, cell_size, cell_size)

                if (r, col) in start_nums:
                    c.setFont("Helvetica-Bold", 7)
                    c.drawString(x + 2, y + cell_size - 8, "/".join(start_nums[(r, col)]))

    # Draw Clues (Across & Down)
    clues_y = start_y - grid_total_w - 25
    across = [p for p in cw_placed if p["dir"] == "ACROSS"]
    down = [p for p in cw_placed if p["dir"] == "DOWN"]

    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + 10, clues_y, "ACROSS")
    c.drawString(PAGE_WIDTH / 2 + 10, clues_y, "DOWN")

    c.setFont("Helvetica", 10)
    for idx, p in enumerate(across):
        c.drawString(MARGIN + 10, clues_y - 20 - (idx * 18), f"{p['num']}. {p['eng']} ({len(p['clean'])})")

    for idx, p in enumerate(down):
        c.drawString(PAGE_WIDTH / 2 + 10, clues_y - 20 - (idx * 18), f"{p['num']}. {p['eng']} ({len(p['clean'])})")

    c.showPage()


def draw_answer_key_pages(c, unit_solutions):
    draw_page_header(c, "Answer Key", "Solutions for Word Searches and Crosswords")
    y_cursor = PAGE_HEIGHT - MARGIN - 55

    for unit_title, ws_ans, cw_grid in unit_solutions:
        if y_cursor < 180:
            c.showPage()
            draw_page_header(c, "Answer Key (Continued)", "")
            y_cursor = PAGE_HEIGHT - MARGIN - 55

        c.setFont("Helvetica-Bold", 11)
        c.drawString(MARGIN, y_cursor, unit_title)
        y_cursor -= 14

        c.setFont("Courier", 8)
        ws_lines = [" ".join(row) for row in ws_ans]
        cw_lines = [" ".join(ch if ch != ' ' else '.' for ch in row) for row in cw_grid]

        for line_idx in range(max(len(ws_lines), len(cw_lines))):
            ws_str = ws_lines[line_idx] if line_idx < len(ws_lines) else ""
            cw_str = cw_lines[line_idx] if line_idx < len(cw_lines) else ""
            c.drawString(MARGIN + 10, y_cursor, ws_str)
            c.drawString(PAGE_WIDTH / 2, y_cursor, cw_str)
            y_cursor -= 9.5

        y_cursor -= 15

    c.showPage()

def draw_certificate_page(c, book_subtitle="Bilingual Vocabulary & Brain Puzzles"):
    # Dashed outer cut-out border
    c.setStrokeColor(colors.black)
    c.setLineWidth(1.5)
    c.setDash(6, 4)
    c.rect(MARGIN, MARGIN, PAGE_WIDTH - 2 * MARGIN, PAGE_HEIGHT - 2 * MARGIN)

    # Solid decorative inner border
    c.setDash([])
    c.setLineWidth(2.5)
    inner_offset = 14
    c.rect(
        MARGIN + inner_offset,
        MARGIN + inner_offset,
        PAGE_WIDTH - 2 * (MARGIN + inner_offset),
        PAGE_HEIGHT - 2 * (MARGIN + inner_offset)
    )

    # Scissors / Cut instruction at top
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.darkgray)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - MARGIN + 6, "✂  Cut along the dashed line to display your certificate!  ✂")

    # Main Certificate Title
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 165, "CERTIFICATE OF ACHIEVEMENT")

    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 205, "This certifies that")

    # Student Name Line
    c.setLineWidth(1.2)
    c.line(140, PAGE_HEIGHT - 275, PAGE_WIDTH - 140, PAGE_HEIGHT - 275)
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.darkgray)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 290, "(Write your name here)")

    # Achievement Text
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 14)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 340, "has successfully completed all units and brain puzzles in")

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 370, book_subtitle)

    # Decorative Star / Seal Emblem
    center_x = PAGE_WIDTH / 2
    seal_y = PAGE_HEIGHT - 465
    c.setLineWidth(2)
    c.circle(center_x, seal_y, 38, stroke=1, fill=0)
    c.setLineWidth(1)
    c.circle(center_x, seal_y, 32, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(center_x, seal_y + 4, "SUPER")
    c.drawCentredString(center_x, seal_y - 10, "LEARNER")

    # Date and Signature Lines
    sig_y = MARGIN + 75
    c.setLineWidth(1)
    c.line(95, sig_y, 255, sig_y)
    c.line(PAGE_WIDTH - 255, sig_y, PAGE_WIDTH - 95, sig_y)

    c.setFont("Helvetica", 11)
    c.drawCentredString(175, sig_y - 16, "Date")
    c.drawCentredString(PAGE_WIDTH - 175, sig_y - 16, "Parent / Teacher Signature")

    c.showPage()


def build_kdp_pdf(json_path="data/units_en_fr.json", output_path="output/bilingual_workbook_kdp.pdf"):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_output_path = os.path.join(base_dir, output_path)
    os.makedirs(os.path.dirname(full_output_path), exist_ok=True)

    c = canvas.Canvas(full_output_path, pagesize=letter)
    unit_solutions = []

    puzzle_units = load_units_for_puzzles(json_path)
    full_units = load_full_units(json_path)

    for unit_title, words in puzzle_units.items():
        # Page 1 of unit: Trace & Write
        draw_tracing_page(c, unit_title, full_units[unit_title])

        # Page 2 & 3 of unit: Word Search & Crossword
        ws_grid, ws_ans, ws_words = generate_word_search(words, size=10)
        cw_grid, cw_placed = generate_crossword(words, size=12)

        draw_word_search_page(c, unit_title, ws_grid, ws_words)
        draw_crossword_page(c, unit_title, cw_grid, cw_placed)
        unit_solutions.append((unit_title, ws_ans, cw_grid))

    draw_answer_key_pages(c, unit_solutions)
    c.save()
    print(f"Successfully generated KDP-ready PDF at: {full_output_path}")


if __name__ == "__main__":
    # Optional CLI usage:
    # python src/pdf_exporter.py data/units_coding_kids.json output/coding_workbook_kdp.pdf
    dataset = sys.argv[1] if len(sys.argv) > 1 else "data/units_en_fr.json"
    out_file = sys.argv[2] if len(sys.argv) > 2 else "output/bilingual_workbook_kdp.pdf"
    build_kdp_pdf(dataset, out_file)
