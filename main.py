from barcode import Code128
from barcode.writer import ImageWriter


counter = 0


def generate_barcode(code_number):
    global counter
    ean = Code128(str(code_number), writer=ImageWriter())

    filename = f'barcode_{counter}'
    counter += 1

    full_path = ean.save(filename)
    print(f'Штрих-код сохранен в файле {full_path}')


if __name__ == "__main__":
    while True:
        code_input = input("Введите число: ")
        if code_input == 'exit':
            break
        elif not code_input.isdigit():
            print("Ошибка ввода.")
        else:
            try:
                generate_barcode(code_input)
            except Exception as e:
                print(e)
