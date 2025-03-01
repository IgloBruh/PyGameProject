import pygame
import random
import os

# Инициализация PyGame
pygame.init()

# Настройки экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Coin Collector")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
MediumSeaGreen = (60, 179, 113)

# Шрифт
font = pygame.font.Font(None, 36)

# Загрузка изображений
def load_image(path, size=None):
    image = pygame.image.load(path)
    if size:
        image = pygame.transform.scale(image, size)
    return image

# Спрайты
player_image = load_image("sprites/player.png", (50, 50))  # Статичный спрайт игрока
coin_image = load_image("sprites/coin.png", (30, 30))
enemy_image = load_image("sprites/enemy.png", (40, 40))

# Звуки
coin_sound = pygame.mixer.Sound("sounds/coin.wav")
hit_sound = pygame.mixer.Sound("sounds/hit.wav")

# Уменьшаем громкость звуков в 2 раза
coin_sound.set_volume(0.2)
hit_sound.set_volume(0.2)

# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed = 5
        self.lives = 3

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

# Класс монеты
class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = coin_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)

    def reset(self):
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)

# Класс врага
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        self.speed = random.randint(2, 4)

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
            self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)

# Функция для отображения экрана завершения игры
def end_game_screen(coins_collected):
    screen.fill(MediumSeaGreen)
    coins_text = font.render(f"Собрано монет: {coins_collected}", True, BLACK)
    restart_text = font.render("Нажми R, чтобы попробовать ещё раз", True, BLACK)

    screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True

# Основной игровой цикл
def main():
    clock = pygame.time.Clock()
    player = Player()
    coin = Coin()
    enemies = [Enemy() for _ in range(3)]  # Создаём несколько врагов

    all_sprites = pygame.sprite.Group()
    all_sprites.add(player, coin, *enemies)

    coins_collected = 0
    level = 1
    running = True
    start_time = pygame.time.get_ticks()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.update(keys)
        for enemy in enemies:
            enemy.update()

        # Проверка сбора монеты
        if pygame.sprite.collide_rect(player, coin):
            coin_sound.play()
            coin.reset()
            coins_collected += 1
            if coins_collected % 10 == 0:
                level += 1
                for enemy in enemies:
                    enemy.speed += 1  # Увеличиваем скорость врагов

        # Проверка столкновения с врагами
        for enemy in enemies:
            if pygame.sprite.collide_rect(player, enemy):
                hit_sound.play()
                player.lives -= 1
                if player.lives == 0:
                    if end_game_screen(coins_collected):
                        main()  # Рестарт игры
                    else:
                        running = False
                enemy.rect.x = random.randint(0, SCREEN_WIDTH - enemy.rect.width)
                enemy.rect.y = random.randint(0, SCREEN_HEIGHT - enemy.rect.height)

        # Таймер
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        time_limit = 60 - elapsed_time
        if time_limit <= 0:
            if end_game_screen(coins_collected):
                main()  # Рестарт игры
            else:
                running = False

        # Отрисовка
        screen.fill(MediumSeaGreen)
        all_sprites.draw(screen)

        # Отображение счёта, уровня, жизней и времени
        score_text = font.render(f"Монеты: {coins_collected}", True, BLACK)
        level_text = font.render(f"Уровень: {level}", True, BLACK)
        lives_text = font.render(f"Жизни: {player.lives}", True, BLACK)
        time_text = font.render(f"Время: {time_limit}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        screen.blit(lives_text, (10, 90))
        screen.blit(time_text, (10, 130))

        pygame.display.flip()
        clock.tick(60)

    # Завершение игры
    pygame.quit()

if __name__ == "__main__":
    main()