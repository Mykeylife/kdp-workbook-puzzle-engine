import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from puzzle_engine import WORKBOOK_UNITS, generate_word_search, generate_crossword

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

def draw_word_search_page(c, unit_title, ws_grid, ws_words):
    draw_page_header(
        c,
        f"{unit_title} — Word Search",
        "Find and circle the hidden French words below (across or down)!"
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
    c.drawString(MARGIN + 20, bank_y, "Word Bank (English → French):")

    c.setFont("Helvetica", 12)
    col1_x = MARGIN + 25
    col2_x = PAGE_WIDTH / 2 + 10
    for idx, (eng, fr, _) in enumerate(ws_words):
        x = col1_x if idx < 4 else col2_x
        y = bank_y - 25 - ((idx % 4) * 22)
        c.drawString(x, y, f"☐  {eng}  —  {fr}")

    c.showPage()

def draw_crossword_page(c, unit_title, cw_grid, cw_placed):
    draw_page_header(
        c,
        f"{unit_title} — Crossword",
        "Translate the English clues into French to fill in the boxes!"
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

    c.setFont("Helvetica", 11)
    for idx, p in enumerate(across):
        c.drawString(MARGIN + 10, clues_y - 20 - (idx * 18), f"{p['num']}. {p['eng']} ({len(p['clean'])} letters)")

    for idx, p in enumerate(down):
        c.drawString(PAGE_WIDTH / 2 + 10, clues_y - 20 - (idx * 18), f"{p['num']}. {p['eng']} ({len(p['clean'])} letters)")

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

def build_kdp_pdf(output_path="output/bilingual_puzzles_kdp.pdf"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    c = canvas.Canvas(output_path, pagesize=letter)
    unit_solutions = []

    for unit_title, words in WORKBOOK_UNITS.items():
        ws_grid, ws_ans, ws_words = generate_word_search(words, size=10)
        cw_grid, cw_placed = generate_crossword(words, size=12)

        draw_word_search_page(c, unit_title, ws_grid, ws_words)
        draw_crossword_page(c, unit_title, cw_grid, cw_placed)
        unit_solutions.append((unit_title, ws_ans, cw_grid))

    draw_answer_key_pages(c, unit_solutions)
    c.save()
    print(f"Successfully generated KDP-ready PDF at: {output_path}")

if __name__ == "__main__":
    build_kdp_pdf()
