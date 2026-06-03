import pygame
import random
import time

pygame.init()

# =====================================================
# WINDOW
# =====================================================

WIDTH = 1024
HEIGHT = 768

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pattern Memory Task")

clock = pygame.time.Clock()

# =====================================================
# COLORS
# =====================================================

BLUE_BG = (0, 0, 140)
CYAN = (30, 220, 220)
RED = (255, 20, 20)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# =====================================================
# FONTS
# =====================================================

font = pygame.font.SysFont("arial", 28, bold=True)

# =====================================================
# STATS
# =====================================================

trial = 0
correct = 0
incorrect = 0
last_rt = None
flash_red_until = 0
FLASH_DURATION = 250  # milliseconds

# =====================================================
# PATTERN GENERATION
# =====================================================

GRID_SIZE = 4


def create_pattern():
    return [
        [random.choice([0, 1]) for _ in range(GRID_SIZE)]
        for _ in range(GRID_SIZE)
    ]


def create_distractor(pattern):
    new_pattern = [row[:] for row in pattern]

    flips = random.randint(1, 3)

    for _ in range(flips):
        r = random.randint(0, 3)
        c = random.randint(0, 3)
        new_pattern[r][c] = 1 - new_pattern[r][c]

    return new_pattern


# =====================================================
# DRAWING
# =====================================================

CELL_SIZE = 48


def draw_pattern(pattern, center_x, center_y):

    size = GRID_SIZE * CELL_SIZE

    start_x = center_x - size // 2
    start_y = center_y - size // 2

    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):

            color = CYAN if pattern[r][c] else RED

            rect = pygame.Rect(
                start_x + c * CELL_SIZE,
                start_y + r * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLUE_BG, rect, 2)


def draw_status():

    bar_y = HEIGHT - 80

    pygame.draw.line(
        screen,
        WHITE,
        (0, bar_y),
        (WIDTH, bar_y),
        2
    )

    acc = (
        0
        if trial == 0
        else round(correct / trial * 100, 1)
    )

    rt_text = "--" if last_rt is None else str(int(last_rt))

    texts = [
        f"Trial: {trial}",
        f"Correct: {correct}",
        f"Incorrect: {incorrect}",
        f"Accuracy: {acc}%",
        f"RT: {rt_text} ms"
    ]

    section = WIDTH / 5

    for i, text in enumerate(texts):

        surf = font.render(text, True, WHITE)

        rect = surf.get_rect(
            center=(section * i + section / 2,
                    HEIGHT - 40)
        )

        screen.blit(surf, rect)


# =====================================================
# GAME STATES
# =====================================================

SHOW_PATTERN = 0
BLANK = 1
CHOICE = 2

state = SHOW_PATTERN

pattern = create_pattern()
distractor = create_distractor(pattern)

original_on_left = random.choice([True, False])

state_start = time.perf_counter()
choice_start = None

# =====================================================
# MAIN LOOP
# =====================================================

running = True

while running:

    clock.tick(60)

    if pygame.time.get_ticks() < flash_red_until:
        screen.fill(RED)
    else:
        screen.fill(BLUE_BG)

    now = time.perf_counter()

    # ---------------------------------
    # SHOW ORIGINAL
    # ---------------------------------

    if state == SHOW_PATTERN:

        draw_pattern(
            pattern,
            WIDTH // 2,
            HEIGHT // 2 - 50
        )

        if now - state_start >= 2:
            state = BLANK
            state_start = now

    # ---------------------------------
    # BLANK SCREEN
    # ---------------------------------

    elif state == BLANK:

        if now - state_start >= 1:
            state = CHOICE
            state_start = now
            choice_start = now

    # ---------------------------------
    # CHOICE SCREEN
    # ---------------------------------

    elif state == CHOICE:

        if original_on_left:

            draw_pattern(
                pattern,
                WIDTH // 3,
                HEIGHT // 2 - 50
            )

            draw_pattern(
                distractor,
                WIDTH * 2 // 3,
                HEIGHT // 2 - 50
            )

        else:

            draw_pattern(
                distractor,
                WIDTH // 3,
                HEIGHT // 2 - 50
            )

            draw_pattern(
                pattern,
                WIDTH * 2 // 3,
                HEIGHT // 2 - 50
            )

    draw_status()

    pygame.display.flip()

    # =================================================
    # EVENTS
    # =================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if state == CHOICE:

            if event.type == pygame.MOUSEBUTTONDOWN:

                rt = (
                    time.perf_counter()
                    - choice_start
                ) * 1000

                last_rt = rt

                response_correct = False

                # LEFT CLICK = LEFT SIDE
                if event.button == 1:

                    response_correct = original_on_left

                # RIGHT CLICK = RIGHT SIDE
                elif event.button == 3:

                    response_correct = not original_on_left

                else:
                    continue

                trial += 1

                if response_correct:
                    correct += 1
                else:
                    incorrect += 1
                    flash_red_until = (
                        pygame.time.get_ticks()
                        + FLASH_DURATION
                    )

                pattern = create_pattern()
                distractor = create_distractor(pattern)

                original_on_left = random.choice(
                    [True, False]
                )

                state = SHOW_PATTERN
                state_start = time.perf_counter()

pygame.quit()