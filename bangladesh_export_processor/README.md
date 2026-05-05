# Bangladesh Export Declaration Processor

Обработка экспортных деклараций Bangladesh с OCR и переводом на русский язык.

## Структура проекта

```
bangladesh_export_processor/
├── exdBD.py                 # Основной entry point
├── requirements.txt         # Зависимости Python
├── src/                    # Исходный код
│   ├── __init__.py
│   ├── main.py             # Основной процессор
│   ├── ocr_reader.py      # OCR (Tesseract с TSV координатами)
│   ├── field_mapper.py    # Маппинг полей (label-based подход)
│   ├── translator.py      # Перевод на русский
│   ├── excel_writer.py    # Запись в Excel
│   ├── pdf_processor.py   # Обработка PDF
│   └── image_preprocessor.py # Предобработка изображений
├── samples/                # Оригинальные сканы (JPG)
├── docs/                   # Документация и анализ
└── photo/                  # Обработанные изображения
```

## Модули

### exdBD.py
Основной entry point. Запускает обработку всех файлов из указанной папки.

**Использование:**
```bash
python exdBD.py                    # Обработать data/input
python exdBD.py samples            # Обработать папку samples
python exdBD.py <file.jpg>         # Обработать один файл
python exdBD.py --test              # Тестовый режим
```

### src/ocr_reader.py
OCR модуль на базе Tesseract.

**Особенности:**
- Использует `--psm 6` для многострочного распознавания
- Парсит TSV вывод для получения реальных координат bbox
- Поддерживает JPG, PNG, PDF

**Пример использования:**
```python
from ocr_reader import OCRReader
reader = OCRReader(use_tesseract=True, use_preprocessing=False)
results = reader.read_image('file.jpg')
# results = [{'text': '...', 'bbox': ((x1,y1), (x2,y2), ...), 'confidence': 0.95}]
```

### src/field_mapper.py
Маппинг OCR текста в структурированные поля (48 полей декларации).

**Подход:**
- Поиск по LABEL (например "2 Consignor/Exporter")
- Извлечение значения относительно позиции label
- Поддержка сложных полей с подполями (31, 44)

**Исправления (v4):**
- Поле 8: содержит ВСЁ ВМЕСТЕ (название + адрес + страна)
- Поле 34: Gross weight(kg) (НЕ C.O. Code!)
- Поле 37: CPC = "1072"
- Поля 31 и 35: РАЗНЫЕ (разные Y-диапазоны!)

### src/main.py
Координирует работу всех модулей:
1. OCR → 2. Field mapping → 3. Translation → 4. Excel export

### src/translator.py
Перевод полей с английского на русский используя словарь.

### src/excel_writer.py
Запись результатов в Excel файл с форматированием.

### src/image_preprocessor.py
Предобработка изображений (CLAHE, бинаризация).

## Поля документа (48 полей)

| № | Поле | Label паттерн |
|---|------|---------------|
| 1 | Тип документа | `BILL OF ENTRY / EXPORT` |
| 2 | Экспортер | `2 Consignor/Exporter` |
| 8 | Получатель (всё вместе) | `8 Consignee/importer` |
| 14 | Декларант | `14 Declarant/Agent` |
| 21 | Авиакомпания | `21 Carrier` |
| 31 | Packages (сложное) | `31 Packages` |
| 33 | HS Code | `33 HS Code` |
| 34 | Gross weight | `34 C.O. Code` |
| 35 | Description | `Description of Goods` |
| 37 | CPC | `37 CPC` |
| 44 | Add. info (сложное) | `44 Add. info` |
| 46 | Assessable Value | `46 fem Value` |
| ... | ... | ... |

## Требования

- Python 3.12+
- Tesseract 5.4.0+ (Windows: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
- openpyxl
- Pillow
- pdf2image (для PDF)

## Установка

```bash
pip install -r requirements.txt
```

## Тестирование

```bash
cd bangladesh_export_processor
python exdBD.py samples
```

Обработает все JPG файлы из папки `samples/` и создаст Excel файлы с переводом.

## История версий

### v4 (текущая)
- Label-based маппинг вместо привязки к названиям компаний
- Исправленная структура полей (34=Gross weight, 37=CPC)
- Реальные bbox координаты из Tesseract TSV

### v3
- Позиционный маппинг с фиксированными координатами
- Высокая точность (46/48), но неправильный подход

## Лицензия

MIT