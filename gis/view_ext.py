"""
Внешний, по отношению к игре в целом, интерфейс (интерфейс внешнего периметра)
- Уточнения по начале, завершению игры, приветствие, прощание и пр.
"""
from utilities import offset_tup, goto_xy, question, get_input
from gis import normal, color_comment, color_cancel, color_set, under
from t3_models import set_nav
import t3_models as m

import os

# Константы зон интерфейса:
# размещение поля на экране, ключевые точки зон
CELL_x, CELL_y = 3, 1                                   # размер ячейки
X0, Y0 = 3, 2                                           # координаты левого угла поля
STATISTICS_zone = len('Статистика выигрышей:')          # ширина зоны статистики
INPUT_zone = 76                                         # длина зоны ввода данных настройки параметров
pos_question = set_nav(X0, CELL_x, m.SIZE_BOARD)[2] + STATISTICS_zone + 10, Y0 + 6  # Начало зоны задания параметров
pos_answer = offset_tup(pos_question, 1, pos=-1)        # Позиция курсора в зоне "Ответ" системы под статистикой
pos_exit = 0, set_nav(Y0, CELL_y, m.SIZE_BOARD)[2] + 6  # Позиция курсора в зоне "Выход"
pos_settings = 72                                       # Позиция вывода введенных значений параметров игры


# Инициация размеров интерфейсных зон (заплатка, т.к. н`ет функционала изменения этих параметров, да и не нужен он пока)
def init_view():
    global CELL_x
    global CELL_y
    global X0
    global Y0
    global STATISTICS_zone
    global INPUT_zone
    global pos_question
    global pos_exit
    global pos_answer
    CELL_x, CELL_y = CELL_x, CELL_y                         # размер ячейки
    X0, Y0 = X0, Y0                                         # координаты левого угла игрового поля
    STATISTICS_zone = STATISTICS_zone                       # ширина зоны статистики
    INPUT_zone = INPUT_zone                                 # длина зоны ввода данных настройки параметров
    pos_question = set_nav(X0, CELL_x, m.SIZE_BOARD)[2] + STATISTICS_zone + 10, Y0 + 6      # Конец зоны параметров
    pos_answer = offset_tup(pos_question, 1, pos=-1)        # Позиция курсора в зоне "Ответ" системы под статистикой
    pos_exit = 0, set_nav(Y0, CELL_y, m.SIZE_BOARD)[2] + 6  # Позиция курсора в зоне "Выход"

    return pos_question, pos_answer, pos_exit


# Выводит переданные фрагменты в указанной позиции экрана
def pynput_print(*fragments_for_printing, sep=None, goto=None):
    if goto:
        goto_xy(*goto)
        if sep:
            pos_x, pos_y = goto
            for i, fragment in enumerate(fragments_for_printing):
                goto_xy(pos_x, pos_y + i)
                print(fragment)
            return
    print(*fragments_for_printing, sep=sep)


# Запрос ввода и ввод параметров в настройках игры
def set_parameter(values_accept, default, txt_explain, pos_x, offset_y, type_accept=None, area=True):

    if not area: return default

    goto = pos_x, Y0 + offset_y
    pynput_print(' ' * (pos_settings + 2), sep=None, goto=goto)
    goto_xy(*goto)
    if type_accept: values_accept = values_accept,

    param_value = get_input(*values_accept, default=default, txt=f'{color_comment}{txt_explain}',
                            type_input=type_accept, end='-', not_mess=True, goto=goto, len_to_clear=INPUT_zone)

    goto = pos_x + pos_settings, Y0 + offset_y
    if (not type_accept or param_value is None) and question(param_value, goto=pos_exit):
        pynput_print(f'{color_cancel}-> Exit', sep=None, goto=goto)
        return None
    pynput_print(f'{color_set}{param_value}', sep=None, goto=goto)

    return param_value


# Подготовка экрана, разбивка на интерфейсные зоны:
#   TODO: отрисовка отдельных зон
#    - игровая (поле игры)
#    - зона вывода статистики
#    - зона задания параметров игры
# Пока только очистка экрана
def screen_preparation():
    os.system('cls')                    # Подготовка экрана для вывода игрового поля


def welcome_game(gre='Добро пожаловать', que='Начнем?'):
    screen_preparation()
    user_interaction(gre, zone=0, active=False)
    result = user_interaction(que, zone=0, add_zone=1, not_mess=True, cancel=False, enter=True)
    return result


# Взаимодействие с пользователем (игроком):
# - Уточнения / Подтверждения и пр.
# Входные параметры: question - Вопрос, Запрос уточнения, Сообщение
#                    zone - Зона (место на экране) вывода question:
#                           -   0           - титул игрового поля
#                           -  -1           - зона задания параметров
#                           -   1           - зона "Уточняющих вопросов" внутри игровой зоне, под статистикой
#                           -   2           - зона "Ответа" системы под статистикой
#                           -   3           - зона "Выход" - под игровой зоной
#                    add_zone - дополнительный параметр (смещение по Y относительно фокуса)
#                    active - если == False - выводится только сообщение question
#                    not_clear - если == True, то по завершении взаимодействия question не затирается
#                    enter  - если == True - при утвердительном ответе возвращается None
#                    cancel: True - Подтвердить Продолжение
#                            False - Подтвердить Выход
def user_interaction(question_txt, zone, add_zone=0, active=True, not_clear=None, **question_par):

    # Позиционирование и задание цвета
    if zone == 0:
        goto = X0, Y0 - 2 + add_zone
    elif zone == -1:
        goto = pos_question[0], Y0 - zone
        question_txt = f'{color_comment}{under}{question_txt}{normal}'
    elif zone == 1:
        goto = pos_question
    elif zone == 2:
        goto = pos_answer
    elif zone == 3:
        goto = offset_tup(pos_exit, -1, pos=-1)
    else:
        goto = (0, 0)

    # Просто сообщение, уведомление
    if not active:
        pynput_print(question_txt, goto=goto)
        return

    # Взаимодействие (Уточнения / Подтверждения)
    goto_xy(*goto)
    result = question(txt_req=question_txt, goto=pos_answer, **question_par)

    # Почистим за собой
    if not not_clear:
        spaces_grout = ' ' * (len(question_txt) + 10)
        pynput_print(spaces_grout, goto=goto)

    return result
