import random

def generate_maze(width, height):
    # Создаем пустой лабиринт
    maze = [[1 for x in range(width)] for y in range(height)]
    
    def carve_path(x, y):
        maze[y][x] = 0
        
        # Направления: вправо, влево, вниз, вверх
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < width and 0 <= new_y < height and
                maze[new_y][new_x] == 1):
                maze[y + dy//2][x + dx//2] = 0
                carve_path(new_x, new_y)

    # Начинаем с случайной точки
    start_x = random.randrange(0, width, 2)
    start_y = random.randrange(0, height, 2)
    carve_path(start_x, start_y)
    
    # Добавляем дополнительные проходы
    for _ in range(width * height // 10):
        x = random.randint(1, width-2)
        y = random.randint(1, height-2)
        maze[y][x] = 0

    return maze 