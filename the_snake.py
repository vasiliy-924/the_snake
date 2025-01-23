from random import choice, randint

import pygame as pg

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

# Словарь для определения возможных направлений
DIRECTION_MAP = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 15

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка. z(-), x(+) для смена скорости. Esc для выхода')

# Настройка времени:
clock = pg.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс, от которого наследуются другие игровые объекты."""

    def __init__(self, body_color=None) -> None:
        """Инициализирует базовые атрибуты объекта: позици и цвет."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """
        Абстрактный метод для переопределения в дочерних классах.
        Этот метод определяет, как объект будет отрисовываться на экране.
        """
        raise NotImplementedError('Метод draw() должен быть переопределен.')

    def draw_cell(self, position, color, border_color=None):
        """Отрисовывает прямоугольник с указанной позицией и цветом."""
        rect = (pg.Rect(position, (GRID_SIZE, GRID_SIZE)))
        pg.draw.rect(screen, color, rect)
        if border_color:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Описывает змейку и ее поведение.
    Этот класс управляет ее движением, отрисовкой,
    а также отрабатывает действия пользователя.
    """

    def __init__(self, body_color: str = SNAKE_COLOR):
        """Инициализирует начальное состояние змейки."""
        super().__init__(body_color)
        self.reset()
        self.direction = RIGHT

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки: голову и хвост."""
        head_x, head_y = self.get_head_position()
        move_x, move_y = self.direction
        self.position = ((head_x + move_x * GRID_SIZE) % SCREEN_WIDTH,
                         (head_y + move_y * GRID_SIZE) % SCREEN_HEIGHT)

        self.positions.insert(0, self.position)
        if len(self.positions) > self.lenth:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает голову змейки и затирает хвост."""
        # Отрисовка головы змейки
        self.draw_cell(self.get_head_position(), self.body_color, BORDER_COLOR)

        # Затирание последнего сегмента
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.lenth = 1
        self.direction = choice([UP, LEFT, DOWN, RIGHT])
        self.next_direction = None


class Apple(GameObject):
    """Описывает яблоко и действия с ним."""

    def __init__(self, body_color: str = APPLE_COLOR, taken_positions=None):
        """Задает цвет яблока и инициализирует его в случайное положение."""
        super().__init__(body_color)
        self.taken_positions = taken_positions or []
        self.randomize_position(self.taken_positions)

    def randomize_position(self, taken_positions):
        """Устанавливает случайное положение яблока на игровом поле."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in taken_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self.draw_cell(self.position, self.body_color, BORDER_COLOR)


def handle_keys(game_object):
    """Отрабатывает действия пользователя."""
    global SPEED
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return False
            elif event.key == pg.K_z:
                SPEED = max(1, SPEED - 1)
            elif event.key == pg.K_x:
                SPEED += 1
            # Обновление направления с помощью словаря.
            if (game_object.direction, event.key) in DIRECTION_MAP and \
                    DIRECTION_MAP[(
                        game_object.direction,
                        event.key
                    )] != game_object.direction:
                game_object.next_direction = DIRECTION_MAP[(
                    game_object.direction, event.key
                )]


def display_message(text, size, color, position):
    """Выводит сообщение о победе."""
    font = pg.font.SysFont("Arial", size)  # Выбираем шрифт и размер
    text_surface = font.render(text, True, color)  # Рендерим текст
    screen.blit(text_surface, position)  # Отображаем текст на экране


def main():
    """Обновляет состояние объектов."""
    # Инициализация PyGame:
    pg.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple(taken_positions=snake.positions)

    while True:
        clock.tick(SPEED)
        if handle_keys(snake) is False:
            break
        snake.update_direction()
        snake.move()

        # Проверка на выигрыш
        if len(snake.positions) >= (GRID_WIDTH * GRID_HEIGHT):
            screen.fill(BOARD_BACKGROUND_COLOR)  # Очистить экран
            display_message("Поздравляем, вы выиграли!",
                            36, (255, 255, 255),
                            (SCREEN_WIDTH // 4,
                             SCREEN_HEIGHT // 2)
                            )
            pg.display.update()  # Обновить экран
            pg.time.wait(2000)  # Задержка, чтобы игрок успел увидеть сообщение
            break  # Врядли игрок захочет играть снова после долгой игры

        if snake.get_head_position() == apple.position:
            snake.lenth += 1
            apple.randomize_position(snake.positions)

        elif snake.get_head_position() in snake.positions[1:snake.lenth]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()

        pg.display.update()


if __name__ == '__main__':
    main()
