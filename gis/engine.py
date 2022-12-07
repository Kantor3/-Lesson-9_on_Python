"""
Graphics.
Модуль непосредственно поддержки графического интерфейса игры
"""

from utilities import goto_xy
from gis import normal, color_XO_inst
from gis.view_ext import CELL_x, CELL_y, X0, Y0
from t3_models import set_nav
from t3_models import SIGNS_synonyms
import t3_models as m

from pynput import keyboard
from queue import Queue
import colorama
queue = Queue()
colorama.init()


# Возвращает key нажатой клавиши, только после того, как поток опустеет
def on_press(key):
    if queue.empty():
        queue.put(key)


# перевод координаты поля в индекс массива состояния
def conv_xy_ind(c, c0, cell_s):
    return int((c - c0) / (cell_s + 1) + 0.5)


# Снятие / установка игрового значка на поле
def set_sign_on_board(available, x_curr, y_curr, x_set, y_set, ev_key, sign_symbol):
    i = conv_xy_ind(y_curr, Y0, CELL_y)
    j = conv_xy_ind(x_curr, X0, CELL_x)
    go = int(10 * i + j)
    if not (go in available):                       # Проверка ячейка занята? Если занята, изменить содержимое нельзя
        return x_set, y_set
    if x_set and y_set:                             # установка/снятие значка текущего игрока на игровом поле
        if x_curr == x_set and y_curr == y_set:
            print(f'{normal} ')
            return 0, 0
        else:
            return x_set, y_set
    elif ev_key == keyboard.Key.delete:
        return x_set, y_set
    else:
        print(f'{color_XO_inst}{sign_symbol}{normal}')
        return x_curr, y_curr


# Поддержка графического интерфейса игры.
# Вход: sign_cod    - текущий игровой символ (код)
#       board_s     - состояние игры на игровом поле до хода текущего игрока (описывает состояние игровой среды)
#       available   - доступные для хода поля
#       xy          - начальное положение курсора на игровом поле
# Возвращает: board_s - изменившееся состояние игры (после хода игрока)
def game_engine(sign_cod, board_s, available, xy=None):

    sign_symbol = m.SIGNS[sign_cod]

    x, x_min, x_max, x_d = set_nav(X0, CELL_x, m.SIZE_BOARD)
    y, y_min, y_max, y_d = set_nav(Y0, CELL_y, m.SIZE_BOARD)
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
            x_sign, y_sign = set_sign_on_board(available, x, y, x_sign, y_sign, event_key, sign_symbol)

        goto_xy(x, y)

        result = None
        if event_key == keyboard.Key.enter and x_sign and y_sign:
            i = conv_xy_ind(y_sign, Y0, CELL_y) - 1
            j = conv_xy_ind(x_sign, X0, CELL_x) - 1
            board_s[i][j] = sign_cod
            result = x, y
        elif event_key == keyboard.Key.esc: pass
        else: continue

        goto_xy(0, y_max)
        listener.stop()
        return result
