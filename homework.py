# task 1

print('task_1', end='\n\n')

development = 'разработка'
soket = 'сокет'
decorator = 'декоратор'

print(f'"Разработка" тип - {type(development)}\n"Сокет" тип - {type(soket)}\n"Декоратор" тип - {type(decorator)}\n')

development_cod = development.encode(encoding='utf-8')
soket_cod = soket.encode(encoding='utf-8')
decorator_cod = decorator.encode(encoding='utf-8')

print(f'"Разработка" тип - {type(development_cod)}\n"Разработка" кодовые точки - {development_cod}\n\n'
      f'"Сокет" тип - {type(soket_cod)}\n"Сокет" кодовые точки - {soket_cod}\n\n'
      f'"Декоратор" тип - {type(decorator_cod)}\n"Декоратор" кодовые точки - {decorator_cod}\n')

# task 2

print('task_2', end='\n\n')

word_1 =b'class'
word_2 = b'function'
word_3 = b'method'

print(f'Длина "class" - {len(word_1)}\nДлина "function" - {len(word_2)}\nДлина "method" - {len(word_3)}\n')
print(f'Байты "class" - {word_1}\nБайты "function" - {word_2}\nБайты "method" - {word_3}\n')
print(f'Тип "class" - {type(word_1)}\nТип "function" - {type(word_2)}\nТип "method" - {type(word_3)}\n')

# task 3

print('task_3', end='\n\n')

"""
word_attribute = b'attribute'
word_class = b'класс'
word_func = b'функция'
word_type = b'type'
"""

# появляется ошибка SyntaxError, ее разве можно обработать?

print("Невозможно записать в байтовом типе - 'класс' и 'функция'\n")

# task 4

print('task_4', end='\n\n')

list_word = ['администрирование', "protocol", 'standard']

for i in list_word:
      code = i.encode(encoding="UTF-8")
      print(f'Кодирование {i} - {code}')
      dec = code.decode('UTF-8')
      print(f'Декодирование {i} - {dec}\n')

# task 5

print('task_5', end='\n\n')

import subprocess

list_url = ['yandex.ru', 'youtube.com']
for i in list_url:
      args = ['ping', i]

      subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
      result = []
      count = 0
      for i in subproc_ping.stdout:
            result.append(i.decode('utf-8'))
            count += 1
            if count == 6:
                  break

      print(result, end='\n\n')

# task 6

import locale

print('task_6', end='\n\n')

file = open('test_file.txt', 'w')
file.write(f'сетевое программирование\nсокет\nдекоратор\n')
file.close()

print(f'Используемая кодировка {locale.getpreferredencoding()}\n')

file = open('test_file.txt', 'r', encoding='utf-8')
for line in file:
      print(line)
file.close()