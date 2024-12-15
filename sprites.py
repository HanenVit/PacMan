import pygame
import math
import random

class PacMan(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = 12
        self.direction = 0  # Угол в градусах
        self.speed = 4
        self.dx = 0  # Добавляем переменные для движения
        self.dy = 0
        self.mouth_angle = 0
        self.mouth_change = 5
        self.powered_up = False
        self.power_timer = 0
        self.rect = pygame.Rect(x-self.radius, y-self.radius,
                              self.radius*2, self.radius*2)

    def handle_input(self, key):
        if key == pygame.K_LEFT:
            self.dx = -self.speed
            self.dy = 0
        elif key == pygame.K_RIGHT:
            self.dx = self.speed
            self.dy = 0
        elif key == pygame.K_UP:
            self.dx = 0
            self.dy = -self.speed
        elif key == pygame.K_DOWN:
            self.dx = 0
            self.dy = self.speed

    def handle_key_up(self, key):
        # Останавливаем движение при отпускании соответствующей клавиши
        if key == pygame.K_LEFT and self.dx < 0:
            self.dx = 0
        elif key == pygame.K_RIGHT and self.dx > 0:
            self.dx = 0
        elif key == pygame.K_UP and self.dy < 0:
            self.dy = 0
        elif key == pygame.K_DOWN and self.dy > 0:
            self.dy = 0

    def update(self, maze):
        # Анимация рта
        self.mouth_angle += self.mouth_change
        if self.mouth_angle >= 45 or self.mouth_angle <= 0:
            self.mouth_change = -self.mouth_change

        # Движение с использованием dx и dy
        new_x = self.x + self.dx
        new_y = self.y + self.dy

        # Проверяем границы игрового поля
        if new_x - self.radius < 0:
            new_x = self.radius
        elif new_x + self.radius > 900:  # WINDOW_WIDTH
            new_x = 900 - self.radius
        
        if new_y - self.radius < 0:
            new_y = self.radius
        elif new_y + self.radius > 600:  # WINDOW_HEIGHT
            new_y = 600 - self.radius

        # Обновляем направление для анимации
        if self.dx != 0 or self.dy != 0:
            self.direction = math.degrees(math.atan2(-self.dy, self.dx))

        # ��роверяем столкновения отдельно по X и Y
        can_move_x = True
        test_rect_x = pygame.Rect(new_x - self.radius, self.y - self.radius,
                               self.radius * 2, self.radius * 2)
        grid_x = int(new_x // 30)
        grid_y = int(self.y // 30)
        
        # Проверяем соседние клетки по X
        for check_x in [grid_x - 1, grid_x, grid_x + 1]:
            if 0 <= check_x < len(maze[0]):
                if maze[grid_y][check_x] == 1:
                    wall_rect = pygame.Rect(check_x * 30, grid_y * 30, 30, 30)
                    if test_rect_x.colliderect(wall_rect):
                        can_move_x = False
                        break

        # Затем пробуем двигаться по Y
        can_move_y = True
        test_rect_y = pygame.Rect(self.x - self.radius, new_y - self.radius,
                               self.radius * 2, self.radius * 2)
        grid_x = int(self.x // 30)
        grid_y = int(new_y // 30)
        
        # Проверяем соседние клетки по Y
        for check_y in [grid_y - 1, grid_y, grid_y + 1]:
            if 0 <= check_y < len(maze):
                if maze[check_y][grid_x] == 1:
                    wall_rect = pygame.Rect(grid_x * 30, check_y * 30, 30, 30)
                    if test_rect_y.colliderect(wall_rect):
                        can_move_y = False
                        break

        # Применяем движение только по разрешенным осям
        if can_move_x:
            self.x = new_x
        if can_move_y:
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
        self.radius = 12
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

        # Проверяем границы игрового поля
        if new_x - self.radius < 0:
            new_x = self.radius
        elif new_x + self.radius > 900:  # WINDOW_WIDTH
            new_x = 900 - self.radius
        
        if new_y - self.radius < 0:
            new_y = self.radius
        elif new_y + self.radius > 600:  # WINDOW_HEIGHT
            new_y = 600 - self.radius

        # Проверяем столкновения отдельно по X и Y
        can_move_x = True
        test_rect_x = pygame.Rect(new_x - self.radius, self.y - self.radius,
                               self.radius * 2, self.radius * 2)
        grid_x = int(new_x // 30)
        grid_y = int(self.y // 30)
        
        for check_x in [grid_x - 1, grid_x, grid_x + 1]:
            if 0 <= check_x < len(maze[0]):
                if maze[grid_y][check_x] == 1:
                    wall_rect = pygame.Rect(check_x * 30, grid_y * 30, 30, 30)
                    if test_rect_x.colliderect(wall_rect):
                        can_move_x = False
                        break

        can_move_y = True
        test_rect_y = pygame.Rect(self.x - self.radius, new_y - self.radius,
                               self.radius * 2, self.radius * 2)
        grid_x = int(self.x // 30)
        grid_y = int(new_y // 30)
        
        for check_y in [grid_y - 1, grid_y, grid_y + 1]:
            if 0 <= check_y < len(maze):
                if maze[check_y][grid_x] == 1:
                    wall_rect = pygame.Rect(grid_x * 30, check_y * 30, 30, 30)
                    if test_rect_y.colliderect(wall_rect):
                        can_move_y = False
                        break

        # Если не можем двигаться, меняем направление
        if not (can_move_x or can_move_y):
            self.direction = random.choice([0, 90, 180, 270])
        else:
            if can_move_x:
                self.x = new_x
            if can_move_y:
                self.y = new_y

        self.rect.center = (self.x, self.y)

    def reset_position(self, maze):
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            x = random.randint(1, len(maze[0]) - 2)
            y = random.randint(1, len(maze) - 2)
            
            if maze[y][x] == 0:
                # Проверяем горизонтальный проход
                if (x > 0 and x < len(maze[0])-1 and 
                    maze[y][x-1] == 0 and maze[y][x+1] == 0):
                    self.x = x * 30 + 15
                    self.y = y * 30 + 15
                    self.rect.center = (self.x, self.y)
                    return
                
                # Проверяем вертикальный проход
                if (y > 0 and y < len(maze)-1 and 
                    maze[y-1][x] == 0 and maze[y+1][x] == 0):
                    self.x = x * 30 + 15
                    self.y = y * 30 + 15
                    self.rect.center = (self.x, self.y)
                    return
            
            attempts += 1
        
        # Если не нашли идеальную позицию, ищем любой проход
        for y in range(1, len(maze) - 1):
            for x in range(1, len(maze[0]) - 1):
                if maze[y][x] == 0:
                    if (x > 0 and x < len(maze[0])-1 and 
                        maze[y][x-1] == 0 and maze[y][x+1] == 0):
                        self.x = x * 30 + 15
                        self.y = y * 30 + 15
                        self.rect.center = (self.x, self.y)
                        return
                    if (y > 0 and y < len(maze)-1 and 
                        maze[y-1][x] == 0 and maze[y+1][x] == 0):
                        self.x = x * 30 + 15
                        self.y = y * 30 + 15
                        self.rect.center = (self.x, self.y)
                        return

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