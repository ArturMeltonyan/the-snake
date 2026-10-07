from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Клавиши регулировки скорости движения змейки:
SPEED_UP_KEY = pygame.K_KP_PLUS
SPEED_DOWN_KEY = pygame.K_KP_MINUS

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (20, 25, 40)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)


# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует игровой объект."""
        self.position = (320, 240)
        self.body_color = body_color

    def draw(self):
        """Отрисовывает игровой объект."""
        pass

    def randomize_position(self):
        """Возвращает случайную позицию на игровом поле."""
        random_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        random_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        random_position = random_x, random_y
        return random_position


class Apple(GameObject):
    """Игровой объект, представляющий яблоко."""

    def __init__(self):
        """Создаёт яблоко и размещает его в случайной позиции."""
        super().__init__(None, APPLE_COLOR)
        self.position = self.randomize_position()
        self.body_color = APPLE_COLOR

    def draw(self):
        """Отрисовывает препятствие на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Rock(GameObject):
    """Игровой объект, представляющий препятствие."""

    def __init__(self):
        """Создаёт препятствие и размещает его в случайной позиции."""
        super().__init__(None, (100, 100, 100))
        self.position = self.randomize_position()
        self.body_color = (100, 100, 100)

    def draw(self):
        """Отрисовывает препятствие на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Игровой объект, представляющий змею."""

    def __init__(self):
        """Создаёт змею с начальной позицией и направлением движения."""
        super().__init__((20, 240), SNAKE_COLOR)
        self.length = 1
        self.positions = [(20, 240)]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.speed = 10

    def get_head_position(self):
        """Возвращает текущую позицию головы змеи."""
        return self.positions[0]

    def move(self):
        """Перемещает змею на одну клетку."""
        head = self.get_head_position()
        new_position_x = (
            head[0] + (self.direction[0] * GRID_SIZE)
        ) % SCREEN_WIDTH
        new_position_y = (
            head[1] + (self.direction[1] * GRID_SIZE)
        ) % SCREEN_HEIGHT
        new_head = new_position_x, new_position_y
        self.positions.insert(0, new_head)
        self.last = self.positions[-1]
        if len(self.positions) > self.length:
            self.positions.pop()

    def draw(self):
        """Отрисовывает змею на игровом поле."""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def update_direction(self):
        """Обновляет направление движения змеи."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def reset(self):
        """Сбрасывает состояние змеи после столкновения."""
        self.length = 1
        self.positions = [(20, 240)]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None


def draw_background():
    """Отрисовывает фон игрового поля."""
    current_time = pygame.time.get_ticks()
    hue = (current_time // 20) % 360

    color = pygame.Color(0)
    color.hsva = (hue, 50, 50, 100)

    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, color, (x, 0), (x, SCREEN_HEIGHT))

    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))


def draw_score(font, speed, score, best_score):
    """Отрисовывает текущую скорость и счёт игрока."""
    current_time = pygame.time.get_ticks()
    hue = (current_time // 20) % 360

    text_color = pygame.Color(0)
    text_color.hsva = (hue, 100, 100, 100)

    speed_text = font.render(f'Speed: {speed}', True, text_color)
    score_text = font.render(f'Score: {score}', True, text_color)
    best_text = font.render(f'Best: {best_score}', True, text_color)

    screen.blit(speed_text, (10, 10))
    screen.blit(score_text, (10, 35))
    screen.blit(best_text, (10, 60))


def main():
    """Запускает основной игровой цикл."""
    pygame.init()
    font = pygame.font.Font(None, 30)
    apple = Apple()
    snake = Snake()
    rock = Rock()
    last_rock_move = pygame.time.get_ticks()
    score = 0
    best_score = 0

    while True:
        clock.tick(snake.speed)
        screen.fill(BOARD_BACKGROUND_COLOR)
        current_time = pygame.time.get_ticks()
        draw_background()
        draw_score(font, snake.speed, score, best_score)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        if snake.get_head_position() == apple.position:
            snake.length += 1
            score += 1
            apple.position = apple.randomize_position()
        if current_time - last_rock_move > 5000:
            rock.position = rock.randomize_position()
            while (
                rock.position in snake.positions[1:]
                or rock.position == apple.position
            ):
                rock.position = rock.randomize_position()
            last_rock_move = current_time
        if score > best_score:
            best_score = score
        if snake.positions[0] in snake.positions[1:]:
            score = 0
            snake.reset()
        if snake.positions[0] == rock.position:
            score = 0
            snake.reset()

        rock.draw()
        snake.draw()
        apple.draw()

        pygame.display.update()


def handle_keys(game_object):
    """Обрабатывает действия пользователя с клавиатуры."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            handle_keydown(event, game_object)


def handle_keydown(event, game_object):
    """Обрабатывает нажатие клавиши."""
    if event.key == SPEED_DOWN_KEY:
        if game_object.speed > 1:
            game_object.speed -= 1
    elif event.key == SPEED_UP_KEY:
        if game_object.speed < 20:
            game_object.speed += 1
    elif event.key == pygame.K_UP and game_object.direction != DOWN:
        game_object.next_direction = UP
    elif event.key == pygame.K_DOWN and game_object.direction != UP:
        game_object.next_direction = DOWN
    elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
        game_object.next_direction = LEFT
    elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
        game_object.next_direction = RIGHT


if __name__ == '__main__':
    main()
