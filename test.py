# Тестовый модуль
# TODO: Разложить на пакеты и модули проекта
import os
import random
from functools import reduce
from pynput import keyboard
from queue import Queue
import colorama
from colorama import Fore

from utilities import question, goto_xy, get_input, dict_rev

queue = Queue()
colorama.init()

# Глобальные константы модуля:
# ----------------------------------------------------------------------------------------
# Глобальные константы всего приложения (временно для отладки, размещаем в этом модуле):
SIGNS = {0: '', 1: 'X', 2: 'O'}
SIGNS_synonyms = {'X': 'XxЧч{[Хх', 'O': 'OoЩщJjОо'}
SIGNS_color = (Fore.RESET, Fore.RED, Fore.CYAN)
PLAYER_one, PLAYER_two = 1, 2                               # Номера игроков

# Определяем цвета и другие аттрибуты элементов надписей
color_norm = Fore.RESET
color_cancel = Fore.RED
color_set = Fore.GREEN
color_board = Fore.LIGHTWHITE_EX
color_round = Fore.YELLOW
color_account = Fore.WHITE
color_acc_total = Fore.YELLOW
color_acc_draw = Fore.LIGHTWHITE_EX
color_comment = Fore.WHITE
normal = '\033[0m'
bolt = '\033[1m'
italics = '\033[3m'
under = '\033[4m'

# Параметры игрового поля
X0, Y0 = 10, 2          # координаты левого угла поля
SIZE_BOARD = 3          # размер поля
numb_XO    = 3          # выигрышная длина "X" или "O"
CELL_x, CELL_y = 3, 1   # размер ячейки
INPUT_zone = 96         # длина зоны ввода данных настройки параметров


# Принимает на вход параметры игрока (code, pin)
# Возвращает pin_code, symbols или COLOR первого и второго игрока в виде кортежа
def get_players_attr(player, ret=None):
    player_cod, player_pin = player
    player_symbol, player_color = SIGNS[player_pin], SIGNS_color[player_pin]
    player_other_pin = sum(SIGNS.keys()) - player_pin
    player_other_symbol, player_other_color = SIGNS[player_other_pin], SIGNS_color[player_other_pin]

    return_this, return_other = (player_pin, player_other_pin) if ret is None else \
                                (player_symbol, player_other_symbol) if ret == 'SYMBOL' else \
                                (player_color, player_other_color)

    return (return_this, return_other) if player_cod == PLAYER_one else (return_other, return_this)


# Выводит переданные фрагменты в указанной позиции экрана
def pynput_print(*fragments_for_printing, sep=None, position=None):
    if position:
        pos_x, pos_y = position
        goto_xy(pos_x, pos_y)
        if sep:
            for i, fragment in enumerate(fragments_for_printing):
                goto_xy(pos_x, pos_y + i)
                print(fragment)
            return
    print(*fragments_for_printing, sep=sep)


# Навигационные границы игрового поля
#   На вход получает: левая граница поля, размер ячейки поля,
#                     размер поля (по числу ячеек) по интересующей оси
#   Возвращает: координаты крайних левой / правой ячеек, начальное положение,
#               расстояние между соседними ячейками, размер зоны статистики
# x, x_min, x_max, x_d = set_nav(X0, CELL_x, SIZE_BOARD)
def set_nav(c0, cell_s, cell_cnt):
    c = c0 + int((cell_s + 1) / 2)
    return c, c, c0 + int((cell_s + 1) * (cell_cnt - 0.5)), cell_s + 1


# Отрисовка игрового поля
# Входные параметры: board_s - состояние игры на игровом поле
# (в виде массива N x N - структура массива список в списке)
def drawing_board(board_s):

    offset = lambda cell_s, ofs: int((cell_s + 1) * (ofs + 0.5))

    # Определяем элементы "графики" игрового поля
    line_border = f"+{'-' * CELL_x}" * SIZE_BOARD + '+'
    line_cell = f"|{' ' * CELL_x}" * SIZE_BOARD + '|' * CELL_y

    # Рисуем игровое поле
    for i in range(SIZE_BOARD):
        pynput_print(f'{color_board}{line_border}', f'{color_board}{line_cell}',
                     sep='\n', position=(X0, Y0 + i * (CELL_y+1)))
    pynput_print(f'{line_border}', position=(X0, Y0 + (CELL_y+1) * SIZE_BOARD))

    # Выводим текущую расстановку игры
    board_sign = reduce(lambda lel, el: lel + [list(map(lambda l_el: SIGNS[l_el], el))], board_s, [])
    for i in range(0, SIZE_BOARD):
        y = Y0 + offset(CELL_y, i)
        for j in range(0, SIZE_BOARD):
            sign_curr = board_sign[i][j]
            sign_color = SIGNS_color[board_s[i][j]]
            x = X0 + offset(CELL_x, j)
            pynput_print(f'{sign_color}{sign_curr}', position=(x, y))


# Вывод текущего состояния игры:
# Игра не окончена  ->  N-й раунд. Ход - Игрок-[1/2] ([X/O]) ...
# Игра завершена    ->  [3]-й Раунд. Победил: Игрок-[1/2]
# Вх. параметры:    n_gm - раунд;
#                   wins_pl -> (winner, wins_1, wins_2) данные текущего игрока, победы 1-го, 2-го игрока, соответственно
#                               winner -> (код игрока, код игрового значка)
#                               если игра не окончена - wins_1 и wins_2 -> отсутствуют, т.е. wins_pl = winner
#                   game_status - статус игры (в виде массива N x N - структура массива список в списке);
def drawing_inscriptions(n_round, game_board, winners, result=None):

    spaces_grout = ' ' * len('-> Игрок-1 "x"    ')

    # Комментарий (краткая инструкция к игре)
    def show_comment():
        _, _, axis_y, _ = set_nav(Y0, CELL_y, SIZE_BOARD)
        pynput_print(f'{color_comment}{italics}Двигайтесь по полю, используя стрелки.{normal}',
                     f'{color_comment}{italics}'
                     f'Установить/Убрать "x" | "o" - [Пробел]: Убрать "x" | "o" - [Del]; '
                     f'Завершить ход - [Enter]. Выйти из игры - [Esc]...{normal}{color_norm}',
                     sep='\n', position=(X0, axis_y + 3)
                     )

    # Текущий раунд игры окончен
    def show_statistic():
        player, wins_1, wins_2 = winners
        # Результаты текущего раунда игры
        if result:                                                              # есть победитель в текущей игре
            winner_cod, winner_pin = player
            color_win = SIGNS_color[winner_pin]
            text_round = f'{color_round}Победитель: {color_win}Игрок-{winner_cod} ' \
                         f'"{bolt}{SIGNS[winner_pin]}"{spaces_grout}{normal}'
        else:                                                                   # НИЧЬЯ (победителей нет)
            text_round = f'{color_acc_draw}НИЧЬЯ{spaces_grout}{normal}'
        pynput_print(f'{color_round}Раунд {n_round}. ', text_round, position=(X0, Y0 - 1))
        #  Статистика игр
        color_one, color_two = get_players_attr(player, ret='COLOR')
        _, _, axis_x, _ = set_nav(X0, CELL_x, SIZE_BOARD)
        pynput_print(f'{color_account}{under}Статистика выигрышей:{normal}',
                     f'{color_account}Сыграно партий - {bolt}{color_acc_total}{n_round}{normal}',
                     f'{color_account}Побед: {color_one}Игрок-1 - {wins_1}',
                     f'{color_account}       {color_two}Игрок-2 - {wins_2}',
                     f'{color_account}Ничьих         - {color_acc_draw}{n_round - wins_1 - wins_2}',
                     sep='\n', position=(axis_x + 7, Y0 + 1)
                     )

    # Игра не окончена. Сообщить чей ход и параметры игрока
    def show_order_move():
        # winner_cod, winner_pin = winners[:2]
        winner_cod, winner_pin = winners
        color_win = SIGNS_color[winner_pin]
        text_round = f'{color_round}Ход -> {color_win}Игрок-{winner_cod} ' \
                     f'"{bolt}{SIGNS[winner_pin]}"{spaces_grout}{normal} '
        pynput_print(f'{color_round}Раунд {n_round}. ', text_round, position=(X0, Y0 - 1))

    drawing_board(game_board)               # Отразить текущее состояние игры на поле

    # Игра не окончена. # Текущий раунд игры - сообщаем чей ход
    if result is None:
        show_order_move()
    else:
        show_statistic()
    show_comment()


# Возвращает key нажатой клавиши, только после того, как поток опустеет
def on_press(key):
    if queue.empty():
        queue.put(key)


# Поддержка графического интерфейса игры.
# Вход: current_player = (player_code, player_pin) - параметры текущего игрока (чей сейчас ход + код игрового значка)
#       board_st - состояние игры на игровом поле до хода текущего игрока (описывает состояние игровой среды)
# Возвращает: board_st - изменившееся состояние игры (после хода игрока)
# def dashboard(player_param, board_s, available):
#     player, sign_cod = player_param
def game_engine(sign_cod, board_s, available, xy=None):

    sign_symbol = SIGNS[sign_cod]

    def conv_xy_ind(c, c0, cell_s):                 # перевод координаты поля в индекс массива состояния
        return int((c - c0) / (cell_s + 1) + 0.5)

    # Снятие / установка игрового значка на поле
    def set_sign_on_board(x_curr, y_curr, x_set, y_set, ev_key):
        i = conv_xy_ind(y_curr, Y0, CELL_y)
        j = conv_xy_ind(x_curr, X0, CELL_x)
        go = int(10 * i + j)
        if not (go in available):                   # Проверка ячейка занята? Если занята, изменить содержимое нельзя
            return x_set, y_set
        if x_set and y_set:                         # установка/снятие значка текущего игрока на игровом поле
            if x_curr == x_set and y_curr == y_set:
                print(f'{normal} ')
                return 0, 0
            else:
                return x_set, y_set
        elif ev_key == keyboard.Key.delete:
            return x_set, y_set
        else:
            sign_color = Fore.YELLOW
            print(f'{sign_color}{sign_symbol}{normal}')
            return x_curr, y_curr

    x, x_min, x_max, x_d = set_nav(X0, CELL_x, SIZE_BOARD)
    y, y_min, y_max, y_d = set_nav(Y0, CELL_y, SIZE_BOARD)
    x, y = xy if xy else (x, y)
    x_sign = y_sign = 0                                   # координаты, установленного игроком, значка

    goto_xy(x, y)

    listener = keyboard.Listener(on_press=on_press, suppress=True)
    listener.start()

    while True:
        event_key = queue.get()

        if event_key == keyboard.Key.up:
            y = max(y_min, y - y_d)
        elif event_key == keyboard.Key.down:
            y = min(y_max, y + y_d)
        elif event_key == keyboard.Key.left:
            x = max(x_min, x - x_d)
        elif event_key == keyboard.Key.right:
            x = min(x_max, x + x_d)
        elif event_key in (keyboard.Key.space, keyboard.Key.delete) or \
                hasattr(event_key, 'char') and event_key.char and event_key.char in SIGNS_synonyms[sign_symbol]:
            x_sign, y_sign = set_sign_on_board(x, y, x_sign, y_sign, event_key)

        goto_xy(x, y)

        result = None
        if event_key == keyboard.Key.enter and x_sign and y_sign:
            i = conv_xy_ind(y_sign, Y0, CELL_y) - 1
            j = conv_xy_ind(x_sign, X0, CELL_x) - 1
            board_s[i][j] = sign_cod
            result = (x, y)                         # True
        elif event_key == keyboard.Key.esc: pass
        else: continue

        goto_xy(0, y_max)
        listener.stop()
        return result


# Доступные ячейки
def get_av_moves(board_s):
    coordinates = [10 * ell + el for ell in range(1, SIZE_BOARD + 1) for el in range(1, SIZE_BOARD + 1)]
    return tuple(filter(lambda m: not board_s[m // 10 - 1][m % 10 - 1], coordinates))


# Задание параметра в настройках игры
def set_parameter(values_accept, default, txt_explain, pos_x,
                  offset_y, pos_relative=73, type_accept=None):

    goto = pos_x, Y0 + offset_y
    pynput_print(' ' * (pos_relative + 2), sep=None, position=goto)
    goto_xy(*goto)
    if type_accept: values_accept = values_accept,

    param_value = get_input(*values_accept, default=default, txt=f'{color_comment}{txt_explain}',
                            type_input=type_accept, end='-', not_mess=True, goto=goto, len_to_clear=INPUT_zone)

    goto = pos_x + pos_relative, Y0 + offset_y
    if (not type_accept or param_value is None) and question(param_value, goto=pos_exit):
        pynput_print(f'{color_cancel}Отмена -> EXIT', sep=None, position=goto)
        return None

    # goto_xy(pos_x + pos_relative, Y0 + offset_y)
    # print(f'{color_set}{param_value}')
    pynput_print(f'{color_set}{param_value}', sep=None, position=goto)
    return param_value


# Отладка Dashboard'а
if __name__ == '__main__':

    # Инициализация
    n_games = 0
    wins_pl1, wins_pl2 = 0, 0
    size_min, size_max = 3, 8           # Допустимые размеры доски
    pos_question = set_nav(X0, CELL_x, SIZE_BOARD)[2] + len(' Статистика выигрышей:') + 10
    goto_xy(pos_question, Y0 + 6)
    pos_exit = (pos_question, Y0 + 7)
    os.system('cls')                    # Подготовка экрана для вывода игрового поля

    # Цикл серии игр в крестики-нолики
    while True:

        n_games += 1

        # Имитация выбора размера поля, № игрока и его игрового значка и пр.
        # TODO: Оформить отдельной процедурой
        board_status = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        player_curr = random.randint(1, 2)
        # sign_curr = random.randint(1, 2)

        # Настройка параметров игры
        goto_xy(pos_question, Y0 + 1)
        print(f'{color_comment}{under}Настройка параметров игры. '
              f'Для отказа и завершения - "-". Значение по умолчанию - кл. [Enter]:'
              f'{normal}')

        # Уточнение размера доски
        size_accept = (size_min, size_max)
        size = set_parameter(size_accept, 3, 'Размер доски.', pos_question, 2)
        if size is None: break
        SIZE_BOARD = size

        # Уточнение выигрышной комбинации
        size_accept = (size_min,  SIZE_BOARD)
        numb_XO = set_parameter(size_accept, 3, 'Длина выигрышной комбинации.', pos_question, 3)
        if numb_XO is None: break

        # Выбрать номер игрока, за которого вы играете ("1" - Игрок-1; "2" - Игрок-2")
        size_accept = tuple(map(str, (PLAYER_one, PLAYER_two)))
        player_my = set_parameter(size_accept, str(PLAYER_one), 'Выберите свой номер.        ',
                                  pos_question, 4, type_accept=tuple)
        if player_my is None: break
        player_my = int(player_my)

        # Выбрать свой значок ("х" иди "о")
        symbols = tuple(SIGNS.values())[-2:]
        symbol_may = set_parameter(symbols, symbols[0], f'Выберите свой символ для игры.',      # {color_comment}
                                   pos_question, 5, type_accept=tuple)
        if symbol_may is None: break
        sign_my = dict_rev(SIGNS, symbol_may)
        # pin_player = dict([(player_my, SIGNS[pin_cod_my]),
        #                    (PLAYER_one + PLAYER_two - player_my, SIGNS[3 - pin_cod_my])])

        sign_curr = sign_my if player_curr == player_my else sum(SIGNS) - sign_my
        player_attr = (player_curr, sign_curr)

        goto_xy()
        print(normal)

        # Цикл текущего раунда игры
        result_move = None
        while True:

            # Запуск игрового движка
            drawing_inscriptions(n_games, board_status, player_attr)    # Сообщим чей ход
            av_moves = get_av_moves(board_status)
            result_move = game_engine(sign_curr, board_status, av_moves, result_move)   # Движок графической поддержки хода

            if not result_move:     # Завершение текущего раунда при отказе его продолжения (по кл. Esc)
                break

            # Имитация результата текущего раунда игры (выигрыш, ничья, игра не окончена)
            # result_game = (0, 1, None):
            #               (ничья, выигрыш текущего игрока, игра не окончена) -
            #               с вероятностью (10%, 10%, 80%), соответственно
            result_rand = random.choice([n for n in range(10)])     # вероятности получения того или иного результата
            result_game = 0 if result_rand < 3 else \
                          1 if result_rand == 3 else None

            # Обработка результата состояния игры в текущем раунде
            if result_game is None:                                             # игра не окончена
                player_curr = PLAYER_one + PLAYER_two - player_curr             # смена игрока
                sign_curr = sum(SIGNS.keys()) - sign_curr
                player_attr = (player_curr, sign_curr)
                continue

            # По завершении раунда выводим его результаты и статистику
            wins_pl1 += 1 if result_game and player_curr == PLAYER_one else 0
            wins_pl2 += 1 if result_game and player_curr == PLAYER_two else 0
            wins_pl = player_attr, wins_pl1, wins_pl2
            drawing_inscriptions(n_games, board_status, wins_pl, result_game)   # Текущая статистика игр
            break

        # Подтверждение Продолжения игры / Завершения серии игр в крестики-нолики:
        # TODO: Оформить отдельной процедурой
        goto_xy(pos_question, Y0 + 6)
        if result_move and not question(txt_req=f'Еще раз? ("y" - ДА) -> ',
                                        cancel=False, enter=None, goto=pos_exit, not_mess=True): break
        if not result_move and question(txt_req=f'Завершить игру? ("y" - ДА) -> ',
                                        cancel=False, enter=True, goto=pos_exit): break
        spaces_grout = ' ' * len('Завершить игру? ("y" - ДА) ->  ')
        pynput_print(f'{spaces_grout}', position=(pos_question, Y0 + 6))

    goto_xy(0, set_nav(Y0, CELL_y, SIZE_BOARD)[2] + 6)
