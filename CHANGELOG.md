## 🎉 Initial Production Release (`v1.0.0`)

The **KDP Workbook Puzzle Engine** is now a complete, end-to-end publishing tool for generating print-ready **8.5" x 11" Amazon KDP educational workbooks** via both a command-line interface and an interactive web dashboard.

### ✨ What's Included in v1.0.0

#### 🖥️ Interactive Frontend (`app.py`)
- **Streamlit Web Dashboard:** Configure workbook editions (`full`, `bilingual`, `coding`, or `custom`), edit cover headings, and export print-ready PDFs directly in your browser.
- **Browser-Based Custom Unit Builder:** Add new vocabulary pairs and phonetic pronunciations on the fly without editing JSON files.
- **Live Grid Previews:** Inspect generated Word Searches and Robot Mazes before compiling your final book.

#### ⚙️ Unified Backend & PDF Engine (`main.py` & `src/`)
- **One-Command Mega Workbook Builder (`main.py`):** Compiles a **65+ page KDP interior** combining Bilingual French–English units, Screen-Free Coding units, Robot Grid Mazes, Binary Pixel Art, Answer Keys, and a Cut-Out Certificate.
- **Primary-School Handwriting Sheets (`src/pdf_exporter.py`):** Generates solid top/base lines and dashed midlines with traceable target words and phonetic guides.
- **Kid-Friendly Puzzle Solver (`src/puzzle_engine.py`):** Builds 10x10 Word Searches (left-to-right and top-to-bottom only for ages 5–8) and intersecting Crosswords with automatic Unicode accent normalization.
- **Unplugged Coding Activities (`src/coding_puzzles.py`):** Procedurally generates solvable Robot Algorithm Mazes and 8x8 Binary Pixel-Art challenges.
- **KDP Print Compliance:** Formatted to `8.5" x 11"` (No Bleed) with `0.65"` safe margins and automatic page numbering (`NumberedCanvas`) starting after the Title Page.

#### 📚 Built-In Curriculum Datasets (`data/`)
- `units_en_fr.json` — 10 everyday English–French beginner units (80 words + phonetics).
- `units_coding_kids.json` — 5 unplugged computer science units (40 terms + phonetics).

---

### 🚀 Quick Start

```bash
git clone https://github.com<your-username>/kdp-workbook-puzzle-engine.git
cd kdp-workbook-puzzle-engine
pip install -r requirements.txt

# Launch the web interface
streamlit run app.py

# Or generate the 65+ page PDF directly via CLI
python main.py --mode full
```
