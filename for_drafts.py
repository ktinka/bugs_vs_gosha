import os
import sys

import pygame


def load_image(name, colorkey=None):  # это для загрузки изображения
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image.convert_alpha()


FPS = 50


def terminate():
    pygame.quit()
    sys.exit()


def start_screen(screen, clock):
    intro_text = ["Гоша против Багов", "",
                  "Правила игры",
                  "Вы играете за программиста Гошу,",
                  "Ваша задача - собрать достаточное",
                  "количество монет, отстреливаясь от жуков.",
                  "Управление: WASD - хождение, E - стрельба"]

    fon = pygame.transform.scale(load_image('fon2.jpg'), (700, 500))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


class Player(pygame.sprite.Sprite):  # класс игрока
    def __init__(self, pos, walls, enemies, current_time, *groups):
        super().__init__(*groups)
        self.images = [load_image('player_run30.png'), load_image('player_run40.png')]
        self.image = self.images[0]  # пока что изображение игрока определяется этими двумя строками
        self.rect = self.image.get_rect(center=pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.pos = pygame.math.Vector2(pos)
        self.walls = walls
        self.camera = pygame.math.Vector2(0, 0)
        self.current_frame = 0
        self.last_frame_time = 0
        self.frame_rate = 250

        self.health = 100
        self.enemies = enemies
        self.current_time = current_time

    def pos(self):
        return self.pos

    def sprites(self):
        self.current_time = 0
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) or (keys[pygame.K_w] or keys[pygame.K_UP]) or (
                keys[pygame.K_s] or keys[pygame.K_DOWN]) or (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            if self.current_time - self.last_frame_time >= self.frame_rate:
                self.current_frame = (self.current_frame + 1) % len(self.images)
                self.image = self.images[self.current_frame]
                self.last_frame_time = self.current_time

    def update(self):
        current_time = pygame.time.get_ticks()
        # движение камеры за игроком и столкновения
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
        if self.vel.x != 0 or self.vel.y != 0:
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) or (keys[pygame.K_w] or keys[pygame.K_UP]) or (
                    keys[pygame.K_s] or keys[pygame.K_DOWN]) or (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
                if current_time - self.last_frame_time >= self.frame_rate:
                    self.current_frame = (self.current_frame + 1) % len(self.images)
                    self.image = self.images[self.current_frame]
                    self.last_frame_time = current_time

        for enemy in pygame.sprite.spritecollide(self, self.enemies, False):
            if self.vel.x > 0:
                self.rect.right = enemy.rect.left
            elif self.vel.x < 0:
                self.rect.left = enemy.rect.right
            self.pos.x = self.rect.centerx
            self.camera.x += self.vel.x
            self.health -= 1
            if self.health == 0:
                print("конец игры")
        for enemy in pygame.sprite.spritecollide(self, self.enemies, False):
            if self.vel.y > 0:
                self.rect.bottom = enemy.rect.top
            elif self.vel.y < 0:
                self.rect.top = enemy.rect.bottom
            self.pos.y = self.rect.centery
            self.camera.y += self.vel.y
            self.health -= 1
            if self.health == 0:
                print("конец игры")


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, walls, current_time, *groups):
        super().__init__(*groups)
        self.image = load_image("enemy3.png")
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=pos)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.walls = walls
        self.current_frame = 0
        self.last_frame_time = 0
        self.frame_rate = 100

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_time >= self.frame_rate:
            self.rect = self.rect.move(0, 1)
            for wall in pygame.sprite.spritecollide(self, self.walls, False):
                self.rect = self.rect.move(0, -1)
            self.last_frame_time = current_time


class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0), )
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.math.Vector2(start_pos)
        self.target = pygame.math.Vector2(target_pos)
        self.speed = 10
        self.calculate_velocity()

    def calculate_velocity(self):
        direction = self.target - self.pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed
        else:
            self.velocity = pygame.math.Vector2(0, 0)

    def update(self):
        self.pos += self.velocity
        self.rect.center = self.pos

        if (self.target - self.pos).length() < self.speed:
            self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.rect)


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
    start_screen(screen, clock)
    all_sprites = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    for rect in ((0, 100, 100, 1000), (200, 0, 1100, 100),
                 (1100, 200, 100, 1200), (500, 100, 100, 500),
                 (100, 300, 300, 100), (700, 400, 300, 100),
                 (200, 1200, 900, 100), (200, 700, 100, 200)):
        walls.add(Wall(*rect))
    all_sprites.add(walls)
    current_time = pygame.time.get_ticks()
    enemy = Enemy((180, 250), walls, current_time, all_sprites)
    enemies.add(enemy)
    all_sprites.add(enemies)
    player = Player((320, 240), walls, enemies, current_time, all_sprites)
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Создание пули в координатах персонажа
                player_pos = player.pos
                target_pos = event.pos
                bullet = Bullet(player.rect.center, target_pos)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    player.vel.x = 5
                elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    player.vel.x = -5
                elif event.key == pygame.K_w or event.key == pygame.K_UP:
                    player.vel.y = -5
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    player.vel.y = 5
            elif event.type == pygame.KEYUP:
                if (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and player.vel.x > 0:
                    player.vel.x = 0
                elif (event.key == pygame.K_a or event.key == pygame.K_LEFT) and player.vel.x < 0:
                    player.vel.x = 0
                elif (event.key == pygame.K_w or event.key == pygame.K_UP) and player.vel.y < 0:
                    player.vel.y = 0
                elif (event.key == pygame.K_s or event.key == pygame.K_DOWN) and player.vel.y > 0:
                    player.vel.y = 0
        all_sprites.update()
        screen.fill((30, 30, 30))
        for sprite in all_sprites:
            screen.blit(sprite.image, sprite.rect.topleft + player.camera)
        pygame.display.flip()
        clock.tick(100)


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
