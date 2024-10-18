import pygame
import os
import random
import math

pygame.init()

WIDTH = 1280
HEIGHT = 720
WORLD_WIDTH = 2560
WORLD_HEIGHT = 1440

GREEN = (34, 139, 34)
BLACK = (0, 0, 0)

# 디스플레이 크기 지정
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("뱀파이버 서바이벌")


# 이미지 로드 함수
def load_images(path):
    images = []
    for i in range(4):  # 0.png에서 3.png까지
        img = pygame.image.load(os.path.join(path, f"{i}.png")).convert_alpha()
        images.append(img)
    return images


player_images = {
    "up": load_images(os.path.join("images", "player", "up")),
    "down": load_images(os.path.join("images", "player", "down")),
    "left": load_images(os.path.join("images", "player", "left")),
    "right": load_images(os.path.join("images", "player", "right")),
}


obstacle_images = [
    pygame.image.load("data/graphics/objects/grassrock1.png").convert_alpha(),
    pygame.image.load("data/graphics/objects/green_tree_small.png").convert_alpha(),
]

enemy_images = {
    "bat": load_images(os.path.join("images", "enemies", "bat")),
    "blob": load_images(os.path.join("images", "enemies", "blob")),
    "skeleton": load_images(os.path.join("images", "enemies", "skeleton")),
}


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):  # 플레이어 위치 좌표로 초기화
        super().__init__()

        self.image = player_images["down"][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.direction = pygame.Vector2()
        self.state = "down"

        self.animation_index = 0
        self.animation_time = 0

        self.shoot_timer = 0
        self.shoot_delay = 1000  # 1초

    def update(self, dt):
        if self.direction.length():
            self.animation_time += dt

            if self.animation_time > 0.2:
                self.animation_time = 0
                self.animation_index += 1
                self.animation_index = self.animation_index % 4
                self.image = player_images[self.state][self.animation_index]
        else:
            self.animation_index = 0
            self.image = player_images[self.state][self.animation_index]

    def move(self, dx, dy):
        if dx > 0:
            self.state = "right"
        elif dx < 0:
            self.state = "left"
        elif dy > 0:
            self.state = "down"
        elif dy < 0:
            self.state = "up"
        self.direction.x = dx
        self.direction.y = dy

        # 대각선 속도 보정
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed

    def shoot(self):
        bullets = []

        for angle in range(0, 360, 45):
            state = (math.cos(math.radians(angle)), math.sin(math.radians(angle)))
            bullet = Bullet(self.rect.centerx, self.rect.centery, state)
            bullets.append(bullet)
        return bullets


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = random.choice(obstacle_images)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class Camera:
    def __init__(self):
        self.camera = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)

    def apply(self, entity):
        return entity.rect.move(
            self.camera.topleft
        )  # 카메라의 topleft 기준으로 entity를 전부 move

    # update 함수로 좌표 계산 후 apply 함수로 적용
    def update(self, player):
        x = WIDTH // 2 - player.rect.centerx
        y = HEIGHT // 2 - player.rect.centery

        # 카메라 제한
        x = min(0, x)
        y = min(0, y)

        x = max(-WIDTH, x)
        y = max(-HEIGHT, y)

        self.camera = pygame.Rect(x, y, WORLD_WIDTH, WORLD_HEIGHT)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.direction = direction
        self.lifetime = 0.5
        self.dtt = 0

    def update(self, dt):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        self.dtt += dt

        if self.dtt > self.lifetime:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = enemy_images[enemy_type][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = pygame.Vector2()

        self.animation_index = 0
        self.animation_speed = 0.2
        self.animation_time = 0
        self.speed = 2

    def update(self, dt):
        self.move()

        if self.direction.length():
            self.animation_time += dt

            if self.animation_time > self.animation_speed:
                self.animation_time = 0
                self.animation_index += 1
                self.animation_index = self.animation_index % 4
                self.image = enemy_images[self.enemy_type][self.animation_index]
        else:
            self.animation_index = 0
            self.image = enemy_images[self.enemy_type][self.animation_index]

    def move(self):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        self.direction.x = dx
        self.direction.y = dy

        # 대각선 속도 보정
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

        self.rect.x += self.direction.x * self.speed
        self.rect.y += self.direction.y * self.speed


# player initialization
player = Player(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

camera = Camera()

# 스프라이트 그룹 (all_sprites = 모든 스프라이트를 저장할 변수)
all_sprites = pygame.sprite.Group()
# 장애물 그룹
obstacles = pygame.sprite.Group()
# 총알 그룹
bullets = pygame.sprite.Group()
# 적 그룹
enemies = pygame.sprite.Group()

all_sprites.add(player)

for _ in range(20):
    x = random.randint(0, WORLD_WIDTH)
    y = random.randint(0, WORLD_HEIGHT)
    obstacle = Obstacle(x, y)
    all_sprites.add(obstacle)
    obstacles.add(obstacle)

for _ in range(10):
    x = random.randint(0, WORLD_WIDTH)
    y = random.randint(0, WORLD_HEIGHT)
    enemy_type = random.choice(["bat", "blob", "skeleton"])
    enemy = Enemy(x, y, enemy_type)
    all_sprites.add(enemy)
    enemies.add(enemy)

# 게임 루프
running = True
clock = pygame.time.Clock()
enemy_timer = 0

while running:
    # 초 당 60프레임
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx = keys[pygame.K_d] - keys[pygame.K_a]
    dy = keys[pygame.K_s] - keys[pygame.K_w]

    player.update(dt)
    player.move(dx, dy)

    bullets.update(dt)
    enemies.update(dt)

    # 플레이어 충돌 체크
    if pygame.sprite.spritecollide(player, obstacles, False):
        player.rect.x -= dx * player.speed
        player.rect.y -= dy * player.speed

    # 총알 발사
    player.shoot_timer += dt * 1000
    if player.shoot_timer >= player.shoot_delay:
        player.shoot_timer = 0
        new_bullets = player.shoot()
        bullets.add(new_bullets)
        all_sprites.add(new_bullets)

    # 무작위 적 생성
    enemy_timer += dt

    if enemy_timer > 1:
        enemy_timer = 0
        enemy_type = random.choice(["bat", "blob", "skeleton"])
        x = random.randint(0, WORLD_WIDTH)
        y = random.randint(0, WORLD_HEIGHT)
        new_enemy = Enemy(x, y, enemy_type)
        all_sprites.add(new_enemy)
        enemies.add(new_enemy)

    # 그리는 부분
    camera.update(player)

    screen.fill(GREEN)

    # all_sprites.draw(screen)
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))

    pygame.display.flip()

pygame.quit()
