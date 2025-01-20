import pygame
import os
import sys
from pygame.math import Vector2


class Player(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface([30, 50])
        self.image.fill((0, 0, 255))  # Синий
        self.rect = self.image.get_rect(center=pos)
        self.vel = Vector2(0, 0)
        self.pos = Vector2(pos)
        self.speed = 5
        self.camera = Vector2(0, 0)

    def update(self):
        keys = pygame.key.get_pressed()
        self.vel = Vector2(0, 0)

        if keys[pygame.K_LEFT]:
            self.vel.x = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vel.x = self.speed
        if keys[pygame.K_UP]:
            self.vel.y = -self.speed
        if keys[pygame.K_DOWN]:
            self.vel.y = self.speed

        self.pos += self.vel
        self.rect.center = self.pos

    def draw(self, screen):
        screen.blit(self.image, (self.pos.x - self.camera.x, self.pos.y - self.camera.y))


class Wall(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface([30, 30])
        self.image.fill((0, 0, 0))  # Черный
        self.rect = self.image.get_rect(topleft=pos)
        self.pos = Vector2(pos)

    def draw(self, screen, camera):
        screen.blit(self.image, (self.pos.x - camera.x, self.pos.y - camera.y))


class Maze:
    def __init__(self, cell_size, all_sprites, walls):
        self.cell_size = cell_size
        self.all_sprites = all_sprites
        self.walls = walls
        self.maze_data = [
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
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.generate_walls()

    def generate_walls(self):
        for row_idx, row in enumerate(self.maze_data):
            for col_idx, cell in enumerate(row):
                if cell == 0:
                    wall_pos = (col_idx * self.cell_size, row_idx * self.cell_size)
                    Wall(wall_pos, self.walls, self.all_sprites)


def main():
    pygame.init()
    # Размеры окна
    WIDTH = 800
    HEIGHT = 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Camera Example")
    all_sprites = pygame.sprite.Group()
    walls = pygame.sprite.Group()

    # Цвета
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Размер ячейки
    CELL_SIZE = 30

    # Создание лабиринта
    maze = Maze(CELL_SIZE, all_sprites, walls)

    # Создание игрока
    player = Player(Vector2(WIDTH // 2, HEIGHT // 2), all_sprites)
    all_sprites.add(player)
    # Мир
    world_offset = Vector2(0, 0)
    # Основной цикл игры
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.update()

        # Обновление позиции камеры
        player.camera.x = player.pos.x - WIDTH // 2
        player.camera.y = player.pos.y - HEIGHT // 2

        # Отрисовка
        screen.fill(WHITE)

        for wall in walls:
            wall.draw(screen, player.camera)  # Передаем player.camera

        for entity in all_sprites:
            entity.draw(screen, player.camera)

        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    main()
    pygame.quit()