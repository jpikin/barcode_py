from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image, ImageDraw, ImageFont
import tkinter as tk
from tkinter import messagebox

counter = 0

# Настройки шрифта и размеров
font_size = 18
font_type = "arial.ttf"  # Можно выбрать другой шрифт, если он установлен на вашей системе
img_width_cm = 10
img_height_cm = 5
dpi = 300  # Чем больше DPI, тем лучше качество изображения

# Конвертируем сантиметры в пиксели
px_per_inch = dpi / 2.54  # Пикселей на дюйм
img_width_px = int(img_width_cm * px_per_inch)
img_height_px = int(img_height_cm * px_per_inch)


def generate_barcode(code_number):
    """
    Генерирует штрих-код формата Code128.
    Возвращает путь к файлу изображения штрих-кода.
    """
    global counter
    ean = Code128(str(code_number), writer=ImageWriter())
    filename = f'barcode_{counter}.png'
    counter += 1
    full_path = ean.save(filename)
    return full_path


def create_template(barcode_image_path, article, name, unit):
    """
    Создает шаблон изображения с текстом и штрих-кодом.
    """
    img = Image.new("RGB", (img_width_px, img_height_px), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(font_type, size=font_size)

    text_y_offset = 10  # Отступ от верха


    text_bbox = font.getbbox(article)
    text_width = text_bbox[2] - text_bbox[0]
    center_x = (img.width - text_width) // 2
    draw.text((center_x, text_y_offset), f"{article}", fill="black", font=font)

    text_bbox = font.getbbox(name)
    text_width = text_bbox[2] - text_bbox[0]
    center_x = (img.width - text_width) // 2
    draw.text((center_x, text_y_offset + font_size * 1.5), f"{name}", fill="black", font=font)

    text_bbox = font.getbbox(unit)
    text_width = text_bbox[2] - text_bbox[0]
    center_x = (img.width - text_width) // 2
    draw.text((center_x, text_y_offset + font_size * 3), f"{unit}", fill="black", font=font)

    # Добавляем штрих-код снизу справа
    bc_img = Image.open(barcode_image_path)
    scale_factor = 0.7  # Масштабируем штрих-код, чтобы он вписался
    new_bc_size = tuple(int(scale_factor * x) for x in bc_img.size)
    resized_bc = bc_img.resize(new_bc_size, resample=Image.LANCZOS)

    position_x = 10  # Слева с небольшим отступом
    position_y = img.height - resized_bc.height - 10  # Снизу с небольшим отступом

    img.paste(resized_bc, (position_x, position_y))

    template_filename = f'template_{counter}.png'
    img.save(template_filename)
    return template_filename


def on_generate_click():
    """Обработчик события нажатия кнопки."""
    article = entry_article.get().strip()
    name = entry_name.get().strip()
    unit = entry_unit.get().strip()
    code = entry_code.get().strip()

    if not all([article, name, unit, code]):
        messagebox.showwarning('Предупреждение', 'Заполнены не все поля!')
        return

    try:
        barcode_path = generate_barcode(code)
        template_path = create_template(barcode_path, article, name, unit)

        messagebox.showinfo('Успех!',
                            f'Шаблон с изображением штрих-кода и информацией\nуспешно сохранён в файле:\n{template_path}')
    except Exception as err:
        messagebox.showerror('Ошибка', str(err))


# Интерфейс программы
root = tk.Tk()
root.title('Генерация этикеток со штрих-кодами')

tk.Label(root, text='Артикул:').grid(row=0, column=0, sticky='w', padx=10, pady=5)
entry_article = tk.Entry(root, width=30)
entry_article.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text='Наименование товара:').grid(row=1, column=0, sticky='w', padx=10, pady=5)
entry_name = tk.Entry(root, width=30)
entry_name.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text='Единица измерения:').grid(row=2, column=0, sticky='w', padx=10, pady=5)
entry_unit = tk.Entry(root, width=30)
entry_unit.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text='Код штрих-кода:').grid(row=3, column=0, sticky='w', padx=10, pady=5)
entry_code = tk.Entry(root, width=30)
entry_code.grid(row=3, column=1, padx=10, pady=5)

generate_button = tk.Button(root, text="Создать этикетку", command=on_generate_click)
generate_button.grid(row=4, columnspan=2, pady=10)

root.mainloop()