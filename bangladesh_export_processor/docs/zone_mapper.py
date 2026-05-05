# -*- coding: utf-8 -*-
"""
Zone-based field mapper - uses fixed zones (in percentages) to extract field values
"""
from typing import Dict, List, Tuple, Optional
import re


class ZoneMapper:
    """
    Maps OCR text to fields using predefined zones (percentage-based)
    """
    
    # Field zones: (x1%, y1%, x2%, y2%) - percentages of image dimensions
    FIELD_ZONES = {
        'Номер документа': (5, 2, 40, 5),
        'Тип документа': (40, 2, 60, 5),
        'Код таможни/тариф': (60, 2, 85, 5),
        'Код режима': (5, 5, 30, 8),
        'Дата': (30, 5, 50, 8),
        'Код офиса экспорта': (50, 5, 70, 8),
        'Регистрационный номер экспортера': (70, 5, 90, 8),
        'Год': (90, 5, 100, 8),
        'Наименование экспортера': (5, 8, 50, 12),
        'Адрес экспортера': (5, 12, 50, 16),
        'Телефон экспортера': (50, 8, 70, 10),
        'Регистрационный номер BIN': (70, 8, 90, 12),
        'Наименование получателя/грузополучателя': (5, 16, 50, 20),
        'Адрес получателя': (5, 20, 50, 24),
        'Код страны получателя': (50, 16, 70, 18),
        'Страна происхождения': (70, 16, 90, 18),
        'Страна конечного получателя': (90, 16, 100, 18),
        'Декларант/Агент': (5, 24, 40, 28),
        'Адрес декларанта/агента': (5, 28, 40, 32),
        'Код агента': (40, 24, 60, 28),
        'Условия поставки': (60, 24, 80, 28),
        'Код условий поставки': (80, 24, 100, 28),
        'Наименование авиакомпании': (5, 32, 50, 36),
        'Код авиакомпании': (50, 32, 70, 36),
        'Код валюты': (70, 32, 80, 36),
        'Общая стоимость': (80, 32, 100, 36),
        'Курс валют': (70, 36, 90, 40),
        'Наименование банка': (5, 40, 50, 44),
        'Код банка': (50, 40, 70, 44),
        'Порт погрузки': (70, 40, 90, 44),
        'Код таможни/выпуска': (90, 40, 100, 44),
        'Сектор и фонд': (5, 44, 30, 48),
        'Номер места': (30, 44, 50, 48),
        'Тип упаковки': (50, 44, 70, 48),
        'Количество мест (ед)': (70, 44, 90, 48),
        'Код ТН ВЭД': (5, 48, 30, 52),
        'Описание товара': (30, 48, 70, 56),
        'Количество мест (ед.изм)': (70, 48, 90, 52),
        'Номер CRF/EXP': (5, 56, 40, 60),
        'Дата CRF/EXP': (40, 56, 60, 60),
        'NMB': (60, 56, 80, 60),
        'VM': (80, 56, 100, 60),
    }
    
    def __init__(self):
        self.field_mapping = {}
        
    def get_text_in_zone(self, ocr_results: List[Dict], 
                         x1_pct: float, y1_pct: float, 
                         x2_pct: float, y2_pct: float,
                         img_width: int, img_height: int) -> str:
        """
        Extract text within a zone
        
        Args:
            ocr_results: List of OCR results
            Zone percentages
            Image dimensions
            
        Returns:
            Concatenated text in zone
        """
        x1 = x1_pct / 100 * img_width
        y1 = y1_pct / 100 * img_height
        x2 = x2_pct / 100 * img_width
        y2 = y2_pct / 100 * img_height
        
        texts = []
        for result in ocr_results:
            bbox = result['bbox']
            # Get center of bbox
            cx = (bbox[0][0] + bbox[2][0]) / 2
            cy = (bbox[0][1] + bbox[2][1]) / 2
            
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                text = result['text'].strip()
                if text:
                    texts.append(text)
        
        return ' '.join(texts)
    
    def map_from_zones(self, ocr_results: List[Dict], img_width: int, img_height: int) -> Dict[str, str]:
        """
        Map OCR results to fields using zones
        
        Args:
            ocr_results: List of OCR results
            Image dimensions
            
        Returns:
            Dictionary of field values
        """
        mapped = {}
        
        for field_name, (x1, y1, x2, y2) in self.FIELD_ZONES.items():
            text = self.get_text_in_zone(ocr_results, x1, y1, x2, y2, img_width, img_height)
            if text:
                mapped[field_name] = text
        
        return mapped


def test_zone_mapper():
    """Test zone mapper"""
    from ocr_reader import OCRReader
    from PIL import Image
    
    # Test on one image
    img_path = 'EXD 784-63264471.jpg'
    
    img = Image.open(img_path)
    width, height = img.size
    
    reader = OCRReader()
    results = reader.read_image(img_path)
    
    mapper = ZoneMapper()
    mapped = mapper.map_from_zones(results, width, height)
    
    print('Mapped fields:')
    for field, value in mapped.items():
        print(f'{field}: {value[:50]}...' if len(value) > 50 else f'{field}: {value}')


if __name__ == '__main__':
    test_zone_mapper()