import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH = 480
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DSG Racing")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Fonts
font = pygame.font.SysFont("Arial", 36, bold=True)
big_font = pygame.font.SysFont("Arial", 72, bold=True)

# Colors
SKY = (135, 206, 235)
GRASS = (34, 177, 76)
ROAD = (50, 50, 50)
WHITE = (255, 255, 255)
YELLOW = (255, 220, 0)
BLUE = (0, 120, 255)
RED = (220, 20, 60)
BLACK = (0, 0, 0)
PURPLE = (180, 0, 255)
ORANGE = (255, 140, 0)

# Road dimensions
ROAD_LEFT = 60
ROAD_RIGHT = WIDTH - 60
ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT

# Three lane centers
LANES = [120, 240, 360]

# Player
player_lane = 1
player_x = LANES[player_lane]
player_y = HEIGHT - 120

# Enemy settings
enemy_speed = 8
enemies = []
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 900)

# Score
score = 0
best_score = 0

# Road animation
road_offset = 0

# Touch debounce (prevents moving too fast)
last_move_time = 0
MOVE_COOLDOWN = 180  # milliseconds


def draw_car(x, y, color):
    # Body
    pygame.draw.rect(screen, color, (x - 30, y - 50, 60, 100), border_radius=12)

    # Windshield
    pygame.draw.rect(screen, (220, 240, 255), (x - 18, y - 25, 36, 28), border_radius=8)

    # Wheels
    for wx in [x - 35, x + 25]:
        pygame.draw.rect(screen, BLACK, (wx, y - 35, 10, 22), border_radius=3)
        pygame.draw.rect(screen, BLACK, (wx, y + 12, 10, 22), border_radius=3)

    # Lights
    pygame.draw.circle(screen, YELLOW, (x - 15, y - 45), 4)
    pygame.draw.circle(screen, YELLOW, (x + 15, y - 45), 4)
    pygame.draw.circle(screen, RED, (x - 15, y + 45), 4)
    pygame.draw.circle(screen, RED, (x + 15, y + 45), 4)



def draw_background():
    global road_offset

    # Sky/grass
    screen.fill(SKY)
    pygame.draw.rect(screen, GRASS, (0, 0, ROAD_LEFT, HEIGHT))
    pygame.draw.rect(screen, GRASS, (ROAD_RIGHT, 0, ROAD_LEFT, HEIGHT))

    # Road
    pygame.draw.rect(screen, ROAD, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))

    # Borders
    pygame.draw.line(screen, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 4)
    pygame.draw.line(screen, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 4)

    # Lane markers
    road_offset = (road_offset + enemy_speed) % 80
    for x in [180, 300]:
        for y in range(-80, HEIGHT, 80):
            pygame.draw.rect(screen, WHITE, (x - 3, y + road_offset, 6, 40))



def spawn_enemy():
    lane = random.choice(LANES)
    color = random.choice([RED, PURPLE, ORANGE])
    enemies.append({"x": lane, "y": -120, "color": color})



def move_enemies():
    global score, enemy_speed

    for enemy in enemies[:]:
        enemy["y"] += enemy_speed

        if enemy["y"] > HEIGHT + 120:
            enemies.remove(enemy)
            score += 1

            # Increase difficulty every 10 points
            if score % 10 == 0:
                enemy_speed += 0.5



def draw_enemies():
    for enemy in enemies:
        draw_car(enemy["x"], enemy["y"], enemy["color"])



def check_collision():
    player_rect = pygame.Rect(player_x - 30, player_y - 50, 60, 100)

    for enemy in enemies:
        enemy_rect = pygame.Rect(enemy["x"] - 30, enemy["y"] - 50, 60, 100)
        if player_rect.colliderect(enemy_rect):
            return True

    return False



def draw_score():
    score_text = font.render(f"Score: {score}", True, WHITE)
    best_text = font.render(f"Best: {best_score}", True, WHITE)
    screen.blit(score_text, (15, 15))
    screen.blit(best_text, (15, 55))



def game_over_screen():
    while True:
        screen.fill((20, 20, 20))

        title = big_font.render("CRASH!", True, RED)
        score_text = font.render(f"Score: {score}", True, WHITE)
        msg = font.render("Tap to Restart", True, WHITE)

        screen.blit(title, title.get_rect(center=(WIDTH // 2, 250)))
        screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 380)))
        screen.blit(msg, msg.get_rect(center=(WIDTH // 2, 500)))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN):
                return



def reset_game():
    global player_lane, player_x, score, enemy_speed, enemies

    player_lane = 1
    player_x = LANES[player_lane]
    score = 0
    enemy_speed = 8
    enemies = []


# Main loop
while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == SPAWN_EVENT:
            spawn_enemy()

    # Touch controls
    current_time = pygame.time.get_ticks()

    if pygame.mouse.get_pressed()[0]:
        if current_time - last_move_time > MOVE_COOLDOWN:
            mx, my = pygame.mouse.get_pos()

            if mx < WIDTH // 2 and player_lane > 0:
                player_lane -= 1
                last_move_time = current_time

            elif mx >= WIDTH // 2 and player_lane < 2:
                player_lane += 1
                last_move_time = current_time

    # Update player x based on lane
    player_x = LANES[player_lane]

    # Update game
    move_enemies()

    # Draw
    draw_background()
    draw_enemies()
    draw_car(player_x, player_y, BLUE)
    draw_score()

    # Touch control hints
    left_hint = font.render("◀", True, WHITE)
    right_hint = font.render("▶", True, WHITE)
    screen.blit(left_hint, (40, HEIGHT - 60))
    screen.blit(right_hint, (WIDTH - 70, HEIGHT - 60))

    pygame.display.flip()

    # Collision
    if check_collision():
        if score > best_score:
            best_score = score
        game_over_screen()
        reset_game()