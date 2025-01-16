import pygame

# Инициализация Pygame
pygame.init()

# Размеры окна
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Sprite Game")

# Цвета
WHITE = (255, 255, 255)

# Загрузка спрайтов игрока (замените на свои пути к изображениям)
player_sprites = [
    pygame.image.load("player_run10.png").convert_alpha(),
    pygame.image.load("player_run20.png").convert_alpha()]

player_sprites_left = [
    pygame.image.load("player_run10_left.png").convert_alpha(),
    pygame.image.load("player_run20_left.png").convert_alpha()]

# Размер спрайта
SPRITE_SIZE = player_sprites[0].get_rect().size

# Позиция игрока
# player_x = WIDTH // 2 - SPRITE_SIZE[0] // 2
# player_y = HEIGHT // 2 - SPRITE_SIZE[1] // 2
player_x, player_y = 370, 270


player_speed = 5
print(player_x, player_y)

# Индекс текущего спрайта
current_sprite_index = 0
last_sprite_change_time = 0

# Лабиринт (0 - стена, 1 - проход)
maze = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0],
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
    [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]

# Размер ячейки
CELL_SIZE = 30

# Основной цикл игры
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        new_x = player_x - player_speed
        if maze[player_y // CELL_SIZE][new_x // CELL_SIZE] == 1:
            player_x = new_x
    if keys[pygame.K_RIGHT]:
        new_x = player_x + player_speed
        if maze[player_y // CELL_SIZE][(new_x + CELL_SIZE - 1) // CELL_SIZE] == 1:
            player_x = new_x
    if keys[pygame.K_UP]:
        new_y = player_y - player_speed
        if maze[new_y // CELL_SIZE][player_x // CELL_SIZE] == 1:
           player_y = new_y
    if keys[pygame.K_DOWN]:
        new_y = player_y + player_speed
        if maze[(new_y + CELL_SIZE - 1) // CELL_SIZE][player_x // CELL_SIZE] == 1:
            player_y = new_y


    # Меняем спрайт каждую секунду
    current_time = pygame.time.get_ticks()
    if current_time - last_sprite_change_time >= 300: # 1000 миллисекунд = 1 секунда
        current_sprite_index = (current_sprite_index + 1) % len(player_sprites)
        last_sprite_change_time = current_time

    # бег
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
        current_time = pygame.time.get_ticks()
        if current_time - last_sprite_change_time >= 100:  # 1000 миллисекунд = 1 секунда
            current_sprite_index = (current_sprite_index + 1) % len(player_sprites)
            last_sprite_change_time = current_time
    else:
        player = pygame.image.load("player_run10.png").convert_alpha()


    # Отрисовка лабиринта
    screen.fill(WHITE)
    for row_idx, row in enumerate(maze):
        for col_idx, cell in enumerate(row):
            if cell == 0:
                pygame.draw.rect(screen, (0, 0, 0), (col_idx * CELL_SIZE, row_idx * CELL_SIZE, CELL_SIZE, CELL_SIZE))


    # Отрисовка игрока
    if keys[pygame.K_RIGHT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
        screen.blit(player_sprites[current_sprite_index], (player_x, player_y))
    elif keys[pygame.K_LEFT]:
        screen.blit(player_sprites_left[current_sprite_index], (player_x, player_y))
    else:
        screen.blit(player, (player_x, player_y))


    pygame.display.flip()
    clock.tick(60)

pygame.quit()