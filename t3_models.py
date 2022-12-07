"""
T3_models
Модель данных учета состояния текущего раунда игры и результатов серии игр
(состояние, конфигурация игрового поля, данные игроков, статистика игр)
"""
from gis import color_space, color_X, color_O

# Глобальные константы модуля---------------:
# Виды игроков. Используемые игровые символы
SIGNS = {0: '', 1: 'X', 2: 'O'}
SIGNS_synonyms = {'X': 'XxЧч{[Хх', 'O': 'OoЩщJjОо'}
SIGNS_color = (color_space, color_X, color_O)
PLAYER_one, PLAYER_two = 1, 2                                   # Номера игроков

# Конфигурация игрового поля и его размещения на экране
SIZE_BOARD = 3                                                  # размер поля
size_min, size_max = 3, 8                                       # возможное число ячеек стороны (размеры игры N x N)
numb_XO    = 3                                                  # выигрышная длина "X" или "O"
BOARD_STATE = [[0] * SIZE_BOARD for _ in range(SIZE_BOARD)]     # Состояние на игровом поле


# Инициализация / обновление конфигурации игры (не путать с параметрами игры)
def init_configuration(size_new, numb_XO_new):
    global SIGNS
    global SIGNS_synonyms
    global SIGNS_color
    global PLAYER_one
    global PLAYER_two
    global SIZE_BOARD
    global BOARD_STATE
    global numb_XO
    global size_min
    global size_max
    SIGNS = SIGNS
    SIGNS_synonyms = SIGNS_synonyms
    SIGNS_color = SIGNS_color
    PLAYER_one, PLAYER_two = PLAYER_one, PLAYER_two
    size_min, size_max = size_min, size_max
    SIZE_BOARD = size_new                                           # размер поля
    numb_XO    = numb_XO_new                                        # выигрышная длина "X" или "O"
    BOARD_STATE = [[0] * SIZE_BOARD for _ in range(SIZE_BOARD)]     # Состояние на игровом поле

    return SIZE_BOARD, numb_XO, BOARD_STATE     # Пока возвращаем те, что в данной версии программы могут быть изменены


# Навигационные границы игрового поля
#   На вход получает: левая граница поля, размер ячейки поля,
#                     размер поля (по числу ячеек) по интересующей оси
#   Возвращает: координаты крайних левой / правой ячеек, начальное положение,
#               расстояние между соседними ячейками, размер зоны статистики
#   Пример использования: x, x_min, x_max, x_d = set_nav(X0, CELL_x, SIZE_BOARD)
def set_nav(c0, cell_s, cell_cnt):
    c = c0 + int((cell_s + 1) / 2)
    return c, c, c0 + int((cell_s + 1) * (cell_cnt - 0.5)), cell_s + 1


# Получение аттрибутов игроков.
#   Принимает на вход параметры игрока (code, pin)
#   Возвращает pin_code, symbols или COLOR первого и второго игрока в виде кортежа
def get_players_attr(player, ret=None):

    player_cod, player_pin = player
    player_symbol, player_color = SIGNS[player_pin], SIGNS_color[player_pin]
    player_other_pin = sum(SIGNS.keys()) - player_pin
    player_other_symbol, player_other_color = SIGNS[player_other_pin], SIGNS_color[player_other_pin]

    return_this, return_other = (player_pin, player_other_pin) if ret is None else \
                                (player_symbol, player_other_symbol) if ret == 'SYMBOL' else \
                                (player_color, player_other_color)

    return (return_this, return_other) if player_cod == PLAYER_one else (return_other, return_this)


# Доступные ячейки игрового поля
def get_av_moves(board_s):
    coordinates = [10 * ell + el for ell in range(1, SIZE_BOARD + 1) for el in range(1, SIZE_BOARD + 1)]
    return tuple(filter(lambda m: not board_s[m // 10 - 1][m % 10 - 1], coordinates))
