"""
Домашнее задание к Семинару №9
-------------------------------
1. Создайте программу для игры в "Крестики-нолики"
при помощи виртуального окружения и PIP.
Перенести игру в виртуальное окружение venv найти любую понравившуюся библиотеку
(например, можно раскрасить цветом вывод на консоли или проверку данных)
и установить при помощи pip в venv задействовать установленную библиотеку
"""
from t3_controller import main

"""
Структура модулей
1) main - стартовый (запускающий) модуль - настоящий файл
2) gis (graphical interface support) - пакет модулей поддержки графического интерфейса игры
3) t3_models - модель данных учета состояния текущего раунда игры и результатов серии игр
   (состояние, конфигурация игрового поля. данные игроков, статистика игр)
4) t3_controller - управление и контроль процессами игры, расчеты игровых ситуаций
5) utilities - утилиты, сервисные процедуры общего назначения      
"""


# Игра "крести-нолики". Реализация графического интерфейса.
def print_hi(name):
    print(f'Hi, {name}')


if __name__ == '__main__':
    print_hi('Добро пожаловать в игру "Крестики - нолики"')
    main()
