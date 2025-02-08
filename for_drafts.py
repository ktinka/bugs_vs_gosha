import os
import sys

import pygame

FPS = 50
WIDTH = 640
HEIGHT = 480

WHITE = (255, 255, 255)
GREEN = (0, 100, 0)
ORANGE = (233, 109, 26)

killed_enemies = 0
used_medicine = 0


def load_image(name, colorkey=None):  # это для загрузки изображения
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image.convert_alpha()


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
    fon = pygame.transform.scale(load_image('fon2.jpg'), (WIDTH, HEIGHT))
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
                main()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def end_screen(won, mode=0):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    if won:
        intro_text = ["Игра окончена", "Поздравляем, вы выиграли!",
                      "Нажмите на клавишу N для новой игры"]
    else:
        intro_text = ["Игра окончена", "К сожалению, вы проиграли!",
                      "Нажмите на клавишу N для новой игры"]

    fon = pygame.transform.scale(load_image('fon2.jpg'), (WIDTH, HEIGHT))
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
                main()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    gameplay((screen, clock, mode))

        pygame.display.flip()
        clock.tick(FPS)


class Button():

    def __init__(self, text, x=0, y=0, width=296, height=51, command=None, args=None):

        self.text = text
        self.command = command
        self.args = args

        self.image_normal = pygame.Surface((width, height))
        self.image_normal.fill(ORANGE)

        self.image_hovered = pygame.Surface((width, height))
        self.image_hovered.fill(GREEN)

        self.image = self.image_normal
        self.rect = self.image.get_rect()

        font = pygame.font.SysFont('italic', 30)

        text_image = font.render(text, True, WHITE)
        text_rect = text_image.get_rect(center=self.rect.center)

        self.image_normal.blit(text_image, text_rect)
        self.image_hovered.blit(text_image, text_rect)

        self.rect.topleft = (x, y)

        self.hovered = False

    def update(self):

        if self.hovered:
            self.image = self.image_hovered
        else:
            self.image = self.image_normal

    def draw(self, surface):

        surface.blit(self.image, self.rect)

    def handle_event(self, event):

        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                self.command(self.args)


class Player(pygame.sprite.Sprite):  # класс игрока
    def __init__(self, pos, walls, enemies, clock, current_time, *groups):
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
        self.clock = clock
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
            """if self.vel.x > 0:
                self.rect.right = enemy.rect.left
            elif self.vel.x < 0:
                self.rect.left = enemy.rect.right
            self.pos.x = self.rect.centerx
            self.camera.x += self.vel.x"""
            self.health -= 0.1
            if self.health <= 0:
                end_screen(won=False)
        for enemy in pygame.sprite.spritecollide(self, self.enemies, False):
            """if self.vel.y > 0:
                self.rect.bottom = enemy.rect.top
            elif self.vel.y < 0:
                self.rect.top = enemy.rect.bottom
            self.pos.y = self.rect.centery
            self.camera.y += self.vel.y"""
            self.health -= 0.1
            if self.health <= 0:
                end_screen(won=False)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, walls, current_time, *groups):
        super().__init__(*groups)
        self.image = load_image("enemy3.png")
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.walls = walls
        self.current_frame = 0
        self.last_frame_time = 0
        self.frame_rate = 100
        self.health = 100
        self.speed = 0.5

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_time >= self.frame_rate:
            self.rect = self.rect.move(0, 1)
            for _ in pygame.sprite.spritecollide(self, self.walls, False):
                self.rect = self.rect.move(0, -1)
            self.last_frame_time = current_time

    def collision_check(self, bullets):
        for _ in pygame.sprite.spritecollide(self, bullets, False):
            if self.health > 0:
                self.health -= 1
            else:
                self.kill()

    def calculate_velocity(self, player_pos):
        direction = player_pos - self.pos
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.speed
        else:
            self.velocity = pygame.math.Vector2(0, 0)

    def follow_player(self, player_pos):
        self.pos += self.velocity
        self.rect.center = self.pos

        if (player_pos - self.pos).length() < self.speed:
            pass
        for _ in pygame.sprite.spritecollide(self, self.walls, False):
            pass

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, walls, start_pos, target_pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill((255, 0, 0), )
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.math.Vector2(start_pos)
        self.target = pygame.math.Vector2(target_pos)
        self.walls = walls
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
        for _ in pygame.sprite.spritecollide(self, self.walls, False):
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


def light_mode(all_sprites, walls, enemies, current_time):
    for rect in ((0, 0, 100, 1300), (100, 0, 1100, 100), (1100, 100, 100, 1200),
                 (500, 100, 100, 500), (100, 300, 300, 100), (700, 400, 300, 100),
                 (100, 1200, 1000, 100), (200, 700, 100, 200), (730, 880, 100, 200)):
        walls.add(Wall(*rect))
    all_sprites.add(walls)
    for pos in ((180, 250), (150, 110)):
        enemy = Enemy(pos, walls, current_time, all_sprites)
        enemies.add(enemy)
    all_sprites.add(enemies)


def hard_mode(all_sprites, walls, enemies, current_time):
    for rect in ((0, 0, 100, 1300), (100, 0, 1100, 100),
                     (1100, 100, 100, 1200), (100, 1200, 1000, 100),
                     (300, 900, 300, 100), (500, 100, 200, 500),
                     (300, 600, 400, 100), (600, 700, 100, 300)):
        walls.add(Wall(*rect))
    all_sprites.add(walls)
    """for pos in ((180, 250), (150, 110)):
        enemy = Enemy(pos, walls, current_time, all_sprites)
        enemies.add(enemy)
    all_sprites.add(enemies)"""

def draw_bar(screen, x, y, value, bar_length, bar_height):
    if value < 0:
        value = 0
    fill = (value / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(screen, WHITE, fill_rect)
    pygame.draw.rect(screen, WHITE, outline_rect, 2)

def gameplay(args):
    screen = args[0]
    clock = args[1]
    mode = args[2]
    start_screen(screen, clock)
    all_sprites = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    current_time = pygame.time.get_ticks()
    player = Player((320, 240), walls, enemies, clock, current_time, all_sprites)
    if mode == 0:
        light_mode(all_sprites, walls, enemies, current_time)
    else:
        hard_mode(all_sprites, walls, enemies, current_time)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                main()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Создание пули в координатах персонажа
                player_pos = player.pos
                target_pos = event.pos
                bullet = Bullet(walls, player_pos, target_pos)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if event.key == pygame.K_e:
                    player_pos = player.pos
                    target_pos = pygame.mouse.get_pos()
                    bullet = Bullet(walls, player_pos, target_pos)
                    all_sprites.add(bullet)
                    bullets.add(bullet)
                if (event.key == pygame.K_d or event.key == pygame.K_RIGHT) and not keys[pygame.K_w] and not keys[
                    pygame.K_UP] and not keys[pygame.K_s] and not keys[pygame.K_DOWN]:
                    player.vel.x = 5
                elif (event.key == pygame.K_a or event.key == pygame.K_LEFT) and not keys[pygame.K_w] and not keys[
                    pygame.K_UP] and not keys[pygame.K_s] and not keys[pygame.K_DOWN]:
                    player.vel.x = -5
                elif (event.key == pygame.K_w or event.key == pygame.K_UP) and not keys[pygame.K_a] and not keys[
                    pygame.K_LEFT] and not keys[pygame.K_d] and not keys[pygame.K_RIGHT]:
                    player.vel.y = -5
                elif (event.key == pygame.K_s or event.key == pygame.K_DOWN) and not keys[pygame.K_a] and not keys[
                    pygame.K_LEFT] and not keys[pygame.K_d] and not keys[pygame.K_RIGHT]:
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
        for sprite in enemies:
            sprite.collision_check(bullets)
            sprite.calculate_velocity(player.pos)
            sprite.follow_player(player.pos)

        if not enemies:
            if mode == 0:
                end_screen(won=True, mode=0)
            else:
                end_screen(won=True, mode=1)

        screen.fill((30, 40, 30))
        for sprite in all_sprites:
            screen.blit(sprite.image, sprite.rect.topleft + player.camera)
        draw_bar(screen, 64, 38, player.health, 100, 10)
        pygame.display.flip()
        clock.tick(100)


def profile_page(*args):
    pass


def rules_page(*args):
    pass


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    fon = pygame.transform.scale(load_image('start_screen_fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    btn1 = Button('Light mode', 172, 189, 296, 51, gameplay, (screen, clock, 0))
    btn2 = Button('Hard mode', 172, 274, 296, 51, gameplay, (screen, clock, 1))
    btn3 = Button("Profile", 172, 359, 296, 51, profile_page)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            btn1.handle_event(event)
            btn2.handle_event(event)
            btn3.handle_event(event)

        btn1.update()
        btn2.update()
        btn3.update()

        btn1.draw(screen)
        btn2.draw(screen)
        btn3.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()

