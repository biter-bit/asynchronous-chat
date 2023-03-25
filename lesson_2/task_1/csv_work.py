import csv
import re
import chardet

# def create_file(name, expansion, data, count):
#     list_file_name = []
#     for i in range(1, count):
#         name_file = f'{name}_{i}.{expansion}'
#         with open(name_file, 'w', encoding='utf-8') as file:
#             file.write(data)
#         list_file_name.append(name_file)
#     return list_file_name
#
#
#
# data = 'Изготовитель системы\nНазвание ОС\nКод продукта\nТип системы'
#
#
# with open('new_file.txt', 'w', encoding='utf-8') as file:
#     file.write(res)

list_name_file = ['info_1.txt', 'info_2.txt', 'info_3.txt']


def get_data():
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = [['Изготовитель OC', 'Название ОС', 'Код продукта', 'Тип системы']]
    for i in list_name_file:
        with open(i, 'rb') as file:
            encoding_file = chardet.detect(file.read())
            file.seek(0)
            res = file.read().decode(encoding_file['encoding'])

            result_reg_prod = re.compile('(?<=Изготовитель ОС:).+')
            os_prod_list.append(result_reg_prod.findall(res)[0].strip(' \r'))

            result_reg_name = re.compile('(?<=Название ОС:).+')
            os_name_list.append(result_reg_name.findall(res)[0].strip(' \r'))

            result_reg_code = re.compile('(?<=Код продукта:).+')
            os_code_list.append(result_reg_code.findall(res)[0].strip(' \r'))

            result_reg_type = re.compile('(?<=Тип системы:).+')
            os_type_list.append(result_reg_type.findall(res)[0].strip(' \r'))

    for i in range(3):
        main_data.append([os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]])
    return main_data


def write_to_csv(path):
    with open(path, 'w') as f:
        f_writer = csv.writer(f)
        for row in get_data():
            f_writer.writerow(row)


write_to_csv('test.csv')
