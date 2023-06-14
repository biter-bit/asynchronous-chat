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

word_attribute = 'attribute'
word_class = 'класс'
word_func = 'функция'
word_type = 'type'

word_list = [word_attribute, word_class, word_func, word_type]

for i in word_list:
      try:
            print(bytes(i, 'ascii'))
      except UnicodeEncodeError:
            print(f'Слово "{i}" нельзя записать в байтовом типе')


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

import subprocess, chardet

list_url = ['yandex.ru', 'youtube.com']
for i in list_url:
      args = ['ping', i]
      subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
      result = []
      count = 0
      for line in subproc_ping.stdout:
            res = chardet.detect(line)
            line = line.decode(res['encoding']).encode('utf-8')
            result.append(line.decode('utf-8'))
            count += 1
            if count == 6:
                  break

      print(result, end='\n\n')

# task 6

print('task_6', end='\n\n')

file = open('../test_file.txt', 'w')
file.write(f'сетевое программирование\nсокет\nдекоратор\n')
file.close()

file = open('../test_file.txt', 'rb')
detector = chardet.universaldetector.UniversalDetector()
for line in file:
      detector.feed(line)
      if detector.done:
            break
detector.close()
print(f'Используемая кодировка {detector.result["encoding"]}\n')

file = open('../test_file.txt', 'r', encoding=detector.result["encoding"])
for line in file:
      print(line)
file.close()