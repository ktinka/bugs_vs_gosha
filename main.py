import pygame
from pygame.math import Vector2

import os
import sys


def load_image(name, colorkey=None):  # это для загрузки изображения
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image.convert_alpha()


class Player(pygame.sprite.Sprite):  # класс игрока

    def __init__(self, pos, walls, *groups):
        super().__init__(*groups)
        self.image = pygame.Surface((30, 50))  # пока что изображение игрока определяется этими двумя строками
        self.image.fill((235, 0, 220))  # заменить на красивые картинки
        self.rect = self.image.get_rect(center=pos)
        self.vel = Vector2(0, 0)
        self.pos = Vector2(pos)
        self.walls = walls
        self.camera = Vector2(0, 0)

    def update(self):
        # движение камеры ха игроком и столкновения
        self.camera -= self.vel

        self.pos.x += self.vel.x
        self.rect.centerx = self.pos.x

        self.pos.y += self.vel.y
        self.rect.centery = self.pos.y

        for wall in pygame.sprite.spritecollide(self, self.walls, False):
            if self.vel.x > 0:
                self.rect.right = wall.rect.left
            elif self.vel.x < 0:
                self.rect.left = wall.rect.right
            self.pos.x = self.rect.centerx
            self.camera.x += self.vel.x

        for wall in pygame.sprite.spritecollide(self, self.walls, False):
            if self.vel.y > 0:
                self.rect.bottom = wall.rect.top
            elif self.vel.y < 0:
                self.rect.top = wall.rect.bottom
            self.pos.y = self.rect.centery
            self.camera.y += self.vel.y


class Enemy(pygame.sprite.Sprite):
    pass


class Medicine(pygame.sprite.Sprite):
    pass


class Wall(pygame.sprite.Sprite):  # класс стен лабиринта

    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))  # потом можно будет и стены красивее отрисовать
        self.image.fill((240, 100, 0))
        self.rect = self.image.get_rect(topleft=(x, y))


def main():
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    all_sprites = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    for rect in ((100, 170, 90, 20), (200, 100, 20, 140),  # вот сюда нужно добавлять параметры стен лабиринта
                 (400, 60, 150, 100), (300, 470, 150, 100)):
        walls.add(Wall(*rect))
    all_sprites.add(walls)
    player = Player((320, 240), walls, all_sprites)

    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    player.vel.x = 5
                elif event.key == pygame.K_a:
                    player.vel.x = -5
                elif event.key == pygame.K_w:
                    player.vel.y = -5
                elif event.key == pygame.K_s:
                    player.vel.y = 5
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_d and player.vel.x > 0:
                    player.vel.x = 0
                elif event.key == pygame.K_a and player.vel.x < 0:
                    player.vel.x = 0
                elif event.key == pygame.K_w and player.vel.y < 0:
                    player.vel.y = 0
                elif event.key == pygame.K_s and player.vel.y > 0:
                    player.vel.y = 0

        all_sprites.update()

        screen.fill((30, 30, 30))
        for sprite in all_sprites:
            # Add the player's camera offset to the coords of all sprites.
            screen.blit(sprite.image, sprite.rect.topleft + player.camera)

        pygame.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
