import os
import random
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors

PAGE_WIDTH, PAGE_HEIGHT = letter
MARGIN = 46.8  # 0.65 inches


# ==========================================
# 1. ROBOT GRID MAZE GENERATOR
# ==========================================
def generate_robot_maze(grid_size=6, num_obstacles=7):
    """Generates a solvable grid maze with a guaranteed path from (0,0) to (N-1,N-1)."""
    while True:
        grid = [['.' for _ in range(grid_size)] for _ in range(grid_size)]
        r, c = 0, 0
        path = [(r, c)]
        arrows = []

        # Carve a guaranteed winding path to the goal
        while (r, c) != (grid_size - 1, grid_size - 1):
            moves = []
            if r < grid_size - 1:
                moves.append((1, 0, "DOWN"))
            if c < grid_size - 1:
                moves.append((0, 1, "RIGHT"))
            # Occasionally step up or left if safe to make paths more interesting
            if r > 0 and (r - 1, c) not in path and random.random() < 0.25:
                moves.append((-1, 0, "UP"))
            if c > 0 and (r, c - 1) not in path and random.random() < 0.25:
                moves.append((0, -1, "LEFT"))

            dr, dc, direction = random.choice(moves)
            r += dr
            c += dc
            path.append((r, c))
            arrows.append(direction)

        # Place obstacles only on cells NOT in the solution path
        available_cells = [
            (rr, cc)
            for rr in range(grid_size)
            for cc in range(grid_size)
            if (rr, cc) not in path
        ]
        if len(available_cells) >= num_obstacles and len(arrows) <= 14:
            for orow, ocol in random.sample(available_cells, num_obstacles):
                grid[orow][ocol] = '#'
            grid[0][0] = 'R'
            grid[grid_size - 1][grid_size - 1] = 'G'
            return grid, path, arrows


# ==========================================
# 2. BINARY PIXEL-ART PATTERNS (8x8 GRIDS)
# ==========================================
BINARY_PICTURES = {
    "Mystery Picture 1": [,
 ,
 ,
 ,
 ,
 ,
 ,
 ,
    ],
    "Mystery Picture 2": [,
 ,
 ,
 ,
 ,
 ,
 ,
 ,
    ],
    "Mystery Picture 3": [,
 ,
 ,
 ,
 ,
 ,
 ,
 ,
    ],
    "Mystery Picture 4": [,
 ,
 ,
 ,
 ,
 ,
 ,
 ,
    ]
}


# ==========================================
# 3. PDF PAGE RENDERERS
# ==========================================
def draw_header(c, title, subtitle):
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - MARGIN - 10, title)
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.darkgray)
    c.drawCentredString(PAGE_WIDTH / 2, PAGE_HEIGHT - MARGIN - 28, subtitle)
    c.setFillColor(colors.black)


def draw_robot_maze_page(c, level_num, grid, arrows):
    draw_header(
        c,
        f"Algorithm Challenge #{level_num}: Program the Robot",
        "Write arrows (UP, DOWN, LEFT, RIGHT) in the boxes to guide ROBOT to GOAL!"
    )

    grid_size = len(grid)
    cell_size = 52
    total_w = grid_size * cell_size
    start_x = (PAGE_WIDTH - total_w) / 2
    start_y = PAGE_HEIGHT - MARGIN - 65

    c.setLineWidth(1.5)
    for r in range(grid_size):
        for col in range(grid_size):
            x = start_x + col * cell_size
            y = start_y - (r + 1) * cell_size
            val = grid[r][col]

            if val == '#':
                c.setFillColor(colors.lightgrey)
                c.rect(x, y, cell_size, cell_size, stroke=1, fill=1)
                c.setFillColor(colors.black)
                c.setFont("Helvetica-Bold", 10)
                c.drawCentredString(x + cell_size / 2, y + cell_size / 2 - 4, "ROCK")
            else:
                c.rect(x, y, cell_size, cell_size, stroke=1, fill=0)
                if val == 'R':
                    c.setFont("Helvetica-Bold", 12)
                    c.drawCentredString(x + cell_size / 2, y + cell_size / 2 - 4, "ROBOT")
                elif val == 'G':
                    c.setFont("Helvetica-Bold", 12)
                    c.drawCentredString(x + cell_size / 2, y + cell_size / 2 - 4, "GOAL")

    # Draw empty Code Sequence Boxes below the grid
    code_y = start_y - total_w - 40
    c.setFont("Helvetica-Bold", 12)
    c.drawString(MARGIN + 15, code_y, f"Your Code Sequence ({len(arrows)} steps needed):")

    box_size = 38
    gap = 8
    cols_per_row = 10
    for idx in range(len(arrows)):
        row_idx = idx // cols_per_row
        col_idx = idx % cols_per_row
        bx = MARGIN + 15 + col_idx * (box_size + gap)
        by = code_y - 48 - row_idx * (box_size + 18)

        c.setFont("Helvetica", 8)
        c.drawString(bx + 2, by + box_size + 3, f"Step {idx + 1}")
        c.rect(bx, by, box_size, box_size)

    c.showPage()


def draw_binary_pixel_page(c, title, matrix):
    draw_header(
        c,
        f"Binary Pixel Art: {title}",
        "Color each square BLACK if the code is 1. Leave it WHITE if the code is 0!"
    )

    rows = len(matrix)
    cols = len(matrix)
    cell_size = 38
    grid_w = cols * cell_size
    start_x = MARGIN + 175
    start_y = PAGE_HEIGHT - MARGIN - 90

    c.setLineWidth(1.2)
    for r in range(rows):
        # Print binary code string to the left of each row
        binary_str = "  ".join(str(bit) for bit in matrix[r])
        c.setFont("Courier-Bold", 13)
        c.drawString(MARGIN + 10, start_y - r * cell_size - 24, binary_str)

        for col in range(cols):
            x = start_x + col * cell_size
            y = start_y - (r + 1) * cell_size
            c.rect(x, y, cell_size, cell_size)

    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(PAGE_WIDTH / 2, start_y - grid_w - 45, "What picture did your binary code create? ________________________")
    c.showPage()


def draw_coding_answer_key(c, maze_solutions, pixel_solutions):
    draw_header(c, "Coding & Logic Answer Key", "Solutions for Robot Mazes and Binary Pixel Art")
    y_cursor = PAGE_HEIGHT - MARGIN - 60

    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, y_cursor, "Robot Algorithm Solutions:")
    y_cursor -= 20

    c.setFont("Helvetica", 10)
    for idx, arrows in enumerate(maze_solutions, start=1):
        seq_str = " -> ".join(arrows)
        c.drawString(MARGIN + 10, y_cursor, f"Challenge #{idx}: {seq_str}")
        y_cursor -= 18

    y_cursor -= 25
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN, y_cursor, "Binary Pixel-Art Solutions:")
    y_cursor -= 20

    cell = 12
    for idx, (title, matrix) in enumerate(pixel_solutions.items()):
        gx = MARGIN + 15 + (idx * 125)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(gx, y_cursor, title)

        for r in range(len(matrix)):
            for col in range(len(matrix)):
                fill_val = 1 if matrix[r][col] == 1 else 0
                c.rect(gx + col * cell, y_cursor - 15 - (r + 1) * cell, cell, cell, stroke=1, fill=fill_val)

    c.showPage()


def build_coding_activities_pdf(output_path="output/coding_activities_kdp.pdf"):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(base_dir, output_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    c = canvas.Canvas(full_path, pagesize=letter)
    maze_solutions = []

    # Generate 4 progressive Robot Grid Mazes
    for level in range(1, 5):
        grid, _, arrows = generate_robot_maze(grid_size=6, num_obstacles=5 + level)
        draw_robot_maze_page(c, level, grid, arrows)
        maze_solutions.append(arrows)

    # Generate 4 Binary Pixel-Art Challenges
    for title, matrix in BINARY_PICTURES.items():
        draw_binary_pixel_page(c, title, matrix)

    draw_coding_answer_key(c, maze_solutions, BINARY_PICTURES)
    c.save()
    print(f"Successfully generated Coding Activities PDF at: {full_path}")


if __name__ == "__main__":
    build_coding_activities_pdf()
