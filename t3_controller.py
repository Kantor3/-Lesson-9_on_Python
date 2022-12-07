"""
T3_controller
Управление и контроль процессами игры
"""
from utilities import dict_rev

from gis.engine import game_engine
from gis.inscription_maker import drawing_inscriptions, drawing_board, show_set_settings
from gis.view_ext import init_view, user_interaction, set_parameter, welcome_game
import gis.view_ext as v
from t3_calculate import is_winnings
import t3_models as m                                                       # доступ к изменяемым переменным модуля
from t3_models import init_configuration, get_av_moves                      # процедуры модуля
from t3_models import PLAYER_one, PLAYER_two, SIGNS, size_min, size_max     # неизменяемые переменные модуля

import random


# Инициализация нового раунда игры
def init_game(size_new, numb_XO_new, player_attr):
    m.SIZE_BOARD, m.numb_XO, m.BOARD_STATE = init_configuration(size_new, numb_XO_new)  # обновление конфигурации
    v.pos_question, v.pos_answer, v.pos_exit = init_view()              # инициализация / обновление интерфейсных зон
    player, sign = player_attr
    player_prime = random.choice((PLAYER_one, PLAYER_two))
    sign_prime = sign if player_prime == player else sum(SIGNS) - sign
    return player_prime, sign_prime


# Задание (настройка) параметров игры
def setting_game(my_attr, area=None):

    show_set_settings()

    my_cod, my_sign = my_attr
    pos_X = v.pos_question[0]
    area = (1, 2, 3, 4) if area is None else area       # при area = None: область редактируемых параметров - Все

    # Уточнение размера доски
    size_accept = (size_min, size_max)
    size = set_parameter(size_accept, m.SIZE_BOARD, 'Размер доски.',
                         pos_X, 2, area=1 in area)
    if size is None: return None

    # Уточнение выигрышной комбинации
    size_accept = (size_min, size)
    numb = set_parameter(size_accept, m.numb_XO, 'Длина выигрышной комбинации.',
                         pos_X, 3, area=2 in area)
    if numb is None: return None

    # Выбрать номер игрока, за которого вы играете ("1" - Игрок-1; "2" - Игрок-2")
    size_accept = tuple(map(str, (my_cod, PLAYER_one + PLAYER_two - my_cod)))
    player = set_parameter(size_accept, str(my_cod), 'Выберите свой номер.        ',
                           pos_X, 4, type_accept=tuple, area=3 in area)
    if player is None: return None
    player = int(player)

    # Выбрать свой значок ("х" иди "о")
    symbols = tuple(SIGNS.values())[-2:]
    symbol = set_parameter(symbols, SIGNS[my_sign], f'Выберите свой символ для игры.',
                           pos_X, 5, type_accept=tuple, area=4 in area)
    if symbol is None: return None
    sign = dict_rev(SIGNS, symbol)

    return size, numb, (player, sign)


# Мастер метод
# TODO: добавить следующий функционалЖ
#       - логирование всех игр - конфигурация игрового поля, ходы (ведение системного журнала)
#       - добавление в качестве игрока - бота со своими "мозгами" функционирующими на базе ИИ
def main():

    # Приветствие. Начинаем?
    if not welcome_game(gre='Добро пожаловать в игру "Крестики - нолики"', que='Сыграем? ("y" - ДА) -> '): return

    # Задание начальных данных игровой серии:
    # TODO: В дальнейшем можно добавить персонализацию игры
    #       new_game = True
    #       player_my, sign_my = None, None
    n_games = 0                                             # Количество сыгранных раундов
    wins_pl1, wins_pl2 = 0, 0                               # Количество выигрышей игроками
    player_my_attr = m.PLAYER_one, [k for k in m.SIGNS][1]  # Мои (игрока) аттрибуты
    area = None                                             # Область редактируемых параметров настройки

    # Цикл серии игр
    while True:

        # Настройка параметров нового раунда игры и ее инициализация
        settings = setting_game(player_my_attr, area=area)
        if not settings: break

        size_board_new, numb_XO_new, player_my_attr = settings
        player_attr = init_game(size_board_new, numb_XO_new, player_my_attr)
        player_curr, sign_curr = player_attr                                    # Запись аттрибутов текущего игрока
        wins_pl = player_attr, wins_pl1, wins_pl2
        drawing_inscriptions(n_games, m.BOARD_STATE, wins_pl,                   # Текущая статистика игр
                             True, my_attr=player_my_attr)
        n_games += 1

        # Цикл текущего раунда игры
        result_move = None
        while True:

            # Запуск игрового движка
            drawing_inscriptions(n_games, m.BOARD_STATE, player_attr)                   # Чей ход
            av_moves = get_av_moves(m.BOARD_STATE)
            result_move = game_engine(sign_curr, m.BOARD_STATE, av_moves, result_move)  # Движок гр. поддержки хода

            if not result_move: break                   # Завершение текущего раунда при отмене (по кл. Esc)
            result = is_winnings(m.BOARD_STATE)         # Определяем результат возможного окончания игры (0, 1, None)
            result_game, board_st_mark = result

            # Обработка результата состояния игры в текущем раунде
            if result_game is None:                                             # игра не окончена
                player_curr = PLAYER_one + PLAYER_two - player_curr             # смена игрока
                sign_curr = sum(SIGNS.keys()) - sign_curr
                player_attr = (player_curr, sign_curr)
                continue

            # По завершении раунда обновляем и выводим его результаты и статистику
            wins_pl1 += 1 if result_game and player_curr == PLAYER_one else 0
            wins_pl2 += 1 if result_game and player_curr == PLAYER_two else 0
            wins_pl = player_attr, wins_pl1, wins_pl2
            drawing_inscriptions(n_games, m.BOARD_STATE, wins_pl,
                                 result_game, my_attr=player_my_attr)           # Изменения на поле. Статистика
            if result_game: drawing_board(board_st_mark)                        # Маркировка линии выигрыша
            break

        # Подтверждение Продолжения игры / Завершения серии игр в крестики-нолики:
        if result_move and not user_interaction(f'Продолжим? ("y" - ДА) -> ',
                                                zone=1, cancel=False, enter=True, not_mess=True): break
        if not result_move and user_interaction(f'Завершить игру? ("y" - ДА) -> ',
                                                zone=1, cancel=False, enter=True): break
        user_interaction(' ' * len('Завершить игру? ("y" - ДА) ->  '), zone=1, active=False)

        area = 1, 2       # Область редактируемых параметров настройки - первые 2-а параметры

    user_interaction('--->', zone=3, active=False)
