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
    def __init__(self, pos, walls, current_time, *groups):
        super().__init__(*groups)
        self.images = [load_image('player_run10.png'), load_image('player_run20.png')]
        self.image = self.images[0]  # пока что изображение игрока определяется этими двумя строками
        self.rect = self.image.get_rect(center=pos)
        self.vel = Vector2(100, 0)
        self.pos = Vector2(pos)
        self.walls = walls
        self.camera = Vector2(100, 0)
        self.current_frame = 0
        self.last_frame_time = 0
        self.frame_rate = 100
    def sprites(self):
        current_time = self.current_time
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_a] or keys[pygame.K_LEFT]) or (keys[pygame.K_w] or keys[pygame.K_UP]) or (keys[pygame.K_s] or keys[pygame.K_DOWN]) or (keys[pygame.K_d] or keys[pygame.K_RIGHT]):
            if current_time - self.last_frame_time >= self.frame_rate:
                self.current_frame = (self.current_frame + 1) % len(self.images)
                self.image = self.images[self.current_frame]
                self.last_frame_time = current_time

    def update(self):
        current_time = pygame.time.get_ticks()
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
        if self.vel.x != 0 or self.vel.y != 0:
            if current_time - self.last_frame_time >= self.frame_rate:
                self.current_frame = (self.current_frame + 1) % len(self.images)
                self.image = self.images[self.current_frame]
                self.last_frame_time = current_time

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
    for rect in ((0, 0, 30, 600), (31, 0, 600, 30), (570, 30, 30, 570), (0, 570, 600, 30),
                 (210, 30, 30, 60), (60, 60, 120, 30), (60, 120, 60, 30), (60, 120, 30, 90),
                 (150, 120, 180, 30), (270, 60, 150, 30), (360, 120, 60, 30), (510, 60, 30, 90),
                 (450, 120, 60, 30), (450, 120, 30, 210), (360, 180, 180, 30), (270, 240, 150, 30),
                 (241, 180, 210, 30), (210, 210, 30, 60), (30, 360, 450, 30), (210, 390, 30, 60),
                 (450, 420, 30, 90), (450, 420, 30, 90), (360, 480, 180, 30), (30, 480, 300, 30),):
        walls.add(Wall(*rect))
    all_sprites.add(walls)
    current_time = pygame.time.get_ticks()
    player = Player((320, 240), walls, current_time, all_sprites)
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
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
        #all_sprites.sprites()
        all_sprites.update()
        screen.fill((30, 30, 30))
        for sprite in all_sprites:
            # Add the player's camera offset to the coords of all sprites.
            screen.blit(sprite.image, sprite.rect.topleft + player.camera)
        pygame.display.flip()
        clock.tick(50)
if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()