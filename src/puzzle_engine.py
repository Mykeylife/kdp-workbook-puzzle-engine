import random
import string


def generate_word_search(words, size=10):
    """
    Generates a Word Search grid and its answer-key grid.

    Args:
        words: List of tuples (eng, fr, clean) from data_loader.
        size: Grid dimension (default 10x10).

    Returns:
        ws_grid: 2D list of uppercase letters (puzzle grid with random filler).
        ws_ans: 2D list of uppercase letters with '.' for unused cells (answer key).
        placed_words: List of (eng, fr, clean) tuples successfully placed in the grid.
    """
    grid = [['' for _ in range(size)] for _ in range(size)]
    placed_words = []

    # Sort longest words first for higher placement success
    sorted_words = sorted(words, key=lambda item: len(item[2]), reverse=True)
    directions = [(0, 1), (1, 0)]  # Across (right) and Down (matches PDF instructions)

    for eng, fr, clean in sorted_words:
        word = clean.upper()
        if len(word) > size or not word:
            continue

        placed = False
        attempts = 0
        while not placed and attempts < 150:
            attempts += 1
            dr, dc = random.choice(directions)
            max_r = size - (len(word) if dr == 1 else 1)
            max_c = size - (len(word) if dc == 1 else 1)

            if max_r < 0 or max_c < 0:
                continue

            start_r = random.randint(0, max_r)
            start_c = random.randint(0, max_c)

            # Check if word fits without conflicting with existing letters
            can_place = True
            for i, ch in enumerate(word):
                r = start_r + i * dr
                c = start_c + i * dc
                if grid[r][c] not in ('', ch):
                    can_place = False
                    break

            if can_place:
                for i, ch in enumerate(word):
                    r = start_r + i * dr
                    c = start_c + i * dc
                    grid[r][c] = ch
                placed_words.append((eng, fr, clean))
                placed = True

    # Build answer key grid (dots for non-word cells) and puzzle grid (random letters)
    ws_ans = [[cell if cell != '' else '.' for cell in row] for row in grid]
    ws_grid = [
        [cell if cell != '' else random.choice(string.ascii_uppercase) for cell in row]
        for row in grid
    ]

    # Preserve original order for the Word Bank display
    placed_set = set(placed_words)
    ordered_placed = [w for w in words if w in placed_set]

    return ws_grid, ws_ans, ordered_placed


def generate_crossword(words, size=12):
    """
    Generates an intersecting Crossword grid and numbered clue metadata.

    Args:
        words: List of tuples (eng, fr, clean) from data_loader.
        size: Grid dimension (default 12x12).

    Returns:
        cw_grid: 2D list of characters (' ' for empty cells, uppercase letters for filled).
        cw_placed: List of dicts with keys:
                   {'r', 'c', 'dir', 'eng', 'fr', 'clean', 'num'}
    """
    grid = [[' ' for _ in range(size)] for _ in range(size)]
    placed = []

    # Filter out words longer than grid and sort longest first
    valid_words = [w for w in words if 1 < len(w[2]) <= size]
    sorted_words = sorted(valid_words, key=lambda item: len(item[2]), reverse=True)

    if not sorted_words:
        return grid, placed

    def can_place_word(word, row, col, direction):
        dr, dc = (0, 1) if direction == "ACROSS" else (1, 0)
        end_r = row + dr * (len(word) - 1)
        end_c = col + dc * (len(word) - 1)

        if row < 0 or col < 0 or end_r >= size or end_c >= size:
            return False

        # Ensure cell immediately before start and after end are empty
        before_r, before_c = row - dr, col - dc
        after_r, after_c = end_r + dr, end_c + dc
        if 0 <= before_r < size and 0 <= before_c < size and grid[before_r][before_c] != ' ':
            return False
        if 0 <= after_r < size and 0 <= after_c < size and grid[after_r][after_c] != ' ':
            return False

        intersections = 0
        for i, ch in enumerate(word):
            r = row + dr * i
            c = col + dc * i
            existing = grid[r][c]

            if existing == ch:
                intersections += 1
            elif existing != ' ':
                return False
            else:
                # Check perpendicular neighbors so parallel words don't touch illegally
                if direction == "ACROSS":
                    if (r > 0 and grid[r - 1][c] != ' ') or (r < size - 1 and grid[r + 1][c] != ' '):
                        return False
                else:
                    if (c > 0 and grid[r][c - 1] != ' ') or (c < size - 1 and grid[r][c + 1] != ' '):
                        return False

        return intersections > 0

    def place_word_on_grid(eng, fr, clean, row, col, direction):
        word = clean.upper()
        dr, dc = (0, 1) if direction == "ACROSS" else (1, 0)
        for i, ch in enumerate(word):
            grid[row + dr * i][col + dc * i] = ch
        placed.append({
            "r": row,
            "c": col,
            "dir": direction,
            "eng": eng,
            "fr": fr,
            "clean": word,
        })

    # Place first (longest) word horizontally near the center
    first_eng, first_fr, first_clean = sorted_words[0]
    first_word = first_clean.upper()
    start_r = size // 2
    start_c = max(0, (size - len(first_word)) // 2)
    place_word_on_grid(first_eng, first_fr, first_clean, start_r, start_c, "ACROSS")

    # Attempt to intersect remaining words
    for eng, fr, clean in sorted_words[1:]:
        word = clean.upper()
        best_candidate = None

        for p in placed:
            p_word = p["clean"]
            p_dr, p_dc = (0, 1) if p["dir"] == "ACROSS" else (1, 0)
            new_dir = "DOWN" if p["dir"] == "ACROSS" else "ACROSS"
            new_dr, new_dc = (0, 1) if new_dir == "ACROSS" else (1, 0)

            for i, p_ch in enumerate(p_word):
                inter_r = p["r"] + p_dr * i
                inter_c = p["c"] + p_dc * i

                for j, w_ch in enumerate(word):
                    if p_ch == w_ch:
                        cand_r = inter_r - new_dr * j
                        cand_c = inter_c - new_dc * j
                        if can_place_word(word, cand_r, cand_c, new_dir):
                            best_candidate = (cand_r, cand_c, new_dir)
                            break
                if best_candidate:
                    break
            if best_candidate:
                break

        if best_candidate:
            place_word_on_grid(eng, fr, clean, *best_candidate)

    # Assign standard crossword numbers (top-to-bottom, left-to-right)
    start_coords = sorted({(p["r"], p["c"]) for p in placed})
    coord_to_num = {coord: idx + 1 for idx, coord in enumerate(start_coords)}

    for p in placed:
        p["num"] = coord_to_num[(p["r"], p["c"])]

    # Sort placed clues by number so Across and Down lists render in ascending order
    placed.sort(key=lambda item: (item["num"], item["dir"]))

    return grid, placed
