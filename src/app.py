import os
import sys
import tempfile
import streamlit as st
from reportlab.lib.pagesizes import letter

# Ensure src/ is importable
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from main import (
    NumberedCanvas,
    draw_title_page,
    append_vocab_section,
)
from data_loader import load_full_units
from puzzle_engine import generate_word_search
from pdf_exporter import draw_answer_key_pages, draw_certificate_page
from coding_puzzles import (
    BINARY_PICTURES,
    generate_robot_maze,
    draw_robot_maze_page,
    draw_binary_pixel_page,
    draw_coding_answer_key,
)

# ==========================================
# PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(
    page_title="KDP Workbook Puzzle Engine",
    page_icon="📚",
    layout="wide",
)

st.title("📚 KDP Workbook Puzzle Engine")
st.caption("Generate print-ready 8.5\" x 11\" educational workbooks with tracing, puzzles, mazes, and answer keys.")

# ==========================================
# SIDEBAR: WORKBOOK CONFIGURATION
# ==========================================
with st.sidebar:
    st.header("⚙️ Workbook Settings")

    mode = st.selectbox(
        "Workbook Edition",
        options=["full", "bilingual", "coding"],
        format_func=lambda x: {
            "full": "Mega Workbook (Bilingual + Coding, 65+ Pages)",
            "bilingual": "English–French Bilingual Workbook",
            "coding": "Screen-Free Logic & Coding Workbook",
        }[x],
    )

    default_titles = {
        "full": ("MEGA KIDS ACTIVITY WORKBOOK", "Bilingual French–English, Unplugged Coding & Brain Puzzles"),
        "bilingual": ("ENGLISH–FRENCH WORKBOOK", "Bilingual Vocabulary, Handwriting & Brain Puzzles (Ages 5–8)"),
        "coding": ("SCREEN-FREE CODING & LOGIC", "Unplugged Algorithms, Robot Mazes & Binary Pixel Art (Ages 6–9)"),
    }

    book_title = st.text_input("Title Page Heading", value=default_titles[mode])
    book_subtitle = st.text_input("Title Page Subtitle", value=default_titles[mode])
    cert_title = st.text_input("Certificate Book Name", value=book_title.title())

    maze_count = st.slider("Number of Robot Grid Mazes", min_value=2, max_value=12, value=8, disabled=(mode == "bilingual"))

# ==========================================
# MAIN TABS: PREVIEW & BUILD
# ==========================================
tab_build, tab_preview, tab_data = st.tabs(["🚀 Build & Download PDF", "🔍 Live Puzzle Preview", "📖 Vocabulary Units"])

with tab_build:
    st.subheader("Generate Print-Ready KDP Interior")
    st.write(
        "Your PDF is formatted to **8.5\" x 11\" (No Bleed)** with **0.65\" safe margins**, "
        "automatic page numbering, complete answer keys, and a cut-out certificate."
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Trim Size", "8.5\" x 11\"")
    col2.metric("Interior Style", "Black & White")
    col3.metric("Estimated Pages", "65+ Pages" if mode == "full" else "32+ Pages")

    if st.button("✨ Generate KDP Workbook PDF", type="primary", use_container_width=True):
        with st.spinner("Generating grids, handwriting lines, mazes, and answer keys..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                pdf_path = tmp_file.name

            c = NumberedCanvas(pdf_path, pagesize=letter)
            unit_solutions = []

            draw_title_page(c, book_title, book_subtitle)

            if mode in ("full", "bilingual"):
                append_vocab_section(c, "data/units_en_fr.json", unit_solutions)

            if mode in ("full", "coding"):
                append_vocab_section(c, "data/units_coding_kids.json", unit_solutions)

                maze_solutions = []
                for level in range(1, maze_count + 1):
                    grid, _, arrows = generate_robot_maze(grid_size=6, num_obstacles=min(4 + level, 10))
                    draw_robot_maze_page(c, level, grid, arrows)
                    maze_solutions.append(arrows)

                for title, matrix in BINARY_PICTURES.items():
                    draw_binary_pixel_page(c, title, matrix)

            draw_answer_key_pages(c, unit_solutions)
            if mode in ("full", "coding"):
                draw_coding_answer_key(c, maze_solutions, BINARY_PICTURES)

            draw_certificate_page(c, cert_title)
            c.save()

            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            os.remove(pdf_path)

        st.success("Your KDP workbook PDF is ready!")
        st.download_button(
            label="📥 Download Print-Ready PDF",
            data=pdf_bytes,
            file_name=f"kdp_{mode}_workbook.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

with tab_preview:
    st.subheader("Test Grid Generator Live")
    preview_type = st.radio("Choose Preview Type", ["Bilingual Word Search", "Robot Algorithm Maze"], horizontal=True)

    if preview_type == "Bilingual Word Search":
        sample_words = [("Hello", "Bonjour"), ("Cat", "Chat"), ("Apple", "Pomme"), ("Sun", "Soleil"), ("Book", "Livre")]
        ws_grid, _, _ = generate_word_search(sample_words, size=10)
        grid_text = "\n".join("  ".join(row) for row in ws_grid)
        st.code(grid_text, language="text")
        st.caption("Hidden words: BONJOUR, CHAT, POMME, SOLEIL, LIVRE (Left-to-Right & Top-to-Bottom only)")
    else:
        maze_grid, _, arrows = generate_robot_maze(grid_size=6, num_obstacles=6)
        maze_text = "\n".join("  ".join(row) for row in maze_grid)
        st.code(maze_text, language="text")
        st.info(f"**Solution Path ({len(arrows)} steps):** {' → '.join(arrows)}")

with tab_data:
    st.subheader("Loaded Curriculum Datasets")
    dataset_choice = st.selectbox("Select Dataset", ["data/units_en_fr.json", "data/units_coding_kids.json"])
    units_data = load_full_units(dataset_choice)

    for unit_name, items in units_data.items():
        with st.expander(unit_name):
            st.table(items)
