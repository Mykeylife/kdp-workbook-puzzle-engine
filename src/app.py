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

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import (
    NumberedCanvas,
    draw_title_page,
    append_vocab_section,
)
from data_loader import load_full_units
from puzzle_engine import generate_word_search, generate_crossword
from pdf_exporter import (
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

# ==========================================
# PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="KDP Workbook Puzzle Engine",
    page_icon="📚",
    layout="wide",
)

st.title("📚 KDP Workbook Puzzle Engine")
st.caption("Generate print-ready 8.5\" x 11\" educational workbooks with tracing, puzzles, mazes, and answer keys.")

# Initialize session state for custom units
if "custom_units" not in st.session_state:
    st.session_state.custom_units = {}

# ==========================================
# SIDEBAR: WORKBOOK CONFIGURATION
# ==========================================
with st.sidebar:
    st.header("⚙️ Workbook Settings")

    mode = st.selectbox(
        "Workbook Edition",
        options=["full", "bilingual", "coding", "custom"],
        format_func=lambda x: {
            "full": "Mega Workbook (Bilingual + Coding, 65+ Pages)",
            "bilingual": "English–French Bilingual Workbook",
            "coding": "Screen-Free Logic & Coding Workbook",
            "custom": "Custom Units Only (Built in Browser)",
        }[x],
    )

    default_titles = {
        "full": ("MEGA KIDS ACTIVITY WORKBOOK", "Bilingual French–English, Unplugged Coding & Brain Puzzles"),
        "bilingual": ("ENGLISH–FRENCH WORKBOOK", "Bilingual Vocabulary, Handwriting & Brain Puzzles (Ages 5–8)"),
        "coding": ("SCREEN-FREE CODING & LOGIC", "Unplugged Algorithms, Robot Mazes & Binary Pixel Art (Ages 6–9)"),
        "custom": ("CUSTOM ACTIVITY WORKBOOK", "Vocabulary Tracing, Word Searches & Crossword Puzzles"),
    }

    book_title = st.text_input("Title Page Heading", value=default_titles[mode])
    book_subtitle = st.text_input("Title Page Subtitle", value=default_titles[mode])
    cert_title = st.text_input("Certificate Book Name", value=book_title.title())

    include_custom = st.checkbox(
        "Append my Custom Units to this book",
        value=True,
        disabled=(mode == "custom"),
    )

    maze_count = st.slider(
        "Number of Robot Grid Mazes",
        min_value=2,
        max_value=12,
        value=8,
        disabled=(mode in ("bilingual", "custom")),
    )

# ==========================================
# MAIN TABS
# ==========================================
tab_build, tab_custom, tab_preview, tab_data = st.tabs([
    "🚀 Build & Download PDF",
    "✍️ Custom Unit Builder",
    "🔍 Live Puzzle Preview",
    "📖 Loaded Datasets",
])

with tab_build:
    st.subheader("Generate Print-Ready KDP Interior")
    st.write(
        "Your PDF is formatted to **8.5\" x 11\" (No Bleed)** with **0.65\" safe margins**, "
        "automatic page numbering, complete answer keys, and a cut-out certificate."
    )

    custom_count = len(st.session_state.custom_units)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Trim Size", "8.5\" x 11\"")
    col2.metric("Interior Style", "Black & White")
    col3.metric("Custom Units Added", f"{custom_count} Unit(s)")
    col4.metric("Target Format", "KDP Print PDF")

    if mode == "custom" and custom_count == 0:
        st.warning("You selected 'Custom Units Only', but haven't added any units yet. Open the **Custom Unit Builder** tab to create one first!")
    else:
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

                # Append any custom units built in the browser
                if (mode == "custom" or include_custom) and st.session_state.custom_units:
                    for unit_title, items in st.session_state.custom_units.items():
                        word_pairs = [(entry["en"], entry["fr"]) for entry in items]
                        draw_tracing_page(c, unit_title, items)

                        ws_grid, ws_ans, ws_words = generate_word_search(word_pairs, size=10)
                        cw_grid, cw_placed = generate_crossword(word_pairs, size=12)

                        draw_word_search_page(c, unit_title, ws_grid, ws_words)
                        draw_crossword_page(c, unit_title, cw_grid, cw_placed)
                        unit_solutions.append((unit_title, ws_ans, cw_grid))

                if mode in ("full", "coding"):
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

with tab_custom:
    st.subheader("Create a New Workbook Unit in Browser")
    st.write("Enter up to 8 word pairs below (e.g., English → Spanish, ESL Sight Words, or Science Terms) to add a 3-page Trace + Word Search + Crossword unit.")

    with st.form("custom_unit_form"):
        new_unit_title = st.text_input("Unit Title", placeholder="e.g., Unit 11: Space & Planets")
        st.markdown("**Enter Vocabulary Words (up to 8 pairs):**")

        entries = []
        for i in range(8):
            c1, c2, c3 = st.columns([2, 2, 2])
            en_val = c1.text_input(f"Clue / English #{i+1}", key=f"en_{i}", placeholder="e.g., Star")
            fr_val = c2.text_input(f"Target Word #{i+1}", key=f"fr_{i}", placeholder="e.g., Étoile")
            ph_val = c3.text_input(f"Phonetic (Optional) #{i+1}", key=f"ph_{i}", placeholder="e.g., ay-TWAHL")
            if en_val.strip() and fr_val.strip():
                entries.append({
                    "en": en_val.strip(),
                    "fr": fr_val.strip(),
                    "phonetic": ph_val.strip(),
                })

        submitted = st.form_submit_button("➕ Save Custom Unit", type="primary")
        if submitted:
            if not new_unit_title.strip():
                st.error("Please enter a Unit Title.")
            elif len(entries) < 3:
                st.error("Please enter at least 3 word pairs so the crossword can intersect properly.")
            else:
                st.session_state.custom_units[new_unit_title.strip()] = entries
                st.success(f"Saved '{new_unit_title.strip()}' with {len(entries)} words!")

    if st.session_state.custom_units:
        st.divider()
        st.markdown("### Saved Custom Units")
        for u_title, u_items in list(st.session_state.custom_units.items()):
            col_a, col_b = st.columns([5, 1])
            col_a.write(f"**{u_title}** ({len(u_items)} words)")
            if col_b.button("🗑️ Remove", key=f"del_{u_title}"):
                del st.session_state.custom_units[u_title]
                st.rerun()

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
