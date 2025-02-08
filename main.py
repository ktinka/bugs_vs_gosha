import os
import sys
import sqlite3
import pygame
import math

FPS = 50
WIDTH = 640
HEIGHT = 480

WHITE = (255, 255, 255)
GREEN = (0, 100, 0)
ORANGE = (233, 109, 26)

killed_enemies = all_killed_enemies = 0
money = all_money = 0


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


def draw_bar(screen, x, y, value, bar_length, bar_height):
    if value < 0:
        value = 0
    fill = (value / 100) * bar_length
    outline_rect = pygame.Rect(x, y, bar_length, bar_height)
    fill_rect = pygame.Rect(x, y, fill, bar_height)
    pygame.draw.rect(screen, WHITE, fill_rect)
    pygame.draw.rect(screen, WHITE, outline_rect, 2)


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
    def __init__(self, pos, walls, enemies, coffee, clock, current_time, *groups):
        super().__init__(*groups)
        self.images_right = [load_image('player_run30.png'), load_image('player_run40.png')]
        self.images_left = [load_image('player_run30_left.png'), load_image('player_run40_left.png')]
        self.images_gun = [load_image('player_gun_right.png'), load_image('player_gun_left.png')]
        self.image = self.images_right[0]  # пока что изображение игрока определяется этими двумя строками
        self.rect = self.image.get_rect(center=pos)
        self.vel = pygame.math.Vector2(0, 0)
        self.pos = pygame.math.Vector2(pos)
        self.walls = walls
        self.camera = pygame.math.Vector2(0, 0)
        self.current_frame = 0
        self.last_frame_time = 0
        self.frame_rate = 250
        self.is_shooting = False
        self.health = 100
        self.clock = clock
        self.enemies = enemies
        self.current_time = current_time
        self.coffee = coffee

    def pos(self):
        return self.pos

    def sprites(self):
        self.current_time = 0
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) or (keys[pygame.K_w] or keys[pygame.K_UP]) or (
                keys[pygame.K_s] or keys[pygame.K_DOWN]) or (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            if self.current_time - self.last_frame_time >= self.frame_rate:
                self.current_frame = (self.current_frame + 1) % len(self.images_right)
                self.image = self.images_right[self.current_frame]
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
                    self.current_frame = (self.current_frame + 1) % len(self.images_right)
                    if (keys[pygame.K_w] or keys[pygame.K_UP]) or (keys[pygame.K_s] or keys[pygame.K_DOWN]) or (
                            keys[pygame.K_d] or keys[pygame.K_RIGHT]):
                        self.image = self.images_right[self.current_frame]
                    else:
                        self.image = self.images_left[self.current_frame]
                    self.last_frame_time = current_time
        '''
        # Анимация стрельбы (если is_shooting = True)
        if self.is_shooting:
            if self.image in self.images_right or self.image == self.images_gun[0]:
                self.image = self.images_gun[0]
            else:
                self.image = self.images_gun[1]
            self.is_shooting = False
        '''
        # Анимация стрельбы (если is_shooting = True)
        if self.is_shooting:
            pos = pygame.mouse.get_pos()
            if pos[0] >= self.pos[0]:
                self.image = self.images_gun[0]
            else:
                self.image = self.images_gun[1]
            self.is_shooting = False

        for coffee in pygame.sprite.spritecollide(self, self.coffee, False):
            self.health += 5
        for enemy in pygame.sprite.spritecollide(self, self.enemies, False):
            self.health -= 0.1
            if self.health <= 0:
                end_screen(won=False)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, walls, *groups):
        super().__init__(*groups)
        self.image = load_image("enemy.png")
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
        global killed_enemies
        for _ in pygame.sprite.spritecollide(self, bullets, False):
            if self.health > 0:
                self.health -= 1
            else:
                killed_enemies += 1
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
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = start_pos

        self.walls = walls
        self.start_x, self.start_y = map(float, start_pos)
        self.target_x, self.target_y = map(float, target_pos)

        self.total_distance = math.sqrt((self.target_x - self.start_x) ** 2 + (self.target_y - self.start_y) ** 2)
        self.speed = 5
        self.traveled_distance = 0  # Сколько пуля уже пролетела

    def update(self):
        # Параметрическое уравнение прямой:
        # x = start_x + t * (target_x - start_x)
        # y = start_y + t * (target_y - start_y)
        # где t изменяется от 0 до 1

        if self.traveled_distance < self.total_distance:
            # Вычисляем t, пропорциональное пройденному расстоянию
            t = self.traveled_distance / self.total_distance

            # Вычисляем новые координаты
            new_x = self.start_x + t * (self.target_x - self.start_x)
            new_y = self.start_y + t * (self.target_y - self.start_y)

            # Перемещаем пулю
            self.rect.center = (new_x, new_y)

            # Проверяем столкновения НА ОТРЕЗКЕ пути, а не только в конечной точке
            # (иначе пуля может "пролететь" сквозь тонкую стену)
            for wall in pygame.sprite.spritecollide(self, self.walls, False):
                self.kill()  # Уничтожаем пулю при столкновении
                return  # Важно! Выходим из update() после уничтожения
        else:
            # Пуля достигла цели или пролетела максимальное расстояние
            self.kill()  # Уничтожаем пулю

        # Увеличиваем пройденное расстояние
        self.traveled_distance += self.speed

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Medicine(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = load_image("coffee.png")
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.frame_rate = 100

    def collision_check(self, players, coffee):
        for _ in pygame.sprite.spritecollide(self, players, True):
            # self.kill()
            pygame.sprite.spritecollide(self, players, coffee, True)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = load_image("coin.png")
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Wall(pygame.sprite.Sprite):  # класс стен лабиринта
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))  # потом можно будет и стены красивее отрисовать
        self.image.fill((240, 100, 0))
        self.rect = self.image.get_rect(topleft=(x, y))


def start_screen(screen, clock):
    global killed_enemies
    global money
    fon = pygame.transform.scale(load_image('start_game_fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    money = killed_enemies = 0
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
    global killed_enemies, all_killed_enemies
    global money, all_money
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    if won:
        intro_text = ["Congratulations, you won!", "bugs killed:", str(killed_enemies),
                      "coins earned:", str(money)]
    else:
        intro_text = ["Unfortunately, you have lost!", "bugs killed:", str(killed_enemies),
                      "coins earned:", str(money)]
    all_killed_enemies += killed_enemies
    all_money += money
    killed_enemies = money = 0
    fon = pygame.transform.scale(load_image('gameover_fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 150
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 220
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


def rules_page(args):
    screen = args[0]
    clock = args[1]
    fon = pygame.transform.scale(load_image('rules_fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                profile_page()
        pygame.display.flip()
        clock.tick(FPS)


def light_mode(all_sprites, walls, enemies, coffee, coins, current_time):
    for rect in ((0, 0, 100, 1300), (100, 0, 1100, 100),
                 (1100, 100, 100, 1200), (500, 100, 100, 500),
                 (100, 300, 300, 100), (700, 400, 300, 100),
                 (100, 1200, 1000, 100), (200, 700, 100, 200), (700, 900, 100, 200)):
        walls.add(Wall(*rect))
    all_sprites.add(walls)

    for pos in ((180, 250), (244, 639), (257, 1172), (594, 1136), (1064, 355)):
        enemy = Enemy(pos, walls, all_sprites)
        enemies.add(enemy)
    all_sprites.add(enemies)

    for pos in ((230, 190), (200, 1000), (800, 240), (950, 1000), (500, 850)):
        cofee_class = Medicine(pos, all_sprites)
        coffee.add(cofee_class)
        all_sprites.add(coffee)

    for pos in ((700, 600), (300, 1000), (900, 1000), (1000, 700), (700, 300)):
        coin = Coin(pos, all_sprites)
        coins.add(coin)
        all_sprites.add(coins)


def hard_mode(all_sprites, walls, enemies, coffee, coins, current_time):
    for rect in ((0, 0, 100, 1300), (100, 0, 1100, 100),
                 (1100, 100, 100, 1200), (100, 1200, 1000, 100),
                 (300, 900, 300, 100), (500, 100, 200, 500),
                 (300, 600, 400, 100), (600, 700, 100, 300)):
        walls.add(Wall(*rect))
    all_sprites.add(walls)

    for pos in ((180, 250), (580, 792), (150, 150), (480, 592), (290, 1260),
                (663, 1160), (1100, 1100), (1000, 281), (663, 160), (700, 200),
                (1103, 1060), (1000, 1108), (900, 381), (463, 190), (450, 130),
                (900, 281), (960, 381), (890, 481)):
        enemy = Enemy(pos, walls, all_sprites)
        enemies.add(enemy)
    all_sprites.add(enemies)

    for pos in ((230, 200), (200, 1000), (880, 330), (1000, 1100), (500, 780)):
        cofee_class = Medicine(pos, all_sprites)
        coffee.add(cofee_class)
        all_sprites.add(coffee)

    for pos in ((230, 400), (1050, 1100), (880, 500), (200, 1100), (500, 1100)):
        coin = Coin(pos, all_sprites)
        coins.add(coin)
        all_sprites.add(coins)


def gameplay(args):
    global money
    screen = args[0]
    clock = args[1]
    mode = args[2]
    start_screen(screen, clock)
    all_sprites = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coffee = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    current_time = pygame.time.get_ticks()
    player = Player((320, 240), walls, enemies, coffee, clock, current_time, all_sprites)
    if mode == 0:
        light_mode(all_sprites, walls, enemies, coffee, coins, current_time)
    else:
        hard_mode(all_sprites, walls, enemies, coffee, coins, current_time)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                main()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                player.is_shooting = True
                target_pos = event.pos
                x = player.pos[0] - 320 + target_pos[0]
                y = player.pos[1] - 240 + target_pos[1]
                bullet = Bullet(walls, player.pos, (x, y))
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if event.key == pygame.K_e:
                    pos = pygame.mouse.get_pos()

                    player.is_shooting = True
                    target_pos = pygame.mouse.get_pos()
                    x = player.pos[0] - 320 + target_pos[0]
                    y = player.pos[1] - 240 + target_pos[1]
                    bullet = Bullet(walls, player.pos, (x, y))
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

        for sprite in coffee:
            pygame.sprite.spritecollide(player, coffee, True)

        for sprite in coins:
            coins_collected_list = pygame.sprite.spritecollide(player, coins, True)  # True - удалить монетку
            money += len(coins_collected_list)  # Увеличиваем счетчик на количество собранных в этот момент
            if pygame.sprite.spritecollide(player, coins, True):
                print(money)

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
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    info_text = [str(all_money), str(all_killed_enemies)]
    fon = pygame.transform.scale(load_image('profile_fon.jpeg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 138
    for line in info_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 48
        intro_rect.top = text_coord
        intro_rect.x = 120
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    btn3 = Button("Game Rules", 23, 381, 296, 51, rules_page, [screen, clock])
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    gameplay((screen, clock))

            btn3.handle_event(event)

        btn3.update()
        btn3.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)


def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    fon = pygame.transform.scale(load_image('main_fon.jpeg'), (WIDTH, HEIGHT))
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
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('Game.db')
    cursor = connection.cursor()

    # Создаем таблицу
    # ПЕРВАЯ ТАБЛИЦА (первый прямоугольник)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Maze1 (
            size_x0 INTEGER,
            size_y0 INTEGER,
            size_x INTEGER,
            size_y INTEGER
            )
            ''')

    cursor.execute('''
        INSERT INTO Maze1 (size_x0, size_y0, size_x, size_y) VALUES (0, 0, 100, 1300), (100, 0, 1100, 100),
        (1100, 100, 100, 1200), (500, 100, 100, 500), (100, 300, 300, 100), (700, 400, 300, 100),
        (100, 1200, 1000, 100), (200, 700, 100, 200), (700, 900, 100, 200)
        ''')

    # ВТОРАЯ ТАБЛИЦА (второй прямоугольник)
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS Maze2 (
                size_x0 INTEGER,
                size_y0 INTEGER,
                size_x INTEGER,
                size_y INTEGER
                )
                ''')

    cursor.execute('''
        INSERT INTO Maze2 (size_x0, size_y0, size_x, size_y) VALUES (0, 0, 100, 1300), (100, 0, 1100, 100),
        (1100, 100, 100, 1200), (100, 1200, 1000, 100), (300, 900, 300, 100), (500, 100, 200, 500),
        (300, 600, 400, 100), (600, 700, 100, 300)
        ''')

    # создаём массив с данными из таблицы Maze1
    cursor.execute("SELECT * FROM Maze1")
    Maze1 = cursor.fetchall()

    # создаём массив с данными из таблицы Maze2
    cursor.execute("SELECT * FROM Maze2")
    Maze2 = cursor.fetchall()

    connection.commit()
    connection.close()
    pygame.init()
    main()
    pygame.quit()
