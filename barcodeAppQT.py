import os
import shutil
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox
from tkinter import messagebox, filedialog
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image as PilImage
from PIL import ImageDraw, ImageFont
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Image as RlImage

counter = 0

# Настройки шрифта и размеров
font_size = 65
font_type = "arial.ttf"
img_width_cm = 10
img_height_cm = 5
dpi = 300
px_per_inch = dpi / 2.54
img_width_px = int(img_width_cm * px_per_inch)
img_height_px = int(img_height_cm * px_per_inch)


def clear_temp_directory():
    temp_dir = 'temp'
    try:
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
    except Exception as e:
        print(f"Ошибка при очистке папки: {e}")


def generate_barcode(code_number):
    global counter

    if not os.path.exists('temp'):
        os.mkdir('temp')

    ean = Code128(str(code_number), writer=ImageWriter())
    filename = f'barcode_{counter}'

    full_path = os.path.join('temp', filename)
    write_options = {
        'module_width': 0.5,  # Ширина одного элемента штрихкода (чем меньше значение, тем тоньше линии)
        'module_height': 10,  # Высота штрихкода в пикселях
        'font_size': 12,  # Размер шрифта внизу штрихкода
        'text_distance': 5  # Расстояние между штрихкодом и текстом снизу
    }
    ean.save(full_path, write_options)
    counter += 1
    return full_path + '.png'


def create_template(barcode_image_path, article, name, unit):
    img = PilImage.new("RGB", (img_width_px, img_height_px), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_type, size=font_size)

    text_y_offset = 0
    text_bbox = font.getbbox(article)
    text_width = text_bbox[2] - text_bbox[0]
    center_x = (img.width - text_width) // 2
    draw.text((center_x, text_y_offset), f"{article}", fill="black", font=font)

    # Логика переноса строки названия
    lines = []
    words = name.split()
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        bbox = font.getbbox(test_line.strip())
        line_width = bbox[2] - bbox[0]
        if line_width > img.width - 20:
            lines.append(current_line.strip())
            current_line = word + " "
        else:
            current_line = test_line
    if current_line.strip():
        lines.append(current_line.strip())

    y_pos = (text_y_offset + 10) + font_size * 1.5
    for i, line in enumerate(lines[:3]):
        text_bbox = font.getbbox(line)
        text_width = text_bbox[2] - text_bbox[0]
        center_x = (img.width - text_width) // 2
        draw.text((center_x, y_pos), line, fill="black", font=font)
        y_pos += font_size * 1.2

    # Единица измерения в правом нижнем углу
    text_bbox = font.getbbox(unit)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    right_bottom_position_x = img.width - text_width - 100
    right_bottom_position_y = img.height - text_height - 100
    draw.text((right_bottom_position_x, right_bottom_position_y),
              f"{unit}",
              fill="black",
              font=ImageFont.truetype(font_type, size=70))

    # Штрих-код снизу слева
    bc_img = PilImage.open(barcode_image_path)
    scale_factor_width = 1   #1.8
    scale_factor_height = 1   #1.1
    new_bc_size = (int(bc_img.width * scale_factor_width), int(bc_img.height * scale_factor_height))
    resized_bc = bc_img.resize(new_bc_size, resample=PilImage.LANCZOS)
    position_x = 0
    position_y = img.height - resized_bc.height + 45
    img.paste(resized_bc, (position_x, position_y))
    template_filename = f'template_{counter}.png'
    full_path = os.path.join('temp', template_filename)
    img.save(full_path)
    return full_path


def save_images_to_pdf(image_paths, output_pdf_path):
    page_width = 1339  # Переход к более мелким размерам приводит к падению.
    page_height = 746  # Более крупные размеры уменьшают макет.

    doc = SimpleDocTemplate(output_pdf_path, pagesize=(page_width, page_height))  # Задание нужного размера страницы
    elements = []

    for path in image_paths:
        img = RlImage(path, width=img_width_px, height=img_height_px)
        elements.append(img)

    doc.build(elements)


def on_generate_click(self):
    article = self.entry_article.text().strip()
    name = self.entry_name.text().strip()
    unit = self.entry_unit.text().strip()
    code = self.entry_code.text().strip()

    if not all([article, name, unit, code]):
        QMessageBox.warning(self, 'Предупреждение', 'Заполнены не все поля!', QMessageBox.Ok)
        return

    try:
        barcode_path = generate_barcode(code)
        template_path = create_template(barcode_path, article, name, unit)
        save_images_to_pdf([template_path], 'output.pdf')  # Сохраняем в PDF сразу одну этикетку
        QMessageBox.information(self, 'Успех!',
                                f'Шаблон с изображением штрих-кода и информацией\n'
                                f'успешно сохранён в файле:\n'
                                f'"output.pdf"', QMessageBox.Ok)
    except Exception as err:
        QMessageBox.critical(self, 'Ошибка', str(err), QMessageBox.Ok)
    clear_temp_directory()


def open_excel_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", ".xls .xlsx")])
    if not file_path:
        return

    df = pd.read_excel(file_path)

    required_columns = ['Артикул', 'Наименование', 'Единица измерения', 'Штрихкод']
    missing_cols = set(required_columns) - set(df.columns)
    if len(missing_cols) > 0:
        messagebox.showerror('Ошибка', f"В файле отсутствуют обязательные колонки: {missing_cols}")
        return

    # Добавляем в ПДФ
    image_paths = []

    for _, row in df.iterrows():
        article = str(row['Артикул']).strip()
        name = str(row['Наименование']).strip()
        unit = str(row['Единица измерения']).strip()
        code = row['Штрихкод']  #.strip()

        if not all([article, name, unit, code]):
            continue  # Пропускаем пустые строки

        try:
            barcode_path = generate_barcode(code)
            template_path = create_template(barcode_path, article, name, unit)
            image_paths.append(template_path)  # Собираем пути всех созданных изображений
        except Exception as err:
            messagebox.showerror('Ошибка', f"Произошла ошибка при обработке записи: {err}")

        if image_paths:
            save_images_to_pdf(image_paths, 'output.pdf')  # Сохраняем все этикетки в один PDF
            # messagebox.showinfo('Готово!', 'Этикетки успешно собраны в PDF.')
        else:
            messagebox.showwarning('Предупреждение', 'Нет валидных записей для создания этикеток.')
    messagebox.showinfo('Готово!', 'Этикетки успешно собраны в PDF.')
    clear_temp_directory()


if not os.path.exists('temp'):
    os.mkdir('temp')

# Интерфейс программы
class BarcodeLabelGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI(on_generate_click(self))

    def initUI(self, o_g_c):
        grid_layout = QGridLayout()

        # Заголовок окна
        self.setWindowTitle('Генерация этикеток со штрих-кодами')

        # Добавляем метки и поля ввода
        article_label = QLabel('Артикул:')
        entry_article = QLineEdit()
        grid_layout.addWidget(article_label, 0, 0)
        grid_layout.addWidget(entry_article, 0, 1)

        name_label = QLabel('Наименование товара:')
        entry_name = QLineEdit()
        grid_layout.addWidget(name_label, 1, 0)
        grid_layout.addWidget(entry_name, 1, 1)

        unit_label = QLabel('Единица измерения:')
        entry_unit = QLineEdit()
        grid_layout.addWidget(unit_label, 2, 0)
        grid_layout.addWidget(entry_unit, 2, 1)

        code_label = QLabel('Код штрих-кода:')
        entry_code = QLineEdit()
        grid_layout.addWidget(code_label, 3, 0)
        grid_layout.addWidget(entry_code, 3, 1)

        # Кнопки
        generate_button = QPushButton('Создать этикетку')
        open_file_button = QPushButton('Открыть файл Excel')

        generate_button.clicked.connect(self.on_generate_click)
        open_file_button.clicked.connect(self.open_excel_file)

        grid_layout.addWidget(generate_button, 4, 0, 1, 2)
        grid_layout.addWidget(open_file_button, 5, 0, 1, 2)

        # Устанавливаем сеточную компоновку в качестве основной
        self.setLayout(grid_layout)


def main():
    app = QApplication(sys.argv)
    ex = BarcodeLabelGenerator()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
