import os
import sys

import pygame

killed_enemies = 0
used_medicine = 0


def handle_button_click(buttons, pos):
    for button in buttons:
        if button.is_clicked(pos):
            return button.button_id
    return None


def middle_screen():
    font = pygame.font.Font(None, 30)
    screen = pygame.display.set_mode((640, 480))
    button1 = Button(50, 150, 200, 50, "УРОВЕНЬ 1", 1)
    button2 = Button(350, 150, 200, 50, "УРОВЕНЬ 2", 2)
    buttons = [button1, button2]
    screen.fill((255, 255, 255))
    button1.draw(screen)
    button2.draw(screen)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()

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
                  "Управление: WASD - хождение, нажатие мышкой - стрельба"]

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
                return  1
        pygame.display.flip()
        clock.tick(FPS)


def end_screen(won):
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    if won:
        intro_text = ["Игра окончена", "Поздравляем, вы выиграли!",
                      "Нажмите на любую клавишу для новой игры"]
    else:
        intro_text = ["Игра окончена", "К сожалению, вы проиграли!",
                      "Нажмите на любую клавишу для новой игры"]

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
                main()

        pygame.display.flip()
        clock.tick(FPS)

class Button:
    def __init__(self, x, y, width, height, text, button_id):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.button_id = button_id  # Уникальный идентификатор кнопки
        self.color = (100, 100, 100)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        font = pygame.font.Font(None, 30)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Player(pygame.sprite.Sprite):  # класс игрока
    def __init__(self, pos, walls, enemies, coffee,clock, current_time, *groups):
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

        # Анимация стрельбы (если is_shooting = True)
        if self.is_shooting:
            if self.image in self.images_right or self.image == self.images_gun[0]:
                self.image = self.images_gun[0]
            else:
                self.image = self.images_gun[1]
            self.is_shooting = False

        for coffee in pygame.sprite.spritecollide(self, self.coffee, False):
            self.health += 5
            Player.show(self)
        for enemy in pygame.sprite.spritecollide(self, self.enemies, False):
            self.health -= 1
            if self.health == 0:
                end_screen(won=False)
            Player.show(self)
    def show(self):
        pass
        #print(self.health)


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
            #self.kill()
            pygame.sprite.spritecollide(self, players, coffee, True)

    def draw(self, screen):
        screen.blit(self.image, self.rect)


class Wall(pygame.sprite.Sprite):  # класс стен лабиринта
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))  # потом можно будет и стены красивее отрисовать
        self.image.fill((240, 100, 0))
        self.rect = self.image.get_rect(topleft=(x, y))


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos, *groups):
        super().__init__(*groups)
        self.image = load_image("coin.png")
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.Vector2(pos)
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.quantity_coins = 0

    def collision_check(self, players, coffee):
        if pygame.sprite.spritecollide(self, players, coins, True):
            self.quantity_coins += 1

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def number(self):
        return self.quantity_coins


def main():
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    start_screen(screen, clock)
    middle_screen()
    all_sprites = pygame.sprite.Group()
    players = pygame.sprite.Group()
    walls = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coffee = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    button1 = Button(50, 150, 200, 50, "Button 1", 1)
    button2 = Button(350, 150, 200, 50, "Button 2", 2)
    buttons = [button1, button2]
    pos = pygame.mouse.get_pos()
    current_time = pygame.time.get_ticks()
    if handle_button_click(buttons, pos) == 1:
        for rect in ((0, 0, 100, 1300), (100, 0, 1100, 100),
                     (1100, 100, 100, 1200), (500, 100, 100, 500),
                     (100, 300, 300, 100), (700, 400, 300, 100),
                     (100, 1200, 1000, 100), (200, 700, 100, 200), (700, 900, 100, 200)):
            walls.add(Wall(*rect))

        for pos in ((180, 250), (244, 639), (257, 1172), (594, 1136), (1064, 355)):
            enemy = Enemy(pos, walls, current_time, all_sprites)
            enemies.add(enemy)
        all_sprites.add(enemies)
        all_sprites.add(walls)

        for pos in ((230, 190), (200, 1000), (800, 240), (950, 1000), (500,850)):
            cofee_class = Medicine(pos, all_sprites)
            coffee.add(cofee_class)
            all_sprites.add(coffee)

        for pos in ((230, 190), (200, 1000), (800, 240), (950, 1000), (500,850)):
            coin = Coin(pos, all_sprites)
            coins.add(coin)
            all_sprites.add(coins)

    elif handle_button_click(buttons, pos) == 2:
        for rect in ((0, 0, 100, 1300), (100, 0, 1100, 100),
                     (1100, 100, 100, 1200), (100, 1200, 1000, 100),
                     (300, 900, 300, 100), (500, 100, 200, 500),
                     (300, 600, 400, 100), (600, 700, 100, 300)):
            walls.add(Wall(*rect))
        for pos in ((180, 250), (580, 792), (150, 150), (480, 592), (290, 1260),
                    (663, 1160), (1100, 1100), (1000, 281), (663, 160), (700, 200),
                    (1103, 1060), (1000, 1108), (900, 381), (463, 190), (450, 130),
                    (900, 281), (960, 381), (890, 481)):
            enemy = Enemy(pos, walls, current_time, all_sprites)
            enemies.add(enemy)
        all_sprites.add(enemies)
        all_sprites.add(walls)

        for pos in ((230, 200), (200, 1000), (880, 330), (1000, 1100), (500, 780)):
            cofee_class = Medicine(pos, all_sprites)
            coffee.add(cofee_class)
            all_sprites.add(coffee)

        for pos in ((200, 100), (100, 900), (700, 340), (900, 1000), (567,650)):
            coin = Coin(pos, all_sprites)
            coins.add(coin)
            all_sprites.add(coins)


    player = Player((320, 240), walls, enemies, coffee, clock, current_time, all_sprites)
    players.add(player)
    all_sprites.add(players)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                print(pos)
                player.is_shooting = True
                target_pos = event.pos
                bullet = Bullet(walls, player.pos, target_pos)
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

        for sprite in coffee:
            pygame.sprite.spritecollide(player, coffee, True)

        coins_collected = 0
        for sprite in coins:
            #if pygame.sprite.spritecollide(player, coins, True):
            coins_collected_list = pygame.sprite.spritecollide(player, coins,True)  # True - удалить монетку
            coins_collected += len(coins_collected_list)  # Увеличиваем счетчик на количество собранных в этот момент
            if pygame.sprite.spritecollide(player, coins, True):
                print(coins_collected)


        if not enemies:
            end_screen(won=True)

        screen.fill((30, 30, 30))
        for sprite in all_sprites:
            screen.blit(sprite.image, sprite.rect.topleft + player.camera)
        pygame.display.flip()
        clock.tick(100)

if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()