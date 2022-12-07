"""
GIS (graphical interface support).
Пакет модулей поддержки графического интерфейса игры
"""
# Глобальные переменные пакета
from colorama import Fore, Back, Style

# Определяем цвета элементов надписей
color_norm = Fore.RESET
color_cancel = Fore.RED
color_set = Fore.GREEN
color_board = Fore.LIGHTWHITE_EX
color_round = Fore.YELLOW
color_account = Fore.WHITE
color_acc_total = Fore.YELLOW
color_acc_draw = Fore.LIGHTWHITE_EX
color_comment = Fore.WHITE
color_X = Fore.RED
color_O = Fore.BLUE
color_space = Fore.RESET
color_XO_inst = Fore.YELLOW
color_mark = Back.WHITE
color_reset = Style.RESET_ALL

# Другие аттрибуты элементов надписей
normal = '\033[0m'
bolt = '\033[1m'
italics = '\033[3m'
under = '\033[4m'
