"""
Отдельные полезные функции составляющие библиотеку
в т.ч. функции по работе с простейшей БД в виде списка записей.
Каждая запись - именованный словарь с полями и их значениями
"""
import math
import ctypes
from typing import Any

# Параметры для позиционирования курсора
STD_OUTPUT_HANDLE = -11
hOut = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)


# Организация выхода:
# Варианты:
# 1. sign = None
# 2. sign = True
# 1. sign = '[symbol_EXIT]' - передан символ для запроса выхода, например, "Y"
# или строка символов, каждый из которых ведет к "Выходу"
# cancel: True - Подтвердить Продолжение
#         False - Подтвердить Выход
def question(sign='YyНн', special=None,
             txt_req='Продолжить? ("y" - ДА) -> ', goto=None,
             not_mess=None, cancel=True, enter=None):

    add = special if not (special is None) else False
    if isinstance(sign, str):
        inp = input(txt_req)
        out = not ( f'-{inp}' in map(lambda el: f'-{el}', f'{sign}{add if add else ""}') )
        out = out if enter is None or inp else False
    else:
        inp = None
        out = sign is None or isinstance(sign, bool) and sign

    out = out if cancel else not out         # Обращение значения возврата на обратное значение при cancel = False
    if out:
        if not not_mess:
            prefix = '\n'
            if goto:
                prefix = ''
                goto_xy(*goto)
            print(f'{prefix}\033[0m--> Работа с программой завершена, До встречи!')
        return True

    return False if special is None else inp


# Организация ввода и возврат целого, вещественного числа (в т.ч. отрицательное) или строки
# в заданном диапазоне или выход. С полным контролем корректности
# def get_input(*rang, default=None, txt='Введите число', type_input=int, end=None, not_mess=None):
def get_input(*rang, default=None, txt='Введите число',
              type_input=None, end=None, not_mess=None,
              goto=None, len_to_clear=None):

    def set_goto():
        line_to_clear = ' ' * (len_to_clear if len_to_clear else 0)
        goto_xy(*goto)
        print(line_to_clear)
        goto_xy(*goto)

    type_input = int if type_input is None else type_input

    borders = '' if len(rang) == 0 or rang[0] is None and rang[-1] is None else \
              f'{rang[0]}' if type_input == tuple else \
              f'({rang[0]} ... )' if len(rang) == 1 else \
              f'({rang[0]} ... {rang[1]})'

    txt_input = f'{txt} {f"Возможные значения => {borders}" if borders else ""}'
    frm, to = (rang + (None, None))[:2]

    while True:
        txt_or = '' if end is None or default else ' или '
        key_for_cancel = f'введите "{end}"' if not (end is None) else (f'{txt_or}[Enter]' if default is None else '')
        mess_cancel = '' if not_mess else f'Для отказа {key_for_cancel} '
        entered = input(f'{txt_input} {mess_cancel}-> ')
        entered = None if not (end is None) and entered == end else \
            (None if default is None else default) if len(entered) == 0 else entered
        if entered is None:
            break

        if type_input == tuple:
            if not (entered in rang[0]):
                if goto: set_goto()
                print(f'Введено "{entered}" допустимые значения {rang[0]}. ', end='')
                txt_input = 'Повторите ввод'
                continue

        if type_input != int:
            break

        try:
            entered = int(entered)
        except ValueError:
            try:
                entered = float(entered)
            except ValueError:
                if goto: set_goto()
                print(f'Введенная строка "{entered}" не является числом. ', end='')
                txt_input = 'Повторите ввод'
                continue

        if not (frm is None) and entered < frm or not (to is None) and entered > to:
            if goto: set_goto()
            print(f'Введено число [{entered}] не в диапазоне ({rang[0]} ... {rang[1]}). ', end='')
            txt_input = 'Повторите ввод'
            continue

        break

    return entered


# Ввод нескольких элементов данных (целых чисел, строк и пр.) - Возврат введенных данных в виде кортежа
def get_inputs(*input_params, type_input=int, end=None, not_mess=None, all_input=None):
    tup_i_par = tuple()
    cnt_params = len(input_params)

    for param in input_params:
        if type_input == tuple:
            if isinstance(param[0], tuple):
                ranges = (param[0], None, param[1] if len(param) == 3 else None)
            else:
                ranges = (param[:-1] + (None, None))[:3]

            input_param = get_input(ranges[0], ranges[1], default=ranges[2],  # = last_input =
                                    txt=param[-1], type_input=type_input, end=end, not_mess=not_mess)
        else:
            input_param = get_input(txt=param, type_input=type_input, end=end, not_mess=not_mess)
        if all_input is None and input_param is None:
            break

        tup_i_par += (input_param,)

    return (tup_i_par + (None,) * cnt_params)[:cnt_params]


# Считывание и возврат данных из файла по заданному пути
def get_data_file(name_file, err_txt='\n'):
    try:
        with open(name_file, 'r', encoding='utf8') as f:
            str_read = f.read()
        return str_read
    except FileNotFoundError:
        print(f'{err_txt}The requested file {name_file} was not found')
        return None


# Запись данных в файл
def wr_data_file(name_file, txt, message=None):
    try:
        f = open(name_file, 'w')
        f.close()
        with open(name_file, 'a', encoding='utf8') as f:
            f.writelines(txt)
        if not (message is None):
            print(f'{message} -> {name_file}')
        return True
    except FileNotFoundError:
        print(f'The requested file {name_file} was not found')
        return None


# Получение смещенного значения элементов кортежа на величину
# кортежа смещения *offset. Пример:
# tup = (10, 2, 7); offset = (2, -1); pos -2 => (10, 4, 6)
def offset_tup(tup, *offset, pos=0):
    return *tup[:pos], *tuple([el + s for el, s in zip(tup[pos:], offset)]), *tup[pos:][len(offset):]


# Поиск ключа по соответствующему значению (только для словаря, у которого значения все различные)
def dict_rev(dic, key):
    return dict([(v, k) for k, v in dic.items()])[key]


# транспонирование вложенного списка
# size_ll = len(stt)
# stt_flat = [ell for i in range(size_ll) for el in stt for ell in [el[i]]]            # этот вариант тоже рабочий
# ret = [reduce(lambda ell, el: ell + [el], stt_flat[i * size_ll:][:size_ll], []) for i in range(size_ll)]
def trans_ll(lst_lst):
    return [list(el) for el in zip(*lst_lst)]


# Проверка коллекции на ее пустое значение (пустые значения ее содержимого {0, None, False, '', [], ()})
def empty_coll(coll):
    return not list(filter(lambda el: el, coll)) if not isinstance(coll, dict) else \
               list(filter(lambda el: el, [*coll.values()]))


# Разделитель строки на кортеж опций
def sep_option(line_option):
    return tuple(f"-{',-'.join(line_option)}".split(','))


# Вернуть пустое значение указанного типа
def get_empty(type_val):
    types = {int: 0, float: 0.0, str: '', list: [], tuple: (), dict: dict(), bool: False, set: set()}
    return types[type_val]


# Устанавливает курсор по указанным координатам (x, y)
def goto_xy(pos_x=None, pos_y=None):
    class COORD(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

        def __init__(self, x_cur, y_cur, *args: Any, **kw: Any):
            super().__init__(*args, **kw)
            self.X = x_cur
            self.Y = y_cur

    pos_x = 0 if pos_x is None else pos_x
    pos_y = 0 if pos_y is None else pos_y
    INIT_POS = COORD(pos_x, pos_y)
    ctypes.windll.kernel32.SetConsoleCursorPosition(hOut, INIT_POS)


"""
Утилиты по работе с элементами базы данных (БД)
БД в форме списка записей. Каждая запись - в форме словаря полей и их значений
"""


# Инициализация пустыми значениями нужного типа полей с неопределенными значениями (None)
def init_fields_none(record, sample):
    types_fields = tuple(map(type, sample.values())) if isinstance(sample, dict) else sample
    record = map(lambda el: str(get_empty(el[1])) if el[0] is None else el[0], zip(record, types_fields))
    return tuple(map(lambda el: (el[0] if el[1] == str else eval(el[0])), zip(record, types_fields)))


# Вернуть список записей БД, у которых указанные поля (ключи словаря записи) имеют непустое значение
def get_fill_fields(records, fields):
    return list(filter(lambda rec: list(filter(lambda el: el, [rec[k] for k in fields])), records))


# Обрезка записей БД по указанным полям
def slice_by_fields(records, fields):
    return [dict([(k, staff_in[k]) for k in fields]) for staff_in in records]


# Приведение значений указанных полей к заданному типу
def typing_by_fields(records, structure):
    fields, types = (structure.keys(), structure.values()) if isinstance(structure, dict) else structure
    types_by_fields = dict([(item[0], item[1]) for item in zip(fields, types)])
    return [dict([(k, v if types_by_fields[k] == str else eval(v))
                  for k, v in staff_in.items()]) for staff_in in records]


# Получение списка ID переданной БД
def get_ids(db, id_name='id'):
    ids = tuple(map(lambda rec: rec[id_name], db))
    return ids


# Получение уникального ID для переданной БД
def get_uniqid_db(db, id_name='id'):
    ids = (0, *get_ids(db, id_name))
    id_new = max(ids) + 1
    return id_new


# Получение кортежа максимальной длины значения полей БД
def get_maxlen_fields(db):
    len_fields = [tuple(map(len, map(str, el.values()))) for el in db] + [tuple(map(len, db[0]))]
    len_fields = [el for el in zip(*len_fields)]
    return list(map(max, len_fields))


# Поиск данных по переданному фильтру по полям базы данных
# реализован самый простой вариант - все полученные данные по полям соединяются логикой "И":
# Вариант-1 Фильтр => кортеж значений всех полей, последовательность - строгая.
#                     Не учитываемые поля, значения которых в кортеже == None.
# Вариант-2 Фильтр => в виде запроса, представляющего словарь с полями, по которым требуется выполнить (поиск/отбор)
# Вариант-3 Фильтр => в виде номера ID (тип ID - int)
# Если это поиск соответствия для переданной записи - то возврат True/False, иначе индекс найденной записи из БД или 0
# request - что ищем (запрос, фильтр), варианты см. выше
# records_db - где ищем (если не указано, то по всему телефонному справочнику)
def where(request, records_db, id_name='id'):

    def isn_records(recs, req):
        if isinstance(req, dict):
            res = math.prod([str(v) in str(recs[k]) for k, v in tuple(req.items())])
        else:
            res = math.prod([f is None or str(f) in str(v) for v, f in zip(tuple(recs.values()), req)])
        return res

    request = {id_name: request} if isinstance(request, int) else request   # поддержка варианта поиска по id

    if isinstance(records_db, dict):                # если проверяем в одной (переданной) записи
        return isn_records(records_db, request)
    else:                                           # если это список записей, возвращаем номер найденной записи
        for ind, rec in enumerate(records_db):
            if isn_records(rec, request):
                return ind
        else:
            return None


# Для тестирования методов библиотеки по работе с БД:
if __name__ == '__main__':
    staffs = [{'id': 1, 'fio': 'Ivan Petrov', 'salary': 40},
              {'id': 2, 'fio': 'Bob Ivanov', 'salary': 50},
              {'id': 3, 'fio': 'John Don', 'salary': 100}
              ]
    print(get_ids(staffs, id_name='id'))
