import argparse
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# Ensure src/ is in the Python path so modules import cleanly from root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from data_loader import load_units_for_puzzles, load_full_units
from puzzle_engine import generate_word_search, generate_crossword
from pdf_exporter import (
    PAGE_WIDTH,
    PAGE_HEIGHT,
    MARGIN,
    draw_tracing_page,
    draw_word_search_page,
    draw_crossword_page,
    draw_answer_key_pages,
    draw_certificate_page,
)
from coding_puzzles import (
    BINARY_PICTURES,
    generate_robot_maze,
    draw_robot_maze_page,
    draw_binary_pixel_page,
    draw_coding_answer_key,
)


def draw_title_page(c, book_title, book_subtitle):
    """Renders a clean KDP Title Page."""
    c.setLineWidth(3)
    c.rect(MARGIN, MARGIN, PAGE_WIDTH - 2 * MARGIN, PAGE_HEIGHT - 2 * MARGIN)

    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 220, book_title)

    c.setFont("Helvetica", 15)
    c.setFillColor(colors.darkgray)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 260, book_subtitle)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - 420, "This Workbook Belongs To:")
    c.setLineWidth(1.2)
    c.line(150, PAGE_HEIGHT - 465, PAGE_WIDTH - 150, PAGE_HEIGHT - 465)

    c.setFont("Helvetica", 11)
    c.drawCentredString(PAGE_WIDTH / 2, MARGIN + 45, "8.5\" x 11\" Activity & Brain Puzzle Edition")
    c.showPage()


def append_vocab_section(c, json_path, unit_solutions):
    """Appends Trace, Word Search, and Crossword pages for a JSON dataset."""
    puzzle_units = load_units_for_puzzles(json_path)
    full_units = load_full_units(json_path)

    for unit_title, words in puzzle_units.items():
        draw_tracing_page(c, unit_title, full_units[unit_title])

        ws_grid, ws_ans, ws_words = generate_word_search(words, size=10)
        cw_grid, cw_placed = generate_crossword(words, size=12)

        draw_word_search_page(c, unit_title, ws_grid, ws_words)
        draw_crossword_page(c, unit_title, cw_grid, cw_placed)
        unit_solutions.append((unit_title, ws_ans, cw_grid))


def build_workbook(mode="full", output_path="output/complete_kdp_workbook.pdf"):
    full_output_path = os.path.join(BASE_DIR, output_path)
    os.makedirs(os.path.dirname(full_output_path), exist_ok=True)

    c = canvas.Canvas(full_output_path, pagesize=letter)
    unit_solutions = []

    if mode == "bilingual":
        draw_title_page(
            c,
            "ENGLISH–FRENCH WORKBOOK",
            "Bilingual Vocabulary, Handwriting & Brain Puzzles (Ages 5–8)"
        )
        append_vocab_section(c, "data/units_en_fr.json", unit_solutions)
        draw_answer_key_pages(c, unit_solutions)
        draw_certificate_page(c, "English–French Visual Vocabulary Workbook")

    elif mode == "coding":
        draw_title_page(
            c,
            "SCREEN-FREE CODING & LOGIC",
            "Unplugged Algorithms, Robot Mazes & Binary Pixel Art (Ages 6–9)"
        )
        append_vocab_section(c, "data/units_coding_kids.json", unit_solutions)

        maze_solutions = []
        for level in range(1, 9):
            grid, _, arrows = generate_robot_maze(grid_size=6, num_obstacles=min(4 + level, 10))
            draw_robot_maze_page(c, level, grid, arrows)
            maze_solutions.append(arrows)

        for title, matrix in BINARY_PICTURES.items():
            draw_binary_pixel_page(c, title, matrix)

        draw_answer_key_pages(c, unit_solutions)
        draw_coding_answer_key(c, maze_solutions, BINARY_PICTURES)
        draw_certificate_page(c, "Screen-Free Logic & Coding Workbook")

    elif mode == "full":
        draw_title_page(
            c,
            "MEGA KIDS ACTIVITY WORKBOOK",
            "Bilingual French–English, Unplugged Coding & Brain Puzzles"
        )
        # 1. English-French Section (30 activity pages)
        append_vocab_section(c, "data/units_en_fr.json", unit_solutions)

        # 2. Coding Vocabulary Section (15 activity pages)
        append_vocab_section(c, "data/units_coding_kids.json", unit_solutions)

        # 3. Robot Grid Mazes (8 pages) & Binary Pixel Art (4 pages)
        maze_solutions = []
        for level in range(1, 9):
            grid, _, arrows = generate_robot_maze(grid_size=6, num_obstacles=min(4 + level, 10))
            draw_robot_maze_page(c, level, grid, arrows)
            maze_solutions.append(arrows)

        for title, matrix in BINARY_PICTURES.items():
            draw_binary_pixel_page(c, title, matrix)

        # 4. Complete Answer Keys & Cut-Out Certificate
        draw_answer_key_pages(c, unit_solutions)
        draw_coding_answer_key(c, maze_solutions, BINARY_PICTURES)
        draw_certificate_page(c, "Mega Kids Bilingual & Coding Workbook")

    c.save()
    print(f"[SUCCESS] Generated '{mode}' KDP workbook at: {full_output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KDP Workbook Puzzle Engine CLI")
    parser.add_argument(
        "--mode",
        choices=["full", "bilingual", "coding"],
        default="full",
        help="Choose workbook type: 'full' (60+ pages), 'bilingual', or 'coding'"
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Custom output PDF path (e.g., output/my_book.pdf)"
    )
    args = parser.parse_args()

    default_outputs = {
        "full": "output/mega_65page_kdp_workbook.pdf",
        "bilingual": "output/bilingual_en_fr_kdp.pdf",
        "coding": "output/screen_free_coding_kdp.pdf",
    }
    target_out = args.out if args.out else default_outputs[args.mode]
    build_workbook(mode=args.mode, output_path=target_out)
