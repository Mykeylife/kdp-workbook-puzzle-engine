import random
import re
import string


def _unpack_word(word_tuple):
    """Supports both (eng, fr) and (eng, fr, clean) tuples."""
    if len(word_tuple) >= 3:
        eng, fr, clean = word_tuple
    else:
        eng, fr = word_tuple
        clean = re.sub(r"[^A-Za-z]", "", fr).upper()
    return eng, fr, clean


def _clean_len(word_tuple):
    _, _, clean = _unpack_word(word_tuple)
    return len(clean)


def generate_word_search(words, size=10):
    """
    Generates a Word Search grid and its answer-key grid.
    """
    grid = [['' for _ in range(size)] for _ in range(size)]
    normalized = [_unpack_word(w) for w in words]
    placed_words = []

    sorted_words = sorted(normalized, key=_clean_len, reverse=True)
    directions = [(0, 1), (1, 0)]  # Across (right) and Down

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

    ws_ans = [[cell if cell != '' else '.' for cell in row] for row in grid]
    ws_grid = [
        [cell if cell != '' else random.choice(string.ascii_uppercase) for cell in row]
        for row in grid
    ]

    placed_set = set(placed_words)
    ordered_placed = [w for w in normalized if w in placed_set]

    return ws_grid, ws_ans, ordered_placed


def generate_crossword(words, size=12):
    """
    Generates an intersecting Crossword grid and numbered clue metadata.
    """
    grid = [[' ' for _ in range(size)] for _ in range(size)]
    normalized = [_unpack_word(w) for w in words]
    placed = []

    valid_words = [w for w in normalized if 1 < _clean_len(w) <= size]
    sorted_words = sorted(valid_words, key=_clean_len, reverse=True)

    if not sorted_words:
        return grid, placed

    def can_place_word(word, row, col, direction):
        dr, dc = (0, 1) if direction == "ACROSS" else (1, 0)
        end_r = row + dr * (len(word) - 1)
        end_c = col + dc * (len(word) - 1)

        if row < 0 or col < 0 or end_r >= size or end_c >= size:
            return False

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

    first_item, *remaining_words = sorted_words
    first_eng, first_fr, first_clean = first_item
    first_word = first_clean.upper()
    start_r = size // 2
    start_c = max(0, (size - len(first_word)) // 2)
    place_word_on_grid(first_eng, first_fr, first_clean, start_r, start_c, "ACROSS")

    for eng, fr, clean in remaining_words:
        word = clean.upper()
        best_candidate = None

        for p in placed:
            p_word = p.get("clean")
            p_dir = p.get("dir")
            p_r = p.get("r")
            p_c = p.get("c")
            p_dr, p_dc = (0, 1) if p_dir == "ACROSS" else (1, 0)
            new_dir = "DOWN" if p_dir == "ACROSS" else "ACROSS"
            new_dr, new_dc = (0, 1) if new_dir == "ACROSS" else (1, 0)

            for i, p_ch in enumerate(p_word):
                inter_r = p_r + p_dr * i
                inter_c = p_c + p_dc * i

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

    start_coords = sorted({(p.get("r"), p.get("c")) for p in placed})
    coord_to_num = {coord: idx + 1 for idx, coord in enumerate(start_coords)}

    for p in placed:
        p["num"] = coord_to_num.get((p.get("r"), p.get("c")))

    placed.sort(key=lambda item: (item.get("num"), item.get("dir")))

    return grid, placed
