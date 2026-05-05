# -*- coding: utf-8 -*-
"""
Модуль предобработки изображений для OCR
Функции:
1. Определение границ документа
2. Улучшение контраста и четкости
3. Конвертация в черно-белое
"""
import cv2
import numpy as np
from PIL import Image
import os


def detect_document_bounds(image_path: str) -> np.ndarray:
    """
    Определение границ документа на изображении
    """
    # Читаем через PIL (поддержка кириллицы)
    pil_img = Image.open(image_path)
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Если изображение уже достаточно чистое (скан), не обрезаем
    # Проверяем соотношение сторон - если близкое к A4, не обрезаем
    h, w = img.shape[:2]
    aspect_ratio = w / h
    
    # A4 ratio is about 0.707, if close to that, likely a full document scan
    if 0.6 < aspect_ratio < 0.8:
        return img
    
    # Конвертируем в градации серого
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Размытие для сглаживания шума
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Находим границы (Canny)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Находим контуры
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return img
    
    # Находим самый большой контур (документ)
    largest = max(contours, key=cv2.contourArea)
    
    # Проверяем размер контура - если он занимает > 90% изображения, не обрезаем
    img_area = w * h
    contour_area = cv2.contourArea(largest)
    
    if contour_area > 0.9 * img_area:
        return img
    
    # Упрощаем контур до прямоугольника
    peri = cv2.arcLength(largest, True)
    approx = cv2.approxPolyDP(largest, 0.02 * peri, True)
    
    if len(approx) >= 4:
        x, y, w_box, h_box = cv2.boundingRect(approx)
        # Обрезаем только если найденная область значительно меньше оригинала
        if w_box < w * 0.95 or h_box < h * 0.95:
            cropped = img[y:y+h_box, x:x+w_box]
            return cropped
    
    return img


def enhance_image(img: np.ndarray) -> np.ndarray:
    """
    Улучшение контраста и резкости изображения
    """
    # Конвертируем в градации серого
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # CLAHE - адаптивное увеличение контраста
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # Удаление шума
    denoised = cv2.medianBlur(enhanced, 3)
    
    # Увеличение резкости
    kernel = np.array([[-1,-1,-1], [-1, 9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    return sharpened


def make_black_white(img: np.ndarray) -> np.ndarray:
    """
    Конвертация в черно-белое (бинаризация)
    """
    _, binary = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def preprocess_image(image_path: str, output_path: str = None) -> np.ndarray:
    """
    Полная предобработка изображения для OCR
    """
    # Этап 1: Определение границ
    cropped = detect_document_bounds(image_path)
    
    # Этап 2: Улучшение качества
    enhanced = enhance_image(cropped)
    
    # Этап 3: Черно-белое
    bw = make_black_white(enhanced)
    
    # Сохранение
    if output_path:
        pil_img = Image.fromarray(bw)
        pil_img.save(output_path)
    
    return bw


def process_all_images(input_dir: str, output_dir: str):
    """
    Обработка всех изображений из папки
    """
    os.makedirs(output_dir, exist_ok=True)
    
    jpg_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.jpg')]
    
    print(f"Найдено {len(jpg_files)} файлов для обработки")
    
    for filename in jpg_files:
        input_path = os.path.join(input_dir, filename)
        output_filename = f"processed_{filename}"
        output_path = os.path.join(output_dir, output_filename)
        
        try:
            preprocess_image(input_path, output_path)
            print(f"Обработан: {filename}")
        except Exception as e:
            print(f"Ошибка при обработке {filename}: {e}")
    
    print(f"\nГотово! Обработанные изображения сохранены в: {output_dir}")


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    input_dir = os.path.join(base_dir, "samples")
    output_dir = os.path.join(base_dir, "photo")
    
    print("=" * 50)
    print("ПРЕДОБРАБОТКА ИЗОБРАЖЕНИЙ ДЛЯ OCR")
    print("=" * 50)
    print(f"Входная папка: {input_dir}")
    print(f"Выходная папка: {output_dir}")
    
    if os.path.exists(input_dir):
        process_all_images(input_dir, output_dir)
    else:
        print(f"Папка не найдена: {input_dir}")
