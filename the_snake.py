"""
Модуль реализует игру 'Змейка', включая игровые классы,
обработку управления и основной игровой цикл.
"""
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

# Цвета:
BOARD_BACKGROUND_COLOR = (20, 25, 40)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)
ROCK_COLOR = (100, 100, 100)

# Настройки оттенков:
HUE_CHANGE_INTERVAL = 20
HUE_MAX = 360
BACKGROUND_SATURATION = 50
BACKGROUND_VALUE = 50
HSV_ALPHA = 100
TEXT_SATURATION = 100
TEXT_VALUE = 100

# Координаты и размеры области счёта:
SCORE_TEXT_X = 10
SPEED_TEXT_Y = 10
SCORE_TEXT_Y = 35
BEST_SCORE_TEXT_Y = 60
SCORE_PANEL_WIDTH = 150
SCORE_PANEL_HEIGHT = 90

# Настройка игрового окна:
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует игровой объект."""
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает игровой объект."""
        raise NotImplementedError

    def randomize_position(self, occupied_positions):
        """Устанавливает позицию объекта в свободной клетке."""
        random_position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )
        while random_position in occupied_positions:
            random_position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )
        self.position = random_position


class Apple(GameObject):
    """Игровой объект, представляющий яблоко."""

    def __init__(self, occupied_positions=(), body_color=APPLE_COLOR):
        """Создаёт яблоко в свободной позиции."""
        super().__init__(None, body_color)
        self.randomize_position(occupied_positions)

    def respawn(self, occupied_positions):
        """Перемещает яблоко в свободную клетку."""
        self.randomize_position(occupied_positions)

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Rock(GameObject):
    """Игровой объект, представляющий препятствие."""

    def __init__(self, occupied_positions):
        """Создаёт препятствие в свободной позиции."""
        super().__init__(None, ROCK_COLOR)
        self.randomize_position(occupied_positions)

    def respawn(self, occupied_positions):
        """Перемещает камень в свободную клетку."""
        self.randomize_position(occupied_positions)

    def draw(self):
        """Отрисовывает препятствие на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Игровой объект, представляющий змею."""

    def __init__(self):
        """Создаёт змею с начальной позицией и направлением."""
        super().__init__((20, 240), SNAKE_COLOR)
        self.speed = 10
        self.reset()

    def get_head_position(self):
        """Возвращает текущую позицию головы змеи."""
        return self.positions[0]

    def move(self):
        """Перемещает змею на одну клетку."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_position_x = (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH
        new_position_y = (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_position_x, new_position_y)
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def grow(self):
        """Увеличивает длину змейки."""
        self.length += 1

    def draw(self):
        """Отрисовывает голову и тело змеи."""
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
    hue = (current_time // HUE_CHANGE_INTERVAL) % HUE_MAX
    color = pygame.Color(0)
    color.hsva = (hue, BACKGROUND_SATURATION, BACKGROUND_VALUE, HSV_ALPHA)
    for x_position in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(
            screen, color, (x_position, 0),
            (x_position, SCREEN_HEIGHT)
        )
    for y_position in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(
            screen, color, (0, y_position),
            (SCREEN_WIDTH, y_position)
        )


def erase_cell(position):
    """Стирает клетку и восстанавливает линии сетки."""
    x_position, y_position = position
    rect = pygame.Rect(x_position, y_position, GRID_SIZE, GRID_SIZE)
    screen.fill(BOARD_BACKGROUND_COLOR, rect)
    current_time = pygame.time.get_ticks()
    hue = (current_time // HUE_CHANGE_INTERVAL) % HUE_MAX
    color = pygame.Color(0)
    color.hsva = (hue, BACKGROUND_SATURATION, BACKGROUND_VALUE, HSV_ALPHA)
    pygame.draw.line(
        screen, color, (x_position, y_position),
        (x_position + GRID_SIZE, y_position)
    )
    pygame.draw.line(
        screen, color, (x_position, y_position + GRID_SIZE),
        (x_position + GRID_SIZE, y_position + GRID_SIZE)
    )
    pygame.draw.line(
        screen, color, (x_position, y_position),
        (x_position, y_position + GRID_SIZE)
    )
    pygame.draw.line(
        screen, color, (x_position + GRID_SIZE, y_position),
        (x_position + GRID_SIZE, y_position + GRID_SIZE)
    )


def draw_score(font, speed, score, best_score):
    """Обновляет панель со скоростью и счётом."""
    current_time = pygame.time.get_ticks()
    hue = (current_time // HUE_CHANGE_INTERVAL) % HUE_MAX
    background_color = pygame.Color(0)
    background_color.hsva = (
        hue, BACKGROUND_SATURATION, BACKGROUND_VALUE, HSV_ALPHA
    )
    for x_position in range(0, SCORE_PANEL_WIDTH, GRID_SIZE):
        pygame.draw.line(
            screen, background_color, (x_position, 0),
            (x_position, SCORE_PANEL_HEIGHT)
        )
    for y_position in range(0, SCORE_PANEL_HEIGHT, GRID_SIZE):
        pygame.draw.line(
            screen, background_color, (0, y_position),
            (SCORE_PANEL_WIDTH, y_position)
        )
    text_color = pygame.Color(0)
    text_color.hsva = (hue, TEXT_SATURATION, TEXT_VALUE, HSV_ALPHA)
    speed_text = font.render(f'Speed: {speed}', True, text_color)
    score_text = font.render(f'Score: {score}', True, text_color)
    best_text = font.render(f'Best: {best_score}', True, text_color)
    screen.blit(speed_text, (SCORE_TEXT_X, SPEED_TEXT_Y))
    screen.blit(score_text, (SCORE_TEXT_X, SCORE_TEXT_Y))
    screen.blit(best_text, (SCORE_TEXT_X, BEST_SCORE_TEXT_Y))


def draw_scene(snake, apple, rock, font, score, best_score):
    """Полностью перерисовывает поле при запуске или сбросе."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    draw_background()
    draw_score(font, snake.speed, score, best_score)
    rock.draw()
    snake.draw()
    apple.draw()
    pygame.display.update()


def main():
    """Запускает основной игровой цикл."""
    font = pygame.font.Font(None, 30)
    snake = Snake()
    apple = Apple(snake.positions)
    rock = Rock(snake.positions + [apple.position])
    last_rock_move = pygame.time.get_ticks()
    score = 0
    best_score = 0

    draw_scene(snake, apple, rock, font, score, best_score)

    while True:
        clock.tick(snake.speed)
        current_time = pygame.time.get_ticks()

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        ate_apple = snake.get_head_position() == apple.position
        if ate_apple:
            snake.grow()
            score += 1
            apple.respawn(snake.positions + [rock.position])

        rock_moved = False
        old_rock_position = rock.position
        if current_time - last_rock_move > 5000:
            rock.respawn(snake.positions + [apple.position])
            last_rock_move = current_time
            rock_moved = old_rock_position != rock.position

        if score > best_score:
            best_score = score

        collided = (
            snake.get_head_position() in snake.positions[1:]
            or snake.get_head_position() == rock.position
        )

        if collided:
            score = 0
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.respawn(snake.positions + [rock.position])
            last_rock_move = current_time
            draw_scene(snake, apple, rock, font, score, best_score)
            continue

        if snake.last is not None:
            erase_cell(snake.last)

        if rock_moved:
            erase_cell(old_rock_position)

        apple.draw()
        rock.draw()
        draw_score(font, snake.speed, score, best_score)
        snake.draw()
        pygame.display.update()


def handle_keys(game_object):
    """Обрабатывает действия пользователя с клавиатуры."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
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
