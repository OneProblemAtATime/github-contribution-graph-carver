import pygame
import csv
import sys

# Initialize Pygame
pygame.init()

# Constants
GRID_WIDTH = 52
GRID_HEIGHT = 7
TILE_SIZE = 16
PADDING = 3
SCREEN_WIDTH = GRID_WIDTH * (TILE_SIZE + PADDING)
SCREEN_HEIGHT = GRID_HEIGHT * (TILE_SIZE + PADDING)

# Colors corresponding to the levels of activity
COLORS = {
    0: "#161b22",  # No commits
    1: "#0e4429",  # 1-5 commits
    2: "#006d32",  # 6-10 commits
    3: "#26a641",  # 11-15 commits
    4: "#39d353"   # 16 or more commits
}

# Background color (black between tiles)
BACKGROUND_COLOR = (0, 0, 0)

# Pygame setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("GitHub Contribution Chart Editor")

# Function to convert hex color to pygame color
def hex_to_color(hex_color):
    return pygame.Color(*tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5)))

# Initial state of the grid (0 indicates no commits)
grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def draw_grid():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            color = hex_to_color(COLORS[grid[y][x]])
            rect = pygame.Rect(
                x * (TILE_SIZE + PADDING), 
                y * (TILE_SIZE + PADDING), 
                TILE_SIZE, TILE_SIZE
            )
            pygame.draw.rect(screen, color, rect)

def get_day_number(x, y):
    return y + x * 7 + 1  # Calculate day number starting from 1

def save_to_csv(filename='commits.csv'):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Day Number', 'Min Commits', 'Max Commits']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                level = grid[y][x]
                day_number = get_day_number(x, y)
                if level == 0:
                    min_commits, max_commits = 0, 0
                elif level == 1:
                    min_commits, max_commits = 1, 5
                elif level == 2:
                    min_commits, max_commits = 6, 10
                elif level == 3:
                    min_commits, max_commits = 11, 15
                elif level == 4:
                    min_commits, max_commits = 16, 20
                writer.writerow({
                    'Day Number': day_number, 
                    'Min Commits': min_commits, 
                    'Max Commits': max_commits
                })

def load_from_csv(filename='commits.csv'):
    try:
        with open(filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                day_number = int(row['Day Number'])
                min_commits = int(row['Min Commits'])
                
                # Determine the level based on min commits
                if min_commits == 0:
                    level = 0
                elif min_commits <= 5:
                    level = 1
                elif min_commits <= 10:
                    level = 2
                elif min_commits <= 15:
                    level = 3
                else:
                    level = 4

                x = (day_number - 1) // 7
                y = (day_number - 1) % 7
                grid[y][x] = level
    except FileNotFoundError:
        print(f"File {filename} not found.")
        sys.exit()

def clear_grid():
    global grid
    grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

def confirm_clear_grid():
    # Create a simple confirmation dialog
    font = pygame.font.SysFont(None, 40)
    small_font = pygame.font.SysFont(None, 30)
    yes_button = pygame.Rect(SCREEN_WIDTH//4 - 50, SCREEN_HEIGHT//2, 100, 50)
    no_button = pygame.Rect(SCREEN_WIDTH//4 * 3 - 50, SCREEN_HEIGHT//2, 100, 50)
    
    running = True
    while running:
        screen.fill((30, 30, 30))
        message = font.render("Clear existing grid?", True, (255, 255, 255))
        sub_message = small_font.render("Current data will be overwritten.", True, (255, 255, 255))
        yes_text = font.render("Yes", True, (255, 255, 255))
        no_text = font.render("No", True, (255, 255, 255))

        screen.blit(message, (SCREEN_WIDTH//2 - message.get_width()//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(sub_message, (SCREEN_WIDTH//2 - sub_message.get_width()//2, SCREEN_HEIGHT//2 - 60))
        pygame.draw.rect(screen, (0, 255, 0), yes_button)
        pygame.draw.rect(screen, (255, 0, 0), no_button)
        screen.blit(yes_text, (yes_button.x + (yes_button.width - yes_text.get_width()) // 2, yes_button.y + (yes_button.height - yes_text.get_height()) // 2))
        screen.blit(no_text, (no_button.x + (no_button.width - no_text.get_width()) // 2, no_button.y + (no_button.height - no_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if yes_button.collidepoint(event.pos):
                    running = False
                    return True
                elif no_button.collidepoint(event.pos):
                    running = False
                    return False
    return False

def update_grid_on_click(grid_x, grid_y, delta):
    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
        grid[grid_y][grid_x] = max(0, min(grid[grid_y][grid_x] + delta, 4))

# Main loop
running = True
left_mouse_down = False
right_mouse_down = False
modified_cells = set()  # Track which cells have been modified during the current mouse press

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            grid_x = mouse_x // (TILE_SIZE + PADDING)
            grid_y = mouse_y // (TILE_SIZE + PADDING)
            if event.button == 1:  # Left mouse button
                left_mouse_down = True
                update_grid_on_click(grid_x, grid_y, 1)
                modified_cells.add((grid_x, grid_y))
            elif event.button == 3:  # Right mouse button
                right_mouse_down = True
                update_grid_on_click(grid_x, grid_y, -1)
                modified_cells.add((grid_x, grid_y))
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                left_mouse_down = False
            elif event.button == 3:  # Right mouse button
                right_mouse_down = False
            modified_cells.clear()  # Clear modified cells on mouse release
        elif event.type == pygame.MOUSEMOTION:
            if left_mouse_down or right_mouse_down:
                mouse_x, mouse_y = event.pos
                grid_x = mouse_x // (TILE_SIZE + PADDING)
                grid_y = mouse_y // (TILE_SIZE + PADDING)
                if (grid_x, grid_y) not in modified_cells:
                    if left_mouse_down:
                        update_grid_on_click(grid_x, grid_y, 1)
                    elif right_mouse_down:
                        update_grid_on_click(grid_x, grid_y, -1)
                    modified_cells.add((grid_x, grid_y))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # Press 'S' to save
                save_to_csv()
            elif event.key == pygame.K_l:  # Press 'L' to load
                if confirm_clear_grid():
                    clear_grid()
                    load_from_csv()
            elif event.key == pygame.K_c:  # Press 'C' to clear all cells
                clear_grid()

    screen.fill(BACKGROUND_COLOR)
    draw_grid()
    pygame.display.flip()

# Save the grid to CSV when exiting
save_to_csv()
pygame.quit()
