# -*- coding: utf-8 -*-
"""
Extra Processor Module - обработка EXD-файлов из папки "доп запрос"
"""
import os
import glob
from typing import List, Dict
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

from .main import BangladeshExportProcessor


def select_directory() -> str:
    """Показать диалог выбора каталога и вернуть путь."""
    root = tk.Tk()
    root.withdraw()  # Скрыть главное окно

    folder_selected = filedialog.askdirectory(
        title="Выберите папку с EXD-файлами",
        initialdir=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'доп запрос')
    )

    root.destroy()
    return folder_selected if folder_selected else ""


def find_exd_images(root_dir: str) -> List[Dict[str, str]]:
    """Рекурсивно найти все изображения с 'EXD' в названии."""
    images = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        pattern = os.path.join(root_dir, '**', ext)
        for path in glob.glob(pattern, recursive=True):
            if 'EXD' in os.path.basename(path).upper():
                base_name = os.path.splitext(os.path.basename(path))[0]
                # Проверить, есть ли уже перевод
                xlsx_path = os.path.join(os.path.dirname(path), f"{base_name} (перевод).xlsx")
                has_translation = os.path.exists(xlsx_path)

                images.append({
                    'path': path,
                    'folder': os.path.dirname(path),
                    'filename': os.path.basename(path),
                    'has_translation': has_translation
                })
    return sorted(images, key=lambda x: x['folder'])


def show_file_selector(files: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Показать Tkinter-окно с чеклистом для выбора файлов."""
    selected = []

    root = tk.Tk()
    root.title("Выберите файлы для обработки")
    root.geometry("750x500")

    # Заголовок
    label = ttk.Label(root, text=f"Найдено файлов: {len(files)}", font=('Arial', 12, 'bold'))
    label.pack(pady=10)

    # Treeview с чекбоксами
    columns = ('Выбрать', 'Папка', 'Файл')
    tree = ttk.Treeview(root, columns=columns, show='headings', height=18)

    tree.heading('Выбрать', text='✓')
    tree.heading('Папка', text='Папка')
    tree.heading('Файл', text='Файл')

    tree.column('Выбрать', width=50, anchor='center')
    tree.column('Папка', width=300)
    tree.column('Файл', width=350)

    # Переменные для чекбоксов
    checkvars = {}

    for i, f in enumerate(files, 1):
        # Если перевод уже есть - галочка по умолчанию НЕ стоит
        has_trans = f.get('has_translation', False)
        var = tk.BooleanVar(value=not has_trans)
        checkvars[i] = var
        folder = os.path.basename(f['folder'])
        # Добавить маркер если перевод уже есть
        filename_display = f['filename'] + (' ✓' if has_trans else '')
        checkbox = '☐' if has_trans else '☑'
        tree.insert('', 'end', values=(checkbox, folder, filename_display), tags=('checked',))

    # Скроллбар
    vsb = ttk.Scrollbar(root, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)

    tree.pack(side='left', fill='both', expand=True, padx=10, pady=5)
    vsb.pack(side='right', fill='y')

    # Кнопки
    def update_checkboxes():
        for i, var in checkvars.items():
            item = tree.get_children()[i-1]
            folder = tree.item(item)['values'][1]
            original_filename = files[i-1]['filename']
            has_trans = files[i-1].get('has_translation', False)
            filename_with_marker = original_filename + (' ✓' if has_trans else '')

            if var.get():
                tree.item(item, values=('☑', folder, filename_with_marker))
            else:
                tree.item(item, values=('☐', folder, filename_with_marker))

    def on_confirm():
        for i, f in enumerate(files, 1):
            if checkvars[i].get():
                selected.append(f)
        root.destroy()

    def on_select_all():
        for var in checkvars.values():
            var.set(True)
        update_checkboxes()

    def on_deselect_all():
        for var in checkvars.values():
            var.set(False)
        update_checkboxes()

    def on_row_click(event):
        """Обработка клика по строке - переключение галочки."""
        item_id = tree.identify_row(event.y)
        if item_id:
            # Получить индекс элемента (0-based)
            idx = tree.index(item_id)
            # Переключить галочку (индексы в checkvars начинаются с 1)
            checkvars[idx + 1].set(not checkvars[idx + 1].get())
            # Обновить отображение
            update_checkboxes()

    # Привязать клик к Treeview
    tree.bind('<Button-1>', on_row_click)

    btn_frame = ttk.Frame(root)
    btn_frame.pack(pady=10)

    ttk.Button(btn_frame, text="Выбрать все", command=on_select_all).pack(side='left', padx=5)
    ttk.Button(btn_frame, text="Снять все", command=on_deselect_all).pack(side='left', padx=5)
    ttk.Button(btn_frame, text="Обработать выбранные", command=on_confirm).pack(side='left', padx=20)

    root.mainloop()
    return selected


def process_selected_files(files: List[Dict[str, str]]) -> List[str]:
    """Обработать выбранные файлы и создать Excel рядом с каждым."""
    outputs = []

    print(f"\nОбработка {len(files)} файлов...")

    for f in files:
        input_path = f['path']
        folder = f['folder']
        filename = f['filename']

        print(f"  → {filename}")

        processor = BangladeshExportProcessor(folder, folder)

        try:
            output_path = processor.process_and_save(input_path)
            outputs.append(output_path)
            print(f"    Создан: {os.path.basename(output_path)}")
        except Exception as e:
            print(f"    Ошибка: {e}")

    return outputs


def run_extra_processor(input_dir: str) -> None:
    """Запустить обработку EXD-файлов из указанной директории."""
    # Если путь не указан или не существует - показать диалог выбора
    if not input_dir or not os.path.exists(input_dir):
        print("Выберите папку с EXD-файлами...")
        input_dir = select_directory()
        if not input_dir:
            print("Папка не выбрана")
            return

    files = find_exd_images(input_dir)

    if not files:
        print("EXD-файлы не найдены")
        return

    print(f"\nНайдено {len(files)} файлов с 'EXD':")
    for f in files:
        print(f"  [{os.path.basename(f['folder'])}] {f['filename']}")

    selected = show_file_selector(files)

    if not selected:
        print("Не выбрано файлов для обработки")
        return

    outputs = process_selected_files(selected)
    print(f"\nОбработано файлов: {len(outputs)}")


if __name__ == '__main__':
    test_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'доп запрос')
    if os.path.exists(test_dir):
        run_extra_processor(test_dir)
    else:
        print(f"Тестовая папка не найдена: {test_dir}")