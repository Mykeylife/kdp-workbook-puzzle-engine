### 2. Updated `README.md` (Documenting CLI + Streamlit Web UI)

```markdown
# 📚 KDP Workbook Puzzle Engine

An end-to-end Python publishing engine and **Streamlit web application** that transforms structured curriculum datasets into print-ready **8.5" x 11" Amazon KDP educational workbooks**.

Built to automate the creation of **Bilingual Vocabulary Builders** and **Screen-Free Logic & Coding Activity Books** for children ages 5–9.

---

## ✨ Key Features

- **Interactive Streamlit Web Dashboard (`app.py`):** Configure book titles, build custom vocabulary units in the browser, preview live puzzle grids, and download print-ready PDFs in one click.
- **Unified CLI Generator (`main.py`):** Build 65+ page Mega Workbooks, Bilingual editions, or Coding editions directly from the command line.
- **Primary-School Handwriting Pages:** Automatically generates solid baseline/topline and dashed midline tracing sheets with phonetic pronunciation guides.
- **Age-Appropriate Grid Logic:** Restricts Word Search placement to left-to-right and top-to-bottom orientations (no backwards or diagonal words) for young learners, with automatic Unicode accent normalization (`Éléphant` → `ELEPHANT`).
- **Unplugged Coding Activities:** Procedurally generates solvable **Robot Algorithm Grid Mazes** and **Binary Pixel-Art** challenges.
- **KDP-Ready Formatting:** Outputs **8.5" x 11" (No Bleed)** black-and-white interiors with `0.65"` safe margins, automatic page numbering (skipping the title page), complete Answer Keys, and a Cut-Out Certificate of Achievement.

---

## 🗂️ Project Structure

```text
kdp-workbook-puzzle-engine/
├── app.py                     # Streamlit web UI & Custom Unit Builder
├── main.py                    # Unified CLI entry point (65+ page PDF builder)
├── requirements.txt           # Project dependencies (reportlab, streamlit)
├── .gitignore                 # Excludes generated PDFs & cache files
├── README.md
├── data/
│   ├── units_en_fr.json       # 10 English–French units (80 words + phonetics)
│   └── units_coding_kids.json # 5 Unplugged Coding units (40 terms + phonetics)
├── src/
│   ├── data_loader.py         # JSON curriculum loader
│   ├── puzzle_engine.py       # Word search & intersecting crossword solver
│   ├── pdf_exporter.py        # ReportLab page layouts, tracing & certificate
│   └── coding_puzzles.py      # Robot maze pathfinder & binary pixel art
└── output/                    # Local PDF output folder (ignored by Git)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com<your-username>/kdp-workbook-puzzle-engine.git
   cd kdp-workbook-puzzle-engine
   ```

git clone https://github.com/<your-username>/kdp-workbook-puzzle-engine.git
cd kdp-workbook-puzzle-engine
pip install -r requirements.txt

2. **Install dependencies:**
   ```bash
   pip install reportlab
   ```

3. **Generate puzzles and export KDP PDF:**
   ```bash
   python src/pdf_exporter.py
   ```
   Your print-ready PDF (`bilingual_puzzles_kdp.pdf`) will be saved inside the `output/` directory.

## Customization

To generate puzzles for a new language pair or subject (e.g., English–Spanish or ESL Sight Words), add a new JSON file in `data/` following this schema:

```json
{
  "Unit 1: Greetings & Politeness": [
    ["Hello", "Bonjour"],
    ["Thank you", "Merci"]
  ]
}
```

## License

MIT License — feel free to use and adapt the puzzle engine for educational projects.
