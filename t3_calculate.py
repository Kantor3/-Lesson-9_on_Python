"""
T3_calculate
Вычисления. Определения победителя или НИЧЬЯ.
"""
import copy
from functools import reduce
import t3_models as m
from gis.inscription_maker import drawing_board
from utilities import trans_ll


# Выигравший символ (код), было: cod_win = get_cod(stat, str_cod(numb))
def get_cod(st, number):
    s_cod = str(list(m.SIGNS.keys())[number]) * m.numb_XO
    to_line = lambda el: ''.join(map(str, el))
    return [(i, to_line(st[i]).find(s_cod) ) for i, el in enumerate(st) if s_cod in to_line(el)]


# выделение элементов, находящихся на диагоналях вложенного списка
def diagonals(st, brd, sl):
    cnt_d = m.SIZE_BOARD - m.numb_XO + 1
    if brd == 1:                                    # Диагонали начинаются с верхней границы поля
        if sl == 1:                                 # наклон - левый
            res = reduce(lambda st_d, j: st_d + [[st[i - j][i] for i in range(j, m.SIZE_BOARD)]],
                         range(0, cnt_d, 1), [])
        else:                                       # наклон - правый (if sl == 2)
            res = reduce(lambda st_d, j: st_d + [[st[i - j][(m.SIZE_BOARD - 1) - i] for i in range(j, m.SIZE_BOARD)]],
                         range(0, cnt_d, 1), [])
    else:                                           # Диагонали заканчиваются на нижней границе поля (if brd == 2)
        if sl == 1:                                 # наклон - левый
            res = reduce(lambda st_d, j: st_d + [[st[i][(j + i)] for i in range(-j, m.SIZE_BOARD)]],
                         range(0, -cnt_d, -1), [])
        else:                                       # наклон - правый (if sl == 2)
            res = reduce(
                lambda st_d, j: st_d + [[st[i][(m.SIZE_BOARD - 1) - (j + i)] for i in range(-j, m.SIZE_BOARD)]],
                range(0, -cnt_d, -1), [])
    return res


# Организация вложенных циклов, обеспечивающая возможность выхода из всех циклов разом
def multi_for(*ins):
    in1, in2, in3 = ins
    for i in in1:
        for j in in2:
            for k in in3: yield i, j, k


# Маркировка выигранной диагонали в массиве
def marking_diagonal(st, cod_win,  brd, sl):
    marked_st = copy.deepcopy(st)
    dg, of = cod_win
    ofs_i = of + (0 if brd == 1 else dg)
    for i in range(m.numb_XO):
        i = i + ofs_i
        j = (i + (dg if brd == 1 else -dg)) * (1 if sl == 1 else -1) - (1 if sl == 2 else 0)
        marked_st[i][j] = -marked_st[i][j]
    return marked_st


# Маркировка выигравшей линии в массиве (маркировка производится негативом)
#   T - признак "Транспонирование":
#       - 1 - не транспонировать
#       - 2 - транспонировать
def marking_line(st, cod_win, T):
    rw, cl = cod_win
    mark_line = lambda ell, frm: [-el if frm + m.numb_XO > i > frm - 1 else el for i, el in enumerate(ell)]
    marked_st = [mark_line(el, cl) if i == rw else el for i, el in enumerate(st)]
    return trans_ll(marked_st) if T == 2 else marked_st


# Проверить игру на завершение (выигрыш одного из игроков или ничья)
# Выигрыш - наличия numb_XO идущих подряд ('x' или '0') по горизонтали, вертикали или на диагоналях
# Ничья - если нет выигрыша и все поля заняты
# Возврат:
# - None - если игра не завершена
# - 0 - если ничья
# - № игрока, который выиграл, если на доске есть выигрыш
def is_winnings(board_st):

    cycle = 1, 2

    # Проверяем наличие выигрышных фрагментов на горизонталях и вертикалях
    # for board, numb, _ in multi_for((1, 2), (1, 2), (None, None)):
    for board, numb, _ in multi_for(cycle, cycle, (None, None)):
        stat = (board_st, trans_ll(board_st))[board-1]
        cod_win = get_cod(stat, numb)
        if cod_win:
            board_st_mark = marking_line(stat, cod_win[0], board)
            return 1, board_st_mark             # Выигрыш текущего игрока
    else:
        # Проверяем наличие выигрышного фрагмента на диагоналях
        drawing_board(board_st)
        for board, slash, numb in multi_for(cycle, cycle, cycle):
            stat = diagonals(board_st, board, slash)
            cod_win = get_cod(stat, numb)
            if cod_win:
                board_st_mark = marking_diagonal(board_st, cod_win[0],  board, slash)
                return 1, board_st_mark         # Выигрыш текущего игрока
        else:
            # Проверяем наличие на доске ничьи
            if not list(filter(lambda el: not el, [ell for el in board_st for ell in el])):
                return 0, None                  # на доске ничья

    return None, None                           # Нет результата (игра не окончена)
