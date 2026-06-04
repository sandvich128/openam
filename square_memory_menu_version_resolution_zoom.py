
import pygame
import random
import time

pygame.init()

info = pygame.display.Info()
WIDTH = int(info.current_w * 0.85)
HEIGHT = int(info.current_h * 0.85)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pattern Memory Task")
clock = pygame.time.Clock()

BLUE_BG = (0, 0, 140)
CYAN = (30, 220, 220)
RED = (255, 20, 20)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

font = pygame.font.SysFont("arial", 28, bold=True)
big_font = pygame.font.SysFont("arial", 48, bold=True)

trial = 0
correct = 0
incorrect = 0
last_rt = None
flash_until = 0
flash_color = RED
FLASH_DURATION = 50

GRID_SIZE = 4

pattern_display_ms = 1000
blank_display_ms = 1000
answer_limit_ms = 3000

CELL_SIZE = 48
grid_scale = 1.0

MENU = "menu"
OPTIONS = "options"
SHOW_PATTERN = "show"
BLANK = "blank"
CHOICE = "choice"

state = MENU

option_cursor = 0
editing_value = False
typed_value = ""

experimental_angle = random.randint(-35, 35)
experimental_pos = (WIDTH // 2 + random.randint(-120, 120),
                    HEIGHT // 2 + random.randint(-80, 80))

def current_grid_size():
    return GRID_SIZE

def create_pattern():
    size = current_grid_size()
    return [[random.choice([0, 1]) for _ in range(size)] for _ in range(size)]

def create_distractor(pattern):
    size = len(pattern)
    new_pattern = [row[:] for row in pattern]
    flips = max(1, min(3, size))
    for _ in range(flips):
        r = random.randint(0, size - 1)
        c = random.randint(0, size - 1)
        new_pattern[r][c] = 1 - new_pattern[r][c]
    return new_pattern

def get_cell_size():
    global grid_scale
    size = current_grid_size()
    return max(4, int(max(8, min(48, 500 // size)) * grid_scale))


def clamp_grid_scale():
    global grid_scale
    size = current_grid_size()
    base = max(8, min(48, 500 // size))
    max_total_width = int(WIDTH * 0.42)
    max_scale = max_total_width / max(1, size * base)
    grid_scale = max(0.25, min(grid_scale, max_scale))

def draw_pattern(pattern, center_x, center_y):
    cell = get_cell_size()
    size = len(pattern)
    total = size * cell
    start_x = center_x - total // 2
    start_y = center_y - total // 2

    for r in range(size):
        for c in range(size):
            color = CYAN if pattern[r][c] else RED
            rect = pygame.Rect(start_x + c * cell, start_y + r * cell, cell, cell)
            pygame.draw.rect(screen, color, rect)
            if cell > 4:
                pygame.draw.rect(screen, BLUE_BG, rect, 1)

def draw_status():
    acc = 0 if trial == 0 else round(correct / trial * 100, 1)
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
        screen.blit(surf, surf.get_rect(center=(section*i + section/2, HEIGHT-40)))

def start_new_round():
    global pattern, distractor, original_on_left, state_start, choice_start, state
    pattern = create_pattern()
    distractor = create_distractor(pattern)
    original_on_left = random.choice([True, False])
    state = SHOW_PATTERN
    state_start = time.perf_counter()
    choice_start = None

pattern = create_pattern()
distractor = create_distractor(pattern)
original_on_left = True
state_start = time.perf_counter()
choice_start = None

running = True
while running:
    clock.tick(60)

    if pygame.time.get_ticks() < flash_until:
        screen.fill(flash_color)
    else:
        screen.fill(BLUE_BG)

    now = time.perf_counter()

    if state == MENU:
        title = big_font.render("Pattern Memory Task", True, WHITE)
        start = font.render("LEFT CLICK = Start", True, WHITE)
        opts = font.render("RIGHT CLICK = Options", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 220)))
        screen.blit(start, start.get_rect(center=(WIDTH//2, 340)))
        screen.blit(opts, opts.get_rect(center=(WIDTH//2, 400)))

    elif state == OPTIONS:
        items = [
            f"Grid Size: {GRID_SIZE}",
            f"Pattern Display (ms): {pattern_display_ms}",
            f"Blank Screen (ms): {blank_display_ms}",
            f"Answer Limit (ms): {answer_limit_ms}"
        ]

        hdr = big_font.render("OPTIONS", True, WHITE)
        screen.blit(hdr, hdr.get_rect(center=(WIDTH//2, 120)))

        for i, txt in enumerate(items):
            prefix = "> " if i == option_cursor else "  "
            surf = font.render(prefix + txt, True, WHITE)
            screen.blit(surf, (180, 220 + i * 60))

        help_txt = font.render("Arrows=Navigate  Mouse Wheel=Adjust  Ctrl +/- = Zoom Grids  Esc=Back", True, WHITE)
        screen.blit(help_txt, (180, 520))

        if editing_value:
            edit = font.render("Value: " + typed_value, True, YELLOW)
            screen.blit(edit, (180, 580))

        if GRID_SIZE > 10:
            intensity = min(1.0, (GRID_SIZE - 10) / 90.0)
            experimental_angle = (pygame.time.get_ticks() * (0.05 + intensity * 0.8)) % 360
            cx = WIDTH//2 + int((50 + intensity * 250) * __import__("math").sin(pygame.time.get_ticks()/max(40, 300-intensity*250)))
            cy = HEIGHT//2 + int((30 + intensity * 180) * __import__("math").cos(pygame.time.get_ticks()/max(50, 350-intensity*280)))
            stamp = font.render("Experimental", True, YELLOW)
            stamp = pygame.transform.rotate(stamp, experimental_angle)
            screen.blit(stamp, stamp.get_rect(center=(cx, cy)))

    elif state == SHOW_PATTERN:
        draw_pattern(pattern, WIDTH//2, HEIGHT//2 - 50)
        if (now - state_start) * 1000 >= pattern_display_ms:
            state = BLANK
            state_start = now

    elif state == BLANK:
        if (now - state_start) * 1000 >= blank_display_ms:
            state = CHOICE
            choice_start = now

    elif state == CHOICE:
        clamp_grid_scale()
        if original_on_left:
            draw_pattern(pattern, WIDTH//3, HEIGHT//2 - 50)
            draw_pattern(distractor, WIDTH*2//3, HEIGHT//2 - 50)
        else:
            draw_pattern(distractor, WIDTH//3, HEIGHT//2 - 50)
            draw_pattern(pattern, WIDTH*2//3, HEIGHT//2 - 50)

        if answer_limit_ms > 0 and (now - choice_start) * 1000 >= answer_limit_ms:
            trial += 1
            incorrect += 1
            flash_color = (0, 255, 0)
            flash_until = pygame.time.get_ticks() + FLASH_DURATION
            flash_color = RED
            flash_until = pygame.time.get_ticks() + FLASH_DURATION
            start_new_round()

        draw_status()

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN:
            mods = pygame.key.get_mods()
            if mods & pygame.KMOD_CTRL:
                if event.key in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS):
                    grid_scale *= 1.1
                    clamp_grid_scale()
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    grid_scale /= 1.1
                    clamp_grid_scale()

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            state = MENU

        if state == MENU and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                start_new_round()
            elif event.button == 3:
                state = OPTIONS

        elif state == OPTIONS and event.type == pygame.MOUSEWHEEL:
            delta = event.y
            if option_cursor == 0:
                GRID_SIZE = max(2, min(100, GRID_SIZE + delta))
            elif option_cursor == 1:
                pattern_display_ms = max(0, min(1000, pattern_display_ms + delta * 50))
            elif option_cursor == 2:
                blank_display_ms = max(0, min(1000, blank_display_ms + delta * 50))
            elif option_cursor == 3:
                answer_limit_ms = max(0, min(1000, answer_limit_ms + delta * 50))

        elif state == OPTIONS and event.type == pygame.KEYDOWN:
            if editing_value:
                if event.key == pygame.K_RETURN:
                    if typed_value.isdigit():
                        v = int(typed_value)
                        if option_cursor == 0:
                            GRID_SIZE = max(2, min(100, v))
                        else:
                            v = max(0, min(1000, v))
                            if option_cursor == 1:
                                pattern_display_ms = v
                            elif option_cursor == 2:
                                blank_display_ms = v
                            elif option_cursor == 3:
                                answer_limit_ms = v
                    editing_value = False
                    typed_value = ""
                elif event.key == pygame.K_BACKSPACE:
                    typed_value = typed_value[:-1]
                elif event.unicode.isdigit():
                    typed_value += event.unicode
            else:
                if event.key == pygame.K_ESCAPE:
                    state = MENU
                elif event.key == pygame.K_UP:
                    option_cursor = (option_cursor - 1) % 4
                elif event.key == pygame.K_DOWN:
                    option_cursor = (option_cursor + 1) % 4
                elif event.key == pygame.K_RETURN:
                    editing_value = True
                    typed_value = ""

        elif state == CHOICE and event.type == pygame.MOUSEBUTTONDOWN:
            rt = (time.perf_counter() - choice_start) * 1000
            last_rt = rt

            if event.button == 1:
                response_correct = original_on_left
            elif event.button == 3:
                response_correct = not original_on_left
            else:
                continue

            trial += 1
            if response_correct:
                correct += 1
                flash_color = (0, 255, 0)
                flash_until = pygame.time.get_ticks() + FLASH_DURATION
            else:
                incorrect += 1
                flash_color = (0, 255, 0)
                flash_until = pygame.time.get_ticks() + FLASH_DURATION
                flash_color = RED
            flash_until = pygame.time.get_ticks() + FLASH_DURATION

            start_new_round()

pygame.quit()
