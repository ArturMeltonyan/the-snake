"""
Модуль реализует игру «Змейка».

Включает игровые классы, обработку управления
и основной игровой цикл.
"""
from random import choice, randint

import pygame as pg

from math import cos, sin, pi

import array

from pathlib import Path

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 840, 600
GRID_SIZE = 20

# Количество клеток, помещающихся на игровом поле:
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Клавиши регулировки скорости движения змейки:
SPEED_UP_KEY = pg.K_KP_PLUS
SPEED_DOWN_KEY = pg.K_KP_MINUS

# Цвета:
BOARD_BACKGROUND_COLOR = (12, 18, 35)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (45, 75, 145)
ROCK_COLOR = (100, 100, 100)
EAT_EFFECT_DURATION = 300
SCORE_PANEL_WIDTH = 125
SCORE_PANEL_HEIGHT = 110
STARS = [
    (randint(0, SCREEN_WIDTH - 1), randint(0, SCREEN_HEIGHT - 1))
    for _ in range(80)
]

# Настройка игрового окна:
pg.mixer.pre_init(frequency=44100, size=-16, channels=1, buffer=512)
pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


def create_apple_eat_sound():
    """Создаёт короткий низкий звук-поп."""
    sample_rate = 44100
    duration = 0.12
    sample_count = int(sample_rate * duration)
    samples = array.array("h")

    for index in range(sample_count):
        progress = index / sample_count
        time = index / sample_rate
        frequency = 420 - 220 * progress
        volume = (1 - progress) ** 3

        tone = (
            sin(2 * pi * frequency * time)
            + 0.25 * sin(2 * pi * frequency * 2.4 * time)
        )
        samples.append(int(15000 * volume * tone))
    return pg.mixer.Sound(buffer=samples.tobytes())


def create_watermelon_eat_sound():
    """Создаёт короткую праздничную восходящую мелодию."""
    sample_rate = 44100
    duration = 0.42
    sample_count = int(sample_rate * duration)
    samples = array.array("h")
    notes = (523, 659, 784)

    for index in range(sample_count):
        progress = index / sample_count
        note_index = min(int(progress * len(notes)), len(notes) - 1)
        frequency = notes[note_index]
        time = index / sample_rate
        envelope = sin(pi * progress)

        tone = (
            sin(2 * pi * frequency * time)
            + 0.3 * sin(2 * pi * frequency * 2 * time)
        )
        samples.append(int(11000 * envelope * tone))

    return pg.mixer.Sound(buffer=samples.tobytes())


def create_crash_sound():
    """Создаёт короткий низкий звук столкновения."""
    sample_rate = 44100
    duration = 0.35
    sample_count = int(sample_rate * duration)
    samples = array.array("h")

    for index in range(sample_count):
        progress = index / sample_count
        time = index / sample_rate
        frequency = 260 - 150 * progress
        volume = (1 - progress) ** 2

        tone = (
            sin(2 * pi * frequency * time)
            + 0.3 * sin(pi * frequency * time)
        )
        samples.append(int(13000 * volume * tone))

    return pg.mixer.Sound(buffer=samples.tobytes())


CRASH_SOUND = create_crash_sound()
APPLE_EAT_SOUND = create_apple_eat_sound()
WATERMELON_EAT_SOUND = create_watermelon_eat_sound()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует игровой объект."""
        position = position or (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает игровой объект."""
        raise NotImplementedError('Метод draw() должен быть переопределён.')

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

    def draw(self):
        """Отрисовывает увеличенное яблоко."""
        x, y = self.position

        pg.draw.circle(screen, (220, 35, 45), (x + 7, y + 10), 7)
        pg.draw.circle(screen, (220, 35, 45), (x + 13, y + 10), 7)
        pg.draw.rect(screen, (220, 35, 45), (x + 4, y + 9, 12, 7))
        pg.draw.circle(screen, (255, 130, 135), (x + 6, y + 9), 2)
        pg.draw.line(screen, (120, 75, 40), (x + 10, y + 5), (x + 12, y + 1), 2)
        pg.draw.ellipse(screen, (65, 190, 75), (x + 11, y + 1, 6, 3))


class Watermelon(GameObject):
    """Игровой объект в виде небольшого арбуза."""

    def __init__(self, occupied_positions=()):
        super().__init__(None, (30, 125, 55))
        self.randomize_position(occupied_positions)

    def respawn(self, occupied_positions):
        """Перемещает арбуз в свободную клетку."""
        self.randomize_position(occupied_positions)

    def draw(self):
        """Отрисовывает увеличенный полосатый арбуз."""
        x, y = self.position

        pg.draw.ellipse(screen, (5, 9, 20), (x - 2, y + 7, 25, 15))
        body = pg.Rect(x - 4, y + 2, 28, 18)
        pg.draw.ellipse(screen, (34, 112, 48), body)
        pg.draw.ellipse(screen, (74, 158, 67), (x - 2, y + 3, 24, 15))

        stripes = [
            (x + 1, y + 6, 2, 10),
            (x + 5, y + 4, 3, 13),
            (x + 10, y + 3, 3, 15),
            (x + 15, y + 4, 3, 13),
            (x + 20, y + 6, 2, 10),
        ]

        for stripe in stripes:
            pg.draw.ellipse(screen, (25, 91, 43), stripe)

        pg.draw.ellipse(screen, (145, 196, 105), (x, y + 5, 5, 2))
        pg.draw.ellipse(screen, (19, 75, 39), body, 1)
        pg.draw.line(screen, (91, 64, 37), (x + 10, y + 3), (x + 11, y), 2)
        pg.draw.ellipse(screen, (105, 178, 72), (x + 11, y, 6, 3))


class Rock(GameObject):
    """Игровой объект, представляющий препятствие."""

    def __init__(self, occupied_positions, body_color=ROCK_COLOR):
        """Создаёт препятствие в свободной позиции."""
        super().__init__(None, body_color)
        self.randomize_position(occupied_positions)

    def respawn(self, occupied_positions):
        """Перемещает камень в свободную клетку."""
        self.randomize_position(occupied_positions)

    def draw(self):
        """Отрисовывает объёмное препятствие."""
        rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(
            screen, self.body_color, rect, border_radius=5
        )
        pg.draw.line(
            screen, (150, 155, 165),
            (rect.left + 4, rect.top + 4),
            (rect.right - 5, rect.top + 4), 2
        )
        pg.draw.line(
            screen, (65, 70, 80),
            (rect.left + 4, rect.bottom - 4),
            (rect.right - 5, rect.bottom - 4), 2
        )
        pg.draw.circle(
            screen, (175, 180, 190),
            (rect.left + 6, rect.top + 7), 2
        )
        pg.draw.circle(
            screen, (75, 80, 90),
            (rect.right - 6, rect.top + 10), 2
        )
        pg.draw.line(
            screen, (110, 115, 125),
            (rect.left + 5, rect.centery),
            (rect.left + 9, rect.centery + 3), 2
        )
        pg.draw.rect(
            screen, BORDER_COLOR, rect, 1, border_radius=5
        )


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

    def get_danger_zone(self):
        """Возвращает клетки рядом с головой и перед ней."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        danger_positions = set()

        for offset_x in range(-5, 6):
            for offset_y in range(-5, 6):
                position = (
                    (head_x + offset_x * GRID_SIZE) % SCREEN_WIDTH,
                    (head_y + offset_y * GRID_SIZE) % SCREEN_HEIGHT
                )
                danger_positions.add(position)

        for step in range(1, 16):
            position = (
                (
                    head_x + direction_x * GRID_SIZE * step
                ) % SCREEN_WIDTH,
                (
                    head_y + direction_y * GRID_SIZE * step
                ) % SCREEN_HEIGHT
            )
            danger_positions.add(position)

        return list(danger_positions)

    def move(self):
        """Перемещает змею на одну клетку."""
        self.previous_positions = self.positions.copy()
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction
        new_position_x = (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH
        new_position_y = (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_position_x, new_position_y)
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()

    def grow(self, amount=1):
        """Увеличивает длину змейки."""
        self.length += amount

    def draw(self, progress=1):
        """Отрисовывает мультяшную змею."""
        for index, position in enumerate(self.positions):
            x, y = position

            if index < len(self.previous_positions):
                previous_x, previous_y = self.previous_positions[index]
                delta_x = x - previous_x
                delta_y = y - previous_y

                if delta_x > SCREEN_WIDTH // 2:
                    delta_x -= SCREEN_WIDTH
                elif delta_x < -SCREEN_WIDTH // 2:
                    delta_x += SCREEN_WIDTH

                if delta_y > SCREEN_HEIGHT // 2:
                    delta_y -= SCREEN_HEIGHT
                elif delta_y < -SCREEN_HEIGHT // 2:
                    delta_y += SCREEN_HEIGHT

                x = (previous_x + delta_x * progress) % SCREEN_WIDTH
                y = (previous_y + delta_y * progress) % SCREEN_HEIGHT

            if index > 0:
                wave = sin(pg.time.get_ticks() / 100 - index * 0.65) * 4

                if self.direction in (LEFT, RIGHT):
                    y += wave
                else:
                    x += wave

            x = round(x)
            y = round(y)

            rect = pg.Rect(x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2)
            pg.draw.rect(screen, self.body_color, rect, border_radius=7)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1, border_radius=7)

            if index == 0:
                self.draw_head(x, y)
            else:
                pg.draw.circle(screen, (80, 130, 200), (x + 6, y + 6), 2)

    def draw_head(self, x, y):
        """Отрисовывает голову и глаза змеи."""
        head_rect = pg.Rect(x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2)
        pg.draw.rect(screen, (60, 105, 185), head_rect, border_radius=8)
        pg.draw.rect(screen, BORDER_COLOR, head_rect, 1, border_radius=8)

        if self.direction == RIGHT:
            eyes = [(x + 13, y + 6), (x + 13, y + 14)]
        elif self.direction == LEFT:
            eyes = [(x + 6, y + 6), (x + 6, y + 14)]
        elif self.direction == UP:
            eyes = [(x + 6, y + 6), (x + 14, y + 6)]
        else:
            eyes = [(x + 6, y + 14), (x + 14, y + 14)]

        for eye in eyes:
            pg.draw.circle(screen, (255, 255, 255), eye, 3)
            pg.draw.circle(screen, (15, 20, 35), eye, 1)

    def update_direction(self, next_direction):
        """Обновляет направление движения змеи."""
        if next_direction:
            self.direction = next_direction

    def reset(self):
        """Сбрасывает состояние змеи после столкновения."""
        self.length = 1
        self.positions = [(20, 240)]
        self.previous_positions = self.positions.copy()
        self.direction = choice([UP, DOWN, LEFT, RIGHT])


def draw_background():
    """Отрисовывает фон игрового поля и звёзды."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    for star in STARS:
        pg.draw.circle(screen, (150, 200, 255), star, 1)


def draw_score(font, speed, score, best_score):
    """Рисует панель со скоростью и счётом."""
    panel = pg.Surface((SCORE_PANEL_WIDTH, SCORE_PANEL_HEIGHT), pg.SRCALPHA)
    panel_rect = panel.get_rect()

    pg.draw.rect(panel, (10, 20, 40, 205), panel_rect, border_radius=12)
    pg.draw.rect(panel, (70, 190, 220, 230), panel_rect, 2, border_radius=12)

    title_font = pg.font.Font(None, 18)
    title_text = "SNAKE  /  SCORE"
    wave_time = pg.time.get_ticks() / 250
    title_x = 14

    for index, letter in enumerate(title_text):
        letter_image = title_font.render(letter, True, (110, 220, 245))
        wave_y = 9 + int(sin(wave_time + index * 0.6) * 2)
        panel.blit(letter_image, (title_x, wave_y))
        title_x += letter_image.get_width()

    pg.draw.line(
        panel,
        (55, 125, 165, 220),
        (12, 29),
        (SCORE_PANEL_WIDTH - 12, 29),
        1
    )

    label_color = (145, 195, 225)
    number_color = (80, 205, 235)
    value_font = pg.font.Font(None, 25)

    now = pg.time.get_ticks()

    if not hasattr(draw_score, "previous_score"):
        draw_score.previous_score = score
        draw_score.score_changed_at = now - 300
    elif score != draw_score.previous_score:
        draw_score.previous_score = score
        draw_score.score_changed_at = now

    elapsed = now - draw_score.score_changed_at

    if elapsed < 300:
        progress = elapsed / 300
        score_scale = 1.1 + 0.15 * (1 - progress)
        score_color = ((220, 250, 255) if elapsed < 100 else number_color)
    else:
        score_scale = 1.1
        score_color = number_color

    panel.blit(font.render("Speed:", True, label_color), (14, 37))
    panel.blit(font.render("Score:", True, label_color), (14, 60))
    panel.blit(font.render("Best:", True, label_color), (14, 83))

    def draw_wavy_value(value, color, x, y, phase=0, scale=1):
        """Рисует число, слегка покачивая каждую цифру."""
        cursor_x = x

        for index, digit in enumerate(str(value)):
            digit_image = value_font.render(digit, True, color)

            if scale != 1:
                digit_size = (
                    int(digit_image.get_width() * scale),
                    int(digit_image.get_height() * scale)
                )
                digit_image = pg.transform.smoothscale(digit_image, digit_size)

            digit_y = y - (
                digit_image.get_height() - value_font.get_height()
            ) // 2
            digit_y += int(sin(wave_time + phase + index * 0.6) * 2)

            panel.blit(digit_image, (cursor_x, digit_y))
            cursor_x += digit_image.get_width()

    draw_wavy_value(speed, number_color, 82, 35)
    draw_wavy_value(best_score, number_color, 82, 81)
    draw_wavy_value(score, score_color, 82, 60, phase=0.6, scale=score_scale)
    screen.blit(panel, (5, 5))


def draw_eat_effect(position, progress):
    """Отрисовывает вспышку и частицы при поедании яблока."""
    x, y = position
    center_x = x + GRID_SIZE // 2
    center_y = y + GRID_SIZE // 2

    radius = 4 + int(22 * progress)
    alpha_color = (255, 220, 80)

    pg.draw.circle(screen, alpha_color, (center_x, center_y), radius, 2)

    for index in range(10):
        angle = 2 * pi * index / 10
        distance = 5 + 25 * progress
        particle_x = int(center_x + cos(angle) * distance)
        particle_y = int(center_y + sin(angle) * distance)

        pg.draw.circle(
            screen,
            (255, 170, 50),
            (particle_x, particle_y),
            max(1, 3 - int(2 * progress))
        )


def draw_watermelon_eat_effect(position, progress):
    """Отрисовывает красно-зелёную вспышку при съедании арбуза."""
    x, y = position
    center_x = x + GRID_SIZE // 2
    center_y = y + GRID_SIZE // 2

    radius = 5 + int(26 * progress)

    pg.draw.circle(screen, (70, 210, 100), (center_x, center_y), radius, 3)
    pg.draw.circle(
        screen, (245, 75, 90),
        (center_x, center_y), max(2, radius // 2), 2
    )

    for index in range(12):
        angle = 2 * pi * index / 12
        distance = 7 + 30 * progress
        particle_x = int(center_x + cos(angle) * distance)
        particle_y = int(center_y + sin(angle) * distance)
        color = (245, 75, 90) if index % 2 == 0 else (100, 210, 90)

        pg.draw.circle(
            screen,
            color,
            (particle_x, particle_y),
            max(1, 4 - int(3 * progress))
        )


def draw_scene(
        snake, apple, watermelon, watermelon_active,
        rock, font, score, best_score
):
    """Полностью перерисовывает поле при запуске или сбросе."""
    draw_background()
    draw_score(font, snake.speed, score, best_score)
    rock.draw()
    snake.draw()
    apple.draw()
    if watermelon_active:
        watermelon.draw()
    pg.display.update()


def draw_fireworks(elapsed):
    """Рисует повторяющийся салют по краям экрана."""
    colors = [
        (80, 205, 235),
        (255, 100, 125),
        (255, 210, 80),
        (120, 230, 140),
        (190, 130, 255),
    ]

    bursts = [
        (100, 150, 0),
        (740, 150, 450),
        (100, 470, 900),
        (740, 470, 1350),
    ]

    for center_x, center_y, delay in bursts:
        if elapsed < delay:
            continue

        burst_time = (elapsed - delay) % 2200
        if burst_time >= 850:
            continue

        progress = burst_time / 850
        radius = 8 + 72 * progress

        for index in range(28):
            angle = 2 * pi * index / 28
            distance = radius * (0.75 + (index % 7) * 0.04)
            end_x = int(center_x + cos(angle) * distance)
            end_y = int(center_y + sin(angle) * distance + 24 * progress ** 2)

            tail_distance = max(0, distance - 12)
            start_x = int(center_x + cos(angle) * tail_distance)
            start_y = int(
                center_y + sin(angle) * tail_distance
                + 24 * progress ** 2
            )

            color = colors[index % len(colors)]
            brightness = max(0.2, 1 - progress)
            dim_color = tuple(
                int(channel * brightness * 0.65)
                for channel in color
            )

            pg.draw.line(
                screen,
                dim_color,
                (start_x, start_y),
                (end_x, end_y),
                2
            )
            pg.draw.circle(
                screen,
                color,
                (end_x, end_y),
                max(1, int(4 * (1 - progress)))
            )

        if progress < 0.12:
            pg.draw.circle(
                screen,
                (255, 255, 220),
                (center_x, center_y),
                8
            )


def show_game_over(
    snake, apple, watermelon, watermelon_active,
    rock, font, score, best_score, new_record
):
    """Показывает экран проигрыша до нажатия кнопки."""
    start_time = pg.time.get_ticks()
    music_folder = Path(__file__).parent / "sounds"
    music_file = "WIN.mp3" if new_record else "game_over.mp3"
    music_path = music_folder / music_file

    if not music_path.exists():
        music_path = music_folder / "game_over.mp3"

    pg.mixer.music.load(str(music_path))
    pg.mixer.music.set_volume(0.35)
    pg.mixer.music.play(loops=-1)
    overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
    overlay.fill((4, 9, 24, 155))

    title_font = pg.font.SysFont("Arial", 36, bold=True)
    message_font = pg.font.SysFont("Arial", 25)
    button_font = pg.font.SysFont("Arial", 24, bold=True)

    card = pg.Rect(0, 0, 520, 180)
    card.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    button_rect = pg.Rect(0, 0, 220, 46)
    button_rect.center = (card.centerx, card.centery + 50)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.mixer.music.stop()
                pg.quit()
                raise SystemExit

            if (
                event.type == pg.MOUSEBUTTONDOWN
                and event.button == 1
                and button_rect.collidepoint(event.pos)
            ):
                pg.mixer.music.stop()
                return

        elapsed = pg.time.get_ticks() - start_time

        draw_background()
        draw_score(font, snake.speed, score, best_score)
        rock.draw()
        snake.draw()
        apple.draw()

        if watermelon_active:
            watermelon.draw()

        screen.blit(overlay, (0, 0))

        draw_fireworks(elapsed)

        pg.draw.rect(screen, (10, 24, 48), card, border_radius=18)
        pg.draw.rect(screen, (70, 190, 220), card, 2, border_radius=18)

        if new_record:
            title_text = "Новый рекорд!"
            title_color = (255, 210, 80)
            last_two_digits = score % 100
            last_digit = score % 10

            if 11 <= last_two_digits <= 14:
                points_word = "очков"
            elif last_digit == 1:
                points_word = "очко"
            elif 2 <= last_digit <= 4:
                points_word = "очка"
            else:
                points_word = "очков"

            message_text = (
                f"Поздравляем! Новый рекорд — {score} {points_word}!"
            )
        else:
            title_text = "Проигрыш :("
            title_color = (255, 125, 145)
            message_text = "Повезет в следующий раз!"

        title = title_font.render(title_text, True, title_color)
        title_rect = title.get_rect(center=(card.centerx, card.centery - 55))
        screen.blit(title, title_rect)

        message = message_font.render(message_text, True, (170, 220, 240))
        message_rect = message.get_rect(
            center=(card.centerx, card.centery - 12)
        )
        screen.blit(message, message_rect)

        mouse_position = pg.mouse.get_pos()
        if button_rect.collidepoint(mouse_position):
            button_color = (65, 175, 210)
        else:
            button_color = (35, 115, 160)

        pg.draw.rect(
            screen,
            button_color,
            button_rect,
            border_radius=12
        )
        pg.draw.rect(screen, (145, 225, 245), button_rect, 2, border_radius=12)

        button_text = button_font.render("Начать игру!", True, (240, 250, 255))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        screen.blit(button_text, button_text_rect)

        pg.display.flip()
        clock.tick(60)


def main():
    """Запускает основной игровой цикл."""
    font = pg.font.Font(None, 21)
    snake = Snake()
    apple = Apple(snake.positions)
    watermelon = Watermelon(snake.positions + [apple.position])
    rock = Rock(
        snake.positions
        + [apple.position, watermelon.position]
        + snake.get_danger_zone()
    )
    last_rock_move = pg.time.get_ticks()
    last_move_time = pg.time.get_ticks()
    score = 0
    new_record = False
    best_score = 0
    eat_effect_start = None
    eat_effect_position = None
    watermelon_eat_effect_start = None
    watermelon_eat_effect_position = None
    watermelon_active = False
    draw_scene(
        snake, apple, watermelon, watermelon_active,
        rock, font, score, best_score
    )
    queued_direction = None

    while True:
        clock.tick(60)
        current_time = pg.time.get_ticks()
        pressed_direction = handle_keys(
            snake,
            direction_is_queued=queued_direction is not None
        )
        if pressed_direction is not None:
            queued_direction = pressed_direction

        ate_apple = False
        ate_watermelon = False
        move_interval = 1000 // snake.speed

        if current_time - last_move_time >= move_interval:
            if queued_direction is not None:
                snake.update_direction(queued_direction)
                queued_direction = None

            snake.move()
            last_move_time = current_time

            ate_apple = snake.get_head_position() == apple.position
            ate_watermelon = (
                watermelon_active
                and snake.get_head_position() == watermelon.position
            )

        if ate_apple:
            eat_effect_position = apple.position
            eat_effect_start = current_time

            APPLE_EAT_SOUND.play()

            snake.grow()
            score += 1

            apple.randomize_position(
                snake.positions
                + [rock.position, watermelon.position]
                + snake.get_danger_zone()
            )

            if not watermelon_active and randint(1, 5) == 1:
                watermelon.respawn(
                    snake.positions
                    + [apple.position, rock.position]
                    + snake.get_danger_zone()
                )
                watermelon_active = True

        if ate_watermelon:
            watermelon_eat_effect_position = watermelon.position
            watermelon_eat_effect_start = current_time

            WATERMELON_EAT_SOUND.play()

            snake.grow(2)
            score += 1
            watermelon_active = False

        progress = min((current_time - last_move_time) / move_interval, 1)

        if current_time - last_rock_move > 5000:
            occupied_positions = (
                snake.positions
                + [apple.position, watermelon.position]
                + snake.get_danger_zone()
            )
            rock.respawn(occupied_positions)
            last_rock_move = current_time

        if score > best_score:
            best_score = score
            new_record = True
        collided = (
            snake.get_head_position() in snake.positions[1:]
            or snake.get_head_position() == rock.position
        )

        if collided:
            CRASH_SOUND.play()

            show_game_over(
                snake,
                apple,
                watermelon,
                watermelon_active,
                rock,
                font,
                score,
                best_score,
                new_record
            )

            new_record = False
            score = 0
            snake.reset()
            watermelon_active = False

            apple.randomize_position(
                snake.positions + [rock.position, watermelon.position]
            )

            last_rock_move = current_time
            last_move_time = current_time

            draw_scene(
                snake,
                apple,
                watermelon,
                watermelon_active,
                rock,
                font,
                score,
                best_score
            )
            continue

        draw_background()
        draw_score(font, snake.speed, score, best_score)
        rock.draw()
        snake.draw(progress)
        apple.draw()
        if watermelon_active:
            watermelon.draw()

        if eat_effect_start is not None:
            elapsed = current_time - eat_effect_start
            effect_progress = elapsed / EAT_EFFECT_DURATION

            if effect_progress < 1:
                draw_eat_effect(eat_effect_position, effect_progress)
            else:
                eat_effect_start = None
                eat_effect_position = None

        if watermelon_eat_effect_start is not None:
            elapsed = current_time - watermelon_eat_effect_start
            effect_progress = elapsed / EAT_EFFECT_DURATION

            if effect_progress < 1:
                draw_watermelon_eat_effect(
                    watermelon_eat_effect_position,
                    effect_progress
                )
            else:
                watermelon_eat_effect_start = None
                watermelon_eat_effect_position = None

        pg.display.update()


def handle_keys(game_object, direction_is_queued=False):
    """Обрабатывает действия пользователя с клавиатуры."""
    next_direction = None

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit

        if event.type != pg.KEYDOWN:
            continue

        is_speed_key = event.key in (SPEED_UP_KEY, SPEED_DOWN_KEY)

        if is_speed_key:
            handle_keydown(event, game_object)
        elif not direction_is_queued and next_direction is None:
            next_direction = handle_keydown(event, game_object)

    return next_direction


def handle_keydown(event, game_object):
    """Обрабатывает нажатие клавиши."""
    if event.key == SPEED_DOWN_KEY:
        if game_object.speed <= 1:
            return None
        game_object.speed -= 1
        return None

    if event.key == SPEED_UP_KEY:
        if game_object.speed >= 20:
            return None
        game_object.speed += 1
        return None

    if event.key == pg.K_UP and game_object.direction != DOWN:
        return UP
    if event.key == pg.K_DOWN and game_object.direction != UP:
        return DOWN
    if event.key == pg.K_LEFT and game_object.direction != RIGHT:
        return LEFT
    if event.key == pg.K_RIGHT and game_object.direction != LEFT:
        return RIGHT

    return None


if __name__ == '__main__':
    main()
