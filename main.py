from barcode import Code128
from barcode.writer import ImageWriter
import tkinter as tk
from tkinter import messagebox


counter = 0


def generate_barcode(code_number):

    global counter

    ean = Code128(str(code_number), writer=ImageWriter())
    filename = f'barcode_{counter}.png'
    counter += 1
    full_path = ean.save(filename)
    return full_path


def on_generate_click():

    user_input = entry_code.get()

    if not user_input.strip():  # Проверка пустого поля
        messagebox.showwarning('Предупреждение', 'Вы ничего не ввели!')
        return

    try:
        result_file = generate_barcode(user_input)
        messagebox.showinfo('Успех!', f'Штрих-код успешно сохранён в файле:\n{result_file}')
    except Exception as err:
        messagebox.showerror('Ошибка', str(err))


# Основной интерфейс приложения
root = tk.Tk()
root.title('Генерация штрих-кодов')

label = tk.Label(root, text='Введите число:')
label.pack(pady=(10, 0))  # Верхний отступ 10 пикселей

entry_code = tk.Entry(root, width=30)
entry_code.pack(padx=10, pady=10)

button_generate = tk.Button(root, text="Создать штрих-код", command=on_generate_click)
button_generate.pack(pady=(0, 10))  # Нижний отступ 10 пикселей

root.mainloop()
