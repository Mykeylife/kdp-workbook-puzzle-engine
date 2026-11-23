import random
import unicodedata

# All 10 Units from your English-French Workbook
WORKBOOK_UNITS = {
    "Unit 1: Greetings & Politeness": [
        ("Hello", "Bonjour"), ("Goodbye", "Au revoir"), ("Please", "S'il vous plaît"),
        ("Thank you", "Merci"), ("Yes", "Oui"), ("No", "Non"),
        ("Good morning", "Bon matin"), ("Good night", "Bonne nuit")
    ],
    "Unit 2: Numbers & Colors": [
        ("One", "Un"), ("Two", "Deux"), ("Three", "Trois"), ("Four", "Quatre"),
        ("Red", "Rouge"), ("Blue", "Bleu"), ("Yellow", "Jaune"), ("Green", "Vert")
    ],
    "Unit 3: My Family": [
        ("Mother", "Mère"), ("Father", "Père"), ("Brother", "Frère"),
        ("Sister", "Sœur"), ("Baby", "Bébé"), ("Grandmother", "Grand-mère"),
        ("Grandfather", "Grand-père"), ("Family", "Famille")
    ],
    "Unit 4: Animals": [
        ("Dog", "Chien"), ("Cat", "Chat"), ("Lion", "Lion"),
        ("Elephant", "Éléphant"), ("Bird", "Oiseau"), ("Fish", "Poisson"),
        ("Cow", "Vache"), ("Monkey", "Singe")
    ],
    "Unit 5: Food & Drinks": [
        ("Apple", "Pomme"), ("Banana", "Banane"), ("Bread", "Pain"),
        ("Water", "Eau"), ("Milk", "Lait"), ("Rice", "Riz"),
        ("Egg", "Œuf"), ("Cake", "Gâteau")
    ]
}

def clean_for_grid(word):
    """Removes spaces, hyphens, apostrophes, and accents for grid placement."""
    word = word.replace("Œ", "OE").replace("œ", "oe")
    nfkd = unicodedata.normalize('NFKD', word)
    only_ascii = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return "".join([c.upper() for c in only_ascii if c.isalpha()])

# ==========================================
# 1. KID-FRIENDLY WORD SEARCH GENERATOR
# ==========================================
def generate_word_search(word_pairs, size=10):
    grid = [[' ' for _ in range(size)] for _ in range(size)]
    answer_grid = [['.' for _ in range(size)] for _ in range(size)]
    # Kids ages 5-8 do best with Horizontal (0,1) and Vertical (1,0) only
    directions = [(0, 1), (1, 0)]
    placed_words = []

    # Sort longest words first for easier placement
    sorted_pairs = sorted(word_pairs, key=lambda x: len(clean_for_grid(x[1])), reverse=True)

    for eng, fr in sorted_pairs:
        clean_fr = clean_for_grid(fr)
        if len(clean_fr) > size:
            continue

        placed = False
        attempts = 0
        while not placed and attempts < 100:
            attempts += 1
            dr, dc = random.choice(directions)
            r = random.randint(0, size - 1 - (dr * (len(clean_fr) - 1)))
            c = random.randint(0, size - 1 - (dc * (len(clean_fr) - 1)))

            if all(grid[r + i*dr][c + i*dc] in (' ', clean_fr[i]) for i in range(len(clean_fr))):
                for i in range(len(clean_fr)):
                    grid[r + i*dr][c + i*dc] = clean_fr[i]
                    answer_grid[r + i*dr][c + i*dc] = clean_fr[i]
                placed_words.append((eng, fr, clean_fr))
                placed = True

    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for r in range(size):
        for c in range(size):
            if grid[r][c] == ' ':
                grid[r][c] = random.choice(alphabet)

    return grid, answer_grid, placed_words

# ==========================================
# 2. SIMPLE INTERSECTING CROSSWORD GENERATOR
# ==========================================
def generate_crossword(word_pairs, size=12):
    grid = [[' ' for _ in range(size)] for _ in range(size)]
    items = [(eng, fr, clean_for_grid(fr)) for eng, fr in word_pairs if len(clean_for_grid(fr)) <= size]
    items.sort(key=lambda x: len(x[2]), reverse=True)

    placed = []
    # Place first word horizontally in the middle
    first_eng, first_fr, first_clean = items[0]
    start_r, start_c = size // 2, (size - len(first_clean)) // 2
    for i, ch in enumerate(first_clean):
        grid[start_r][start_c + i] = ch
    placed.append({"num": 1, "dir": "ACROSS", "r": start_r, "c": start_c, "eng": first_eng, "fr": first_fr, "clean": first_clean})

    num_counter = 2
    for eng, fr, clean in items[1:]:
        found_spot = False
        for p in placed:
            if found_spot:
                break
            for idx_existing, ch_existing in enumerate(p["clean"]):
                if found_spot:
                    break
                for idx_new, ch_new in enumerate(clean):
                    if ch_existing == ch_new:
                        # Try placing perpendicular
                        new_dir = "DOWN" if p["dir"] == "ACROSS" else "ACROSS"
                        if new_dir == "DOWN":
                            r = p["r"] - idx_new
                            c = p["c"] + idx_existing
                        else:
                            r = p["r"] + idx_existing
                            c = p["c"] - idx_new

                        if can_place_crossword(grid, clean, r, c, new_dir, size):
                            for i, ch in enumerate(clean):
                                rr = r + (i if new_dir == "DOWN" else 0)
                                cc = c + (i if new_dir == "ACROSS" else 0)
                                grid[rr][cc] = ch
                            placed.append({"num": num_counter, "dir": new_dir, "r": r, "c": c, "eng": eng, "fr": fr, "clean": clean})
                            num_counter += 1
                            found_spot = True
                            break
    return grid, placed

def can_place_crossword(grid, word, r, c, direction, size):
    dr, dc = (1, 0) if direction == "DOWN" else (0, 1)
    if r < 0 or c < 0 or r + dr*(len(word)-1) >= size or c + dc*(len(word)-1) >= size:
        return False
    # Check cell before and after word so words don't merge accidentally
    if r - dr >= 0 and c - dc >= 0 and grid[r - dr][c - dc] != ' ':
        return False
    if r + dr*len(word) < size and c + dc*len(word) < size and grid[r + dr*len(word)][c + dc*len(word)] != ' ':
        return False

    intersections = 0
    for i, ch in enumerate(word):
        rr, cc = r + i*dr, c + i*dc
        if grid[rr][cc] == ch:
            intersections += 1
        elif grid[rr][cc] != ' ':
            return False
        else:
            # Ensure parallel neighbors are empty
            for nr, nc in [(rr+dc, cc+dr), (rr-dc, cc-dr)]:
                if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] != ' ':
                    return False
    return intersections >= 1

# ==========================================
# RUN & PRINT PUZZLES FOR YOUR WORKBOOK
# ==========================================
if __name__ == "__main__":
    for unit_title, words in WORKBOOK_UNITS.items():
        print("=" * 50)
        print(f"{unit_title.upper()}")
        print("=" * 50)

        # 1. Print Word Search
        ws_grid, ws_ans, ws_words = generate_word_search(words, size=10)
        print("\n[WORD SEARCH PUZZLE - Find the French Words!]")
        for row in ws_grid:
            print("  " + " ".join(row))
        print("\nClues (English -> French to find):")
        for eng, fr, clean in ws_words:
            print(f"  - {eng} ({fr})")

        print("\n[WORD SEARCH ANSWER KEY]")
        for row in ws_ans:
            print("  " + " ".join(row))

        # 2. Print Crossword
        cw_grid, cw_placed = generate_crossword(words, size=12)
        print("\n[CROSSWORD PUZZLE - Write the French Word!]")
        for r in range(len(cw_grid)):
            row_str = []
            for c in range(len(cw_grid)):
                # Check if a word starts here
                start_nums = [str(p["num"]) for p in cw_placed if p["r"] == r and p["c"] == c]
                if start_nums:
                    row_str.append(f"[{start_nums[0]}]")
                elif cw_grid[r][c] != ' ':
                    row_str.append("[ ]")
                else:
                    row_str.append(" . ")
            print("  " + "".join(row_str))

        print("\nCrossword Clues:")
        for p in cw_placed:
            print(f"  {p['num']}. {p['dir']}: {p['eng']} ({len(p['clean'])} letters)")

        print("\n[CROSSWORD ANSWER KEY]")
        for row in cw_grid:
            print("  " + " ".join(ch if ch != ' ' else '.' for ch in row))
        print("\n")
