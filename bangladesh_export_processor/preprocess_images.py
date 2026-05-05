# -*- coding: utf-8 -*-
"""Предобработка изображений деклараций: до и после"""
import cv2
import numpy as np
from PIL import Image
import os

def preprocess_declaration(image_path: str, output_path: str = None) -> np.ndarray:
    """
    Предобработка изображения декларации
    1. Определение границ документа
    2. Улучшение контраста
    3. Черно-белое преобразование
    """
    # Загрузка изображения через PIL (поддержка кириллицы)
    pil_img = Image.open(image_path)
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # === ЭТАП 1: Определение границ документа ===
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Размытие для сглаживания
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Находим границы (Canny)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Находим контуры
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Находим самый большой контур (документ)
        largest = max(contours, key=cv2.contourArea)
        
        # Упрощаем контур до прямоугольника
        peri = cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, 0.02 * peri, True)
        
        if len(approx) >= 4:
            # Обрезаем по контуру
            x, y, w, h = cv2.boundingRect(approx)
            cropped = img[y:y+h, x:x+w]
        else:
            cropped = img
    else:
        cropped = img
    
    # === ЭТАП 2: Улучшение качества ===
    # Конвертируем в градации серого
    gray_crop = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    
    # CLAHE - адаптивное увеличение контраста
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray_crop)
    
    # Удаление шума
    denoised = cv2.medianBlur(enhanced, 3)
    
    # Бинаризация (черно-белое)
    _, binary = cv2.threshold(denoised, 127, 255, cv2.THRESH_BINARY)
    
    # Сохраняем если указан путь
    if output_path:
        cv2.imwrite(output_path, binary)
        print(f"Сохранено: {output_path}")
    
    return binary


def main():
    # Пути
    # Попробуем новый путь без кириллицы, и если не найден -- fallback на старый
    examples_dir = r"D:\pythonProject\BD_exd\bangladesh_export_processor\samples"
    if not os.path.isdir(examples_dir):
        examples_dir = r"D:\pythonProject\BD_exd\bangladesh_export_processor\примеры"
    input_image = os.path.join(examples_dir, "EXD 784-63264471.jpg")
    output_image = os.path.join(examples_dir, "processed_EXD_784-63264471.jpg")
    
    print(f"Исходное изображение: {input_image}")
    print(f"Обработанное изображение: {output_image}")
    
    # Обработка
    processed = preprocess_declaration(input_image, output_image)
    
    print(f"\nРазмер исходного: ", end="")
    img_orig = Image.open(input_image)
    print(f"{img_orig.size}")
    
    print(f"Размер обработанного: {processed.shape[1]}x{processed.shape[0]}")
    
    # Показываем обе картинки
    print("\n=== ИСХОДНОЕ ИЗОБРАЖЕНИЕ ===")
    display(img_orig)
    
    print("\n=== ОБРАБОТАННОЕ ИЗОБРАЖЕНИЕ ===")
    display(Image.fromarray(processed))


if __name__ == '__main__':
    main()
