import pygame
import math
import sys
import random

# ======================
# НАСТРОЙКИ ИГРЫ
# ======================
WIDTH, HEIGHT = 1000, 600
FPS = 60
TITLE = "Технопаук: Побег"

# Цвета
BLACK = (10, 10, 15)
DARK = (25, 25, 35)
GRAY = (60, 60, 75)
LIGHT_GRAY = (120, 120, 140)
CYAN = (0, 220, 255)
YELLOW = (255, 220, 50)
RED = (220, 50, 50)
WHITE = (240, 240, 255)
ORANGE = (255, 140, 40)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 20)
font_big = pygame.font.SysFont("Arial", 48)


# ======================
# КЛАСС ИГРОКА (ТЕХНОПАУК)
# ======================
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 28
        self.height = 22
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 4.2
        self.jump_power = -11.5
        self.on_ground = False
        self.facing_right = True
        self.alive = True
        self.stars = 0
        self.anim_timer = 0

    def update(self, platforms, keys):
        if not self.alive:
            return

        # Управление
        self.vel_x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
            self.facing_right = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
            self.facing_right = True

        # Прыжок
        if (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        # Гравитация
        self.vel_y += 0.55
        if self.vel_y > 14:
            self.vel_y = 14

        # Движение по X
        self.x += self.vel_x
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_x > 0:
                    self.x = p.rect.left - self.width
                elif self.vel_x < 0:
                    self.x = p.rect.right
                self.vel_x = 0

        # Движение по Y
        self.y += self.vel_y
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.on_ground = False
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if self.vel_y > 0:
                    self.y = p.rect.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.y = p.rect.bottom
                    self.vel_y = 0

        # Границы экрана
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width
        if self.y > HEIGHT + 50:
            self.alive = False

        self.anim_timer += 0.25

    def draw(self, surface):
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        # Тело
        pygame.draw.ellipse(surface, (40, 45, 55), (self.x + 4, self.y + 4, 20, 16))
        pygame.draw.ellipse(surface, CYAN, (self.x + 6, self.y + 6, 16, 12), 1)

        # Голова / глаза
        eye_offset = 4 if self.facing_right else -4
        pygame.draw.circle(surface, CYAN, (cx + eye_offset, cy - 3), 4)
        pygame.draw.circle(surface, WHITE, (cx + eye_offset + 1, cy - 4), 2)

        # Лапки (процедурная анимация через синус)
        leg_phase = self.anim_timer
        direction = 1 if self.facing_right else -1

        for i in range(4):
            angle = math.sin(leg_phase + i * 0.9) * 0.6
            base_x = cx - 6 * direction + (i % 2) * 8 * direction
            base_y = cy + 2

            # Верхняя часть лапки
            mid_x = base_x + math.cos(angle) * 10 * direction
            mid_y = base_y + 8 + math.sin(angle) * 4
            # Нижняя часть
            end_x = mid_x + math.cos(angle + 0.4) * 9 * direction
            end_y = mid_y + 7

            color = (80, 90, 110)
            pygame.draw.line(surface, color, (base_x, base_y), (mid_x, mid_y), 3)
            pygame.draw.line(surface, color, (mid_x, mid_y), (end_x, end_y), 2)
            pygame.draw.circle(surface, CYAN, (int(end_x), int(end_y)), 2)


# ======================
# ПЛАТФОРМЫ
# ======================
class Platform:
    def __init__(self, x, y, w, h, sway=False):
        self.base_y = y
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.sway = sway
        self.timer = random.random() * 10
        self.rect = pygame.Rect(x, y, w, h)

    def update(self):
        if self.sway:
            self.timer += 0.03
            self.y = self.base_y + math.sin(self.timer) * 4
            self.rect.y = int(self.y)

    def draw(self, surface):
        # Основная платформа
        pygame.draw.rect(surface, (45, 48, 60), self.rect)
        pygame.draw.rect(surface, (70, 75, 95), self.rect, 2)

        # Детали (болты / линии)
        for i in range(8, self.width, 18):
            pygame.draw.circle(surface, (90, 95, 110), (self.x + i, self.y + 6), 2)
            pygame.draw.line(surface, (55, 58, 70), (self.x + i, self.y + 2), (self.x + i, self.y + self.height - 2), 1)


# ======================
# МОНСТР
# ======================
class Monster:
    def __init__(self, x, y, left_bound, right_bound):
        self.x = x
        self.y = y
        self.width = 48
        self.height = 36
        self.speed = 1.8
        self.direction = 1
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.anim_timer = 0
        self.rect = pygame.Rect(x, y, self.width, self.height)

    def update(self, player):
        self.anim_timer += 0.12

        # Простое патрулирование
        self.x += self.speed * self.direction
        if self.x <= self.left_bound or self.x >= self.right_bound:
            self.direction *= -1

        # Если игрок близко — немного ускоряется
        dist = abs(self.x - player.x)
        if dist < 220 and abs(self.y - player.y) < 80:
            self.speed = 2.7
            if player.x > self.x:
                self.direction = 1
            else:
                self.direction = -1
        else:
            self.speed = 1.8

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        # Тело монстра
        pygame.draw.ellipse(surface, (50, 20, 30), (self.x, self.y + 5, self.width, 28))
        pygame.draw.ellipse(surface, (90, 30, 40), (self.x + 4, self.y + 8, self.width - 8, 22))

        # Голова
        head_x = cx + (12 if self.direction > 0 else -12)
        pygame.draw.circle(surface, (70, 25, 35), (int(head_x), cy - 2), 14)
        # Глаза
        eye_dir = 5 if self.direction > 0 else -5
        pygame.draw.circle(surface, RED, (int(head_x + eye_dir), cy - 5), 5)
        pygame.draw.circle(surface, (255, 100, 100), (int(head_x + eye_dir + 1), cy - 6), 2)

        # Лапки / щупальца (процедурная анимация)
        for i in range(3):
            phase = self.anim_timer + i * 1.2
            leg_x = self.x + 10 + i * 14
            start = (leg_x, self.y + 25)
            mid = (leg_x + math.sin(phase) * 8, self.y + 38)
            end = (leg_x + math.sin(phase + 0.5) * 12, self.y + 48)
            pygame.draw.line(surface, (60, 25, 35), start, mid, 4)
            pygame.draw.line(surface, (80, 30, 40), mid, end, 3)


# ======================
# ЗВЁЗДОЧКИ
# ======================
class Star:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.collected = False
        self.timer = random.random() * 5
        self.rect = pygame.Rect(x - 12, y - 12, 24, 24)

    def update(self):
        self.timer += 0.08

    def draw(self, surface):
        if self.collected:
            return
        # Лёгкое покачивание
        offset = math.sin(self.timer) * 3
        points = []
        for i in range(5):
            angle = math.radians(i * 72 - 90)
            px = self.x + math.cos(angle) * self.radius
            py = self.y + offset + math.sin(angle) * self.radius
            points.append((px, py))
            # внутренние точки
            angle2 = math.radians(i * 72 - 90 + 36)
            px2 = self.x + math.cos(angle2) * (self.radius * 0.4)
            py2 = self.y + offset + math.sin(angle2) * (self.radius * 0.4)
            points.append((px2, py2))
        pygame.draw.polygon(surface, YELLOW, points)
        pygame.draw.polygon(surface, ORANGE, points, 1)


# ======================
# ВЫХОД
# ======================
class Exit:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 50
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.timer = 0

    def update(self):
        self.timer += 0.1

    def draw(self, surface):
        # Рамка
        pygame.draw.rect(surface, (30, 80, 90), self.rect, border_radius=4)
        pygame.draw.rect(surface, CYAN, self.rect, 3, border_radius=4)
        # Светящийся центр
        glow = 100 + int(math.sin(self.timer) * 40)
        pygame.draw.rect(surface, (0, glow, glow), 
                         (self.x + 8, self.y + 8, self.width - 16, self.height - 16), border_radius=3)
        text = font_small.render("EXIT", True, WHITE)
        surface.blit(text, (self.x + 5, self.y + 18))


# ======================
# СОЗДАНИЕ УРОВНЯ
# ======================
def create_level():
    platforms = [
        # Пол
        Platform(0, 560, 1000, 40),
        # Основные платформы
        Platform(80, 480, 160, 20),
        Platform(280, 420, 140, 20, sway=True),
        Platform(480, 360, 130, 20),
        Platform(650, 300, 150, 20, sway=True),
        Platform(820, 420, 120, 20),
        Platform(150, 340, 100, 20),
        Platform(350, 280, 110, 20),
        Platform(50, 220, 130, 20, sway=True),
        Platform(250, 170, 160, 20),
        Platform(500, 200, 140, 20),
        Platform(720, 180, 130, 20, sway=True),
        Platform(880, 250, 100, 20),
        # Дополнительные
        Platform(400, 500, 90, 18),
        Platform(600, 480, 80, 18),
    ]

    stars = [
        Star(140, 450),
        Star(320, 380),
        Star(530, 320),
        Star(700, 260),
        Star(870, 380),
        Star(100, 180),
        Star(300, 130),
        Star(560, 160),
        Star(780, 140),
        Star(920, 210),
    ]

    monster = Monster(400, 524, 200, 700)
    exit_door = Exit(920, 200)
    player = Player(40, 520)

    return platforms, stars, monster, exit_door, player


# ======================
# ОСНОВНОЙ ЦИКЛ
# ======================
def main():
    platforms, stars, monster, exit_door, player = create_level()
    game_state = "playing"  # playing / win / lose
    total_stars = len(stars)

    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r and game_state != "playing":
                    # Рестарт
                    platforms, stars, monster, exit_door, player = create_level()
                    game_state = "playing"

        if game_state == "playing":
            # Обновление
            for p in platforms:
                p.update()
            player.update(platforms, keys)
            monster.update(player)
            for s in stars:
                s.update()
            exit_door.update()

            # Сбор звёзд
            for s in stars:
                if not s.collected and player.rect.colliderect(s.rect):
                    s.collected = True
                    player.stars += 1

            # Столкновение с монстром
            if player.rect.colliderect(monster.rect):
                player.alive = False
                game_state = "lose"

            # Победа
            if player.rect.colliderect(exit_door.rect):
                game_state = "win"

            if not player.alive:
                game_state = "lose"

        # ===== ОТРИСОВКА =====
        screen.fill((18, 18, 28))

        # Фон (простые трубы / конструкции)
        for i in range(0, WIDTH, 80):
            pygame.draw.line(screen, (30, 30, 42), (i, 0), (i, HEIGHT), 1)
        pygame.draw.rect(screen, (22, 22, 32), (0, 0, WIDTH, 40))

        # Платформы
        for p in platforms:
            p.draw(screen)

        # Звёзды
        for s in stars:
            s.draw(screen)

        # Выход
        exit_door.draw(screen)

        # Монстр
        monster.draw(screen)

        # Игрок
        player.draw(screen)

        # UI
        stars_text = font.render(f"Звёзды: {player.stars}/{total_stars}", True, YELLOW)
        screen.blit(stars_text, (20, 12))

        hint = font_small.render("A/D или ←/→ — ходьба   W/↑/Пробел — прыжок   R — рестарт   Esc — выход", True, LIGHT_GRAY)
        screen.blit(hint, (20, HEIGHT - 28))

        # Экраны победы / поражения
        if game_state == "win":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            text = font_big.render("ТЫ ВЫБРАЛСЯ!", True, CYAN)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))
            sub = font.render(f"Собрано звёзд: {player.stars}/{total_stars}", True, YELLOW)
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 20))
            restart = font_small.render("Нажми R, чтобы сыграть ещё раз", True, WHITE)
            screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 60))

        elif game_state == "lose":
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((40, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            text = font_big.render("ТЕБЯ ПОЙМАЛИ...", True, RED)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 30))
            restart = font_small.render("Нажми R, чтобы попробовать снова", True, WHITE)
            screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, HEIGHT // 2 + 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
