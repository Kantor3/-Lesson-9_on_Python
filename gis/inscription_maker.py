"""
Inscription_maker.
Модуль для вывода различных надписей в игровой зоне:
 -  текущие результаты
 - статистика
 - комментарии
"""
from gis import color_board, color_round, bolt, normal, color_acc_draw, \
                color_account, under, color_acc_total, color_comment, \
                italics, color_norm, color_set, color_mark, color_reset
from gis.view_ext import screen_preparation
from gis.view_ext import CELL_x, CELL_y, pynput_print, X0, Y0
import gis.view_ext as v
from t3_models import get_players_attr, set_nav
from t3_models import SIGNS_color
import t3_models as m

from functools import reduce

# Общие константы
spaces_grout = ' ' * len('-> Игрок-1 "x"    ')


# Отрисовка игрового поля
# Входные параметры: board_s - состояние игры на игровом поле
# (в виде массива N x N - структура массива список в списке)
def drawing_board(board_s):

    offset = lambda cell_s, ofs: int((cell_s + 1) * (ofs + 0.5))

    # Определяем элементы "графики" игрового поля
    line_border = f"+{'-' * CELL_x}" * m.SIZE_BOARD + '+'
    line_cell = f"|{' ' * CELL_x}" * m.SIZE_BOARD + '|' * CELL_y

    # Рисуем игровое поле
    for i in range(m.SIZE_BOARD):
        goto = X0, Y0 + (CELL_y + 1) * i
        pynput_print(f'{color_board}{line_border}', f'{color_board}{line_cell}', sep='\n', goto=goto)
    goto = X0, Y0 + (CELL_y + 1) * m.SIZE_BOARD
    pynput_print(f'{line_border}', goto=goto)

    # Выводим текущую расстановку игры
    board_sign = reduce(lambda lel, el: lel + [list(map(lambda l_el: m.SIGNS[abs(l_el)], el))], board_s, [])
    for i in range(0, m.SIZE_BOARD):
        y = Y0 + offset(CELL_y, i)
        for j in range(0, m.SIZE_BOARD):
            sign = board_s[i][j]
            sign_curr = board_sign[i][j]
            sign_color = SIGNS_color[abs(sign)]
            x = X0 + offset(CELL_x, j)
            if sign < 0:
                pynput_print(f'{sign_color}{color_mark}{bolt} {sign_curr} {color_reset}', goto=(x-1, y))
            else:
                pynput_print(f'{sign_color}{sign_curr}{color_reset}', goto=(x, y))


# Вывод текущей игровой информации ("чей ход", параметры этого игрока) - игра не окончена
def show_order_move(n_round, winners):
    winner_cod, winner_pin = winners
    color_win = SIGNS_color[winner_pin]
    text_round = f'{color_round}Ход -> {color_win}Игрок-{winner_cod} ' \
                 f'"{bolt}{m.SIGNS[winner_pin]}"{spaces_grout}{normal} '
    goto = X0, Y0 - 1
    pynput_print(f'{color_round}Раунд {n_round}. ', text_round, goto=goto)


# Вывод информации о результатах текущего раунда игры
def show_statistic(n_round, winners, result):

    player, wins_1, wins_2 = winners

    # Результаты текущего раунда игры
    if result:                                                              # есть победитель в текущей игре
        winner_cod, winner_pin = player
        color_win = SIGNS_color[winner_pin]
        text_round = f'{color_round}Победитель: {color_win}Игрок-{winner_cod} ' \
                     f'"{bolt}{m.SIGNS[winner_pin]}"{spaces_grout}{normal}'
    else:                                                                   # НИЧЬЯ (победителей нет)
        text_round = f'{color_acc_draw}НИЧЬЯ{spaces_grout}{normal}'
    goto = X0, Y0 - 1
    pynput_print(f'{color_round}Раунд {n_round}. ', text_round, goto=goto)

    #  Статистика игр
    color_one, color_two = get_players_attr(player, ret='COLOR')
    _, _, axis_x, _ = set_nav(X0, CELL_x, m.SIZE_BOARD)
    goto = axis_x + 7, Y0 + 1
    pynput_print(f'{color_account}{under}Статистика выигрышей:{normal}',
                 f'{color_account}Сыграно партий - {bolt}{color_acc_total}{n_round}{normal}',
                 f'{color_account}Побед: {color_one}Игрок-1 - {wins_1}',
                 f'{color_account}       {color_two}Игрок-2 - {wins_2}',
                 f'{color_account}Ничьих         - {color_acc_draw}{n_round - wins_1 - wins_2}',
                 sep='\n', goto=goto
                 )


# Вывод текущих игровых настроек
def show_settings(n_round, my_attr):
    pos_X = v.pos_question[0]
    goto = pos_X, Y0 + 1
    my_cod, my_sign = my_attr
    pynput_print(f'{color_account}{under}Игровые настройки {n_round + 1}-го раунда игры:{normal}',
                 f'{color_account}Размер доски - {color_set}{m.SIZE_BOARD}{normal}',
                 f'{color_account}Длина выигрышной комбинации - {color_set}{m.numb_XO}{normal}',
                 f'{color_account}Вы Игрок {color_set}№{my_cod}{normal}',
                 f'{color_account}Ваш игровой символ - {color_set}"{m.SIGNS[my_sign]}"{normal}',
                 sep='\n', goto=goto
                 )


# Вывод комментариев (краткая инструкция к игре)
def show_comment():
    _, _, axis_y, _ = set_nav(Y0, CELL_y, m.SIZE_BOARD)
    goto = X0, axis_y + 3
    pynput_print(f'{color_comment}{italics}Двигайтесь по полю, используя стрелки.{normal}',
                 f'{color_comment}{italics}'
                 f'Установить крестик/нолик - [Пробел]: Убрать - [Пробел] / [Del] '
                 f'(пока не нажат [Enter]); Завершить ход - [Enter]. '
                 f'Выйти из игры - [Esc]...{normal}{color_norm}', sep='\n', goto=goto
                 )


# Вывод текущего состояния игры:
# Игра не окончена  ->  N-й раунд. Ход - Игрок-[1/2] ([X/O]) ...
# Игра завершена    ->  [3]-й Раунд. Победил: Игрок-[1/2]
# Вх. параметры:    n_round - раунд;
#                   winners -> (winner, wins_1, wins_2) данные текущего игрока, победы 1-го, 2-го игрока, соответственно
#                               winner -> (код игрока, код игрового значка)
#                               если игра не окончена - wins_1 и wins_2 -> отсутствуют, т.е. wins_pl = winner
#                   game_board -> статус игры (в виде массива N x N - структура массива список в списке);
def drawing_inscriptions(n_round, game_board, winners, result=None, my_attr=None):

    if not (result is None):
        screen_preparation()
        show_statistic(n_round, winners, result)    # Результат тек. игры + Статистика игр
        show_settings(n_round, my_attr)             # Настройки игры

    drawing_board(game_board)                       # Отразить тек. состояние игры на поле

    if not isinstance(result, int):
        show_order_move(n_round, winners)           # Чей ход
    show_comment()
