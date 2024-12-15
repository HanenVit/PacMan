import pygame
import math
import random

class PacMan(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = 15
        self.direction = 0  # Угол в градусах
        self.speed = 4
        self.mouth_angle = 0
        self.mouth_change = 5
        self.powered_up = False
        self.power_timer = 0
        self.rect = pygame.Rect(x-self.radius, y-self.radius,
                              self.radius*2, self.radius*2)

    def handle_input(self, key):
        if key == pygame.K_RIGHT:
            self.direction = 0
        elif key == pygame.K_LEFT:
            self.direction = 180
        elif key == pygame.K_UP:
            self.direction = 90
        elif key == pygame.K_DOWN:
            self.direction = 270

    def update(self, maze):
        # Анимация рта
        self.mouth_angle += self.mouth_change
        if self.mouth_angle >= 45 or self.mouth_angle <= 0:
            self.mouth_change = -self.mouth_change

        # Движение
        rad = math.radians(self.direction)
        new_x = self.x + math.cos(rad) * self.speed
        new_y = self.y - math.sin(rad) * self.speed

        # Проверка столкновений со стенами
        grid_x = int(new_x // 30)
        grid_y = int(new_y // 30)
        
        if 0 <= grid_x < len(maze[0]) and 0 <= grid_y < len(maze):
            if maze[grid_y][grid_x] != 1:
                self.x = new_x
                self.y = new_y
                self.rect.center = (self.x, self.y)

        # Обработка режима энергетика
        if self.powered_up:
            self.power_timer += 1
            if self.power_timer >= 300:  # 5 секунд
                self.powered_up = False
                self.power_timer = 0

    def draw(self, screen):
        # Рисуем тело
        pygame.draw.circle(screen, (255, 255, 0),
                         (int(self.x), int(self.y)), self.radius)
        
        # Рисуем рот
        start_angle = math.radians(self.direction - self.mouth_angle)
        end_angle = math.radians(self.direction + self.mouth_angle)
        
        pygame.draw.polygon(screen, (0, 0, 0), [
            (self.x, self.y),
            (self.x + math.cos(start_angle) * self.radius,
             self.y - math.sin(start_angle) * self.radius),
            (self.x + math.cos(end_angle) * self.radius,
             self.y - math.sin(end_angle) * self.radius)
        ])

class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.x = x
        self.y = y
        self.speed = speed
        self.radius = 15
        self.color = random.choice([(255, 0, 0), (255, 182, 255),
                                  (0, 255, 255), (255, 182, 85)])
        self.rect = pygame.Rect(x-self.radius, y-self.radius,
                              self.radius*2, self.radius*2)
        self.direction = random.choice([0, 90, 180, 270])

    def update(self, maze, pacman):
        # Простой ИИ: следование за пакманом
        dx = pacman.x - self.x
        dy = pacman.y - self.y
        
        if abs(dx) > abs(dy):
            self.direction = 0 if dx > 0 else 180
        else:
            self.direction = 270 if dy > 0 else 90

        rad = math.radians(self.direction)
        new_x = self.x + math.cos(rad) * self.speed
        new_y = self.y + math.sin(rad) * self.speed

        # Проверка столкновений
        grid_x = int(new_x // 30)
        grid_y = int(new_y // 30)
        
        if 0 <= grid_x < len(maze[0]) and 0 <= grid_y < len(maze):
            if maze[grid_y][grid_x] != 1:
                self.x = new_x
                self.y = new_y
                self.rect.center = (self.x, self.y)
            else:
                self.direction = random.choice([0, 90, 180, 270])

    def reset_position(self):
        self.x = 450
        self.y = 300
        self.rect.center = (self.x, self.y)

    def draw(self, screen):
        # Рисуем тело призрака
        pygame.draw.circle(screen, self.color,
                         (int(self.x), int(self.y)), self.radius)
        
        # Рисуем нижнюю часть
        pygame.draw.rect(screen, self.color,
                        (self.x - self.radius, self.y,
                         self.radius * 2, self.radius))
        
        # Рисуем глаза
        eye_color = (255, 255, 255)
        pygame.draw.circle(screen, eye_color,
                         (int(self.x - 5), int(self.y - 5)), 4)
        pygame.draw.circle(screen, eye_color,
                         (int(self.x + 5), int(self.y - 5)), 4)
        
        # Зрачки
        pupil_color = (0, 0, 255)
        pygame.draw.circle(screen, pupil_color,
                         (int(self.x - 5), int(self.y - 5)), 2)
        pygame.draw.circle(screen, pupil_color,
                         (int(self.x + 5), int(self.y - 5)), 2)

class Dot(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = 3
        self.rect = pygame.Rect(x-self.radius, y-self.radius,
                              self.radius*2, self.radius*2)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255),
                         (int(self.x), int(self.y)), self.radius)

class PowerPellet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = 8
        self.rect = pygame.Rect(x-self.radius, y-self.radius,
                              self.radius*2, self.radius*2)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255),
                         (int(self.x), int(self.y)), self.radius) 