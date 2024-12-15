import pygame
import random
import os
from maze_generator import generate_maze
from sprites import PacMan, Ghost, Dot, PowerPellet

pygame.init()
pygame.mixer.init()

# Константы
TILE_SIZE = 30
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FPS = 60

# Цвета
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

# Загрузка звуков
try:
    CHOMP_SOUND = pygame.mixer.Sound(os.path.join('sounds', 'chomp.wav'))
    DEATH_SOUND = pygame.mixer.Sound(os.path.join('sounds', 'death.wav'))
    POWER_PELLET_SOUND = pygame.mixer.Sound(os.path.join('sounds', 'power_pellet.wav'))
except:
    # Создаем пустой звуковой объект, который ничего не делает
    class NullSound:
        def play(self): pass
    
    CHOMP_SOUND = NullSound()
    DEATH_SOUND = NullSound()
    POWER_PELLET_SOUND = NullSound()
    print("Предупреждение: Звуковые файлы не найдены. Игра продолжится без звука.")

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()
        self.running = True
        self.score = 0
        self.level = 1
        self.reset_game()

    def reset_game(self):
        self.maze = generate_maze(30, 20)  # Размер лабиринта
        
        # Находим безопасную начальную позицию для Пакмана
        pacman_pos = self.find_safe_position()
        self.pacman = PacMan(pacman_pos[0], pacman_pos[1])  # Убираем дополнительные вычисления
        
        self.ghosts = []
        self.dots = []
        self.power_pellets = []
        
        # Создаем призраков в безопасных позициях
        for i in range(min(self.level, 4)):
            ghost_pos = self.find_safe_position()
            ghost = Ghost(ghost_pos[0], ghost_pos[1],  # Убираем дополнительные вычисления
                         1 + self.level * 0.2)
            self.ghosts.append(ghost)
        
        # Размещаем точки и энергетики
        self.place_dots_and_pellets()

    def find_safe_position(self):
        """Находит безопасную позицию в центре прохода"""
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            x = random.randint(1, len(self.maze[0]) - 2)
            y = random.randint(1, len(self.maze) - 2)
            
            if self.maze[y][x] == 0:
                # Проверяем горизонтальный проход
                if (x > 0 and x < len(self.maze[0])-1 and 
                    self.maze[y][x-1] == 0 and self.maze[y][x+1] == 0):
                    # Возвращаем координаты в пикселях
                    return (x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2)
                
                # Проверяем вертикальный проход
                if (y > 0 and y < len(self.maze)-1 and 
                    self.maze[y-1][x] == 0 and self.maze[y+1][x] == 0):
                    # Возвращаем координаты в пикселях
                    return (x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2)
            
            attempts += 1
        
        # Если не нашли идеальную позицию, ищем любой проход
        for y in range(1, len(self.maze) - 1):
            for x in range(1, len(self.maze[0]) - 1):
                if self.maze[y][x] == 0:
                    # Возвращаем координаты в пикселях
                    return (x * TILE_SIZE + TILE_SIZE//2, y * TILE_SIZE + TILE_SIZE//2)
        
        # Если вообще ничего не нашли
        return (TILE_SIZE + TILE_SIZE//2, TILE_SIZE + TILE_SIZE//2)

    def place_dots_and_pellets(self):
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] == 0:  # Пустое пространство
                    if random.random() < 0.7:  # 70% шанс появления точки
                        self.dots.append(Dot(x * TILE_SIZE + TILE_SIZE//2,
                                          y * TILE_SIZE + TILE_SIZE//2))
                    elif random.random() < 0.1:  # 10% шанс появления энергетика
                        self.power_pellets.append(PowerPellet(x * TILE_SIZE + TILE_SIZE//2,
                                                           y * TILE_SIZE + TILE_SIZE//2))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.pacman.handle_input(event.key)
            elif event.type == pygame.KEYUP:  # Добавляем обработку отпускания клавиши
                self.pacman.handle_key_up(event.key)

    def update(self):
        self.pacman.update(self.maze)
        
        # Обновление призраков
        for ghost in self.ghosts:
            ghost.update(self.maze, self.pacman)
        
        # Проверка столкновений с точками
        for dot in self.dots[:]:
            if self.pacman.rect.colliderect(dot.rect):
                self.dots.remove(dot)
                self.score += 10
                CHOMP_SOUND.play()

        # Проверка столкновений с энергетиками
        for pellet in self.power_pellets[:]:
            if self.pacman.rect.colliderect(pellet.rect):
                self.power_pellets.remove(pellet)
                self.score += 50
                self.pacman.powered_up = True
                POWER_PELLET_SOUND.play()

        # Проверка столкновений с призраками
        for ghost in self.ghosts:
            if self.pacman.rect.colliderect(ghost.rect):
                if self.pacman.powered_up:
                    ghost.reset_position(self.maze)
                    self.score += 200
                else:
                    DEATH_SOUND.play()
                    self.reset_game()
                    break

        # Проверка звершения уровня
        if not self.dots and not self.power_pellets:
            self.level += 1
            self.reset_game()

    def draw(self):
        self.screen.fill(BLACK)
        
        # Отрисовка лабиринта
        for y in range(len(self.maze)):
            for x in range(len(self.maze[0])):
                if self.maze[y][x] == 1:
                    pygame.draw.rect(self.screen, BLUE,
                                   (x * TILE_SIZE, y * TILE_SIZE,
                                    TILE_SIZE, TILE_SIZE))

        # Отрисовка точек и энергетиков
        for dot in self.dots:
            dot.draw(self.screen)
        for pellet in self.power_pellets:
            pellet.draw(self.screen)

        # Отрисовка призраков и пакмана
        for ghost in self.ghosts:
            ghost.draw(self.screen)
        self.pacman.draw(self.screen)

        # Отрисовка счета
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        level_text = font.render(f'Level: {self.level}', True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 40))

        pygame.display.flip()

if __name__ == '__main__':
    game = Game()
    game.run()
    pygame.quit() 