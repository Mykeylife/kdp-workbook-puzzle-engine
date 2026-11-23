# KDP Workbook Puzzle Engine

An automated Python generator that converts structured vocabulary data into kid-friendly **Word Searches**, **Intersecting Crosswords**, and **Answer Keys** formatted for **8.5" x 11" Amazon KDP educational workbooks**.

## Features

- **Age-Appropriate Grid Logic:** Restricts word search placement to left-to-right and top-to-bottom orientations (no backwards or diagonal words) to prevent frustration for young learners (ages 5–8).
- **Unicode & Accent Normalization:** Automatically strips diacritics and ligatures (e.g., `Éléphant` → `ELEPHANT`, `Œuf` → `OEUF`) for clean grid placement while preserving proper accented spelling in clue lists.
- **Intersecting Crossword Solver:** Places vocabulary words dynamically with shared intersections and automatic numbering.
- **KDP-Ready PDF Export:** Renders print-ready **8.5" x 11" (No Bleed)** black-and-white interior pages with safe `0.65"` margins and a separate Answer Key section.

## Project Structure

```text
kdp-workbook-puzzle-engine/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── units_en_fr.json       # Structured unit vocabulary lists
├── src/
│   ├── puzzle_engine.py       # Core grid generation & accent normalization
│   └── pdf_exporter.py        # ReportLab 8.5x11 KDP PDF page renderer
└── output/                    # Generated PDFs (excluded from Git)
```

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com<your-username>/kdp-workbook-puzzle-engine.git
   cd kdp-workbook-puzzle-engine
   ```

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
