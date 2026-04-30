# -*- coding: utf-8 -*-
"""
Hybrid field mapper - uses numeric field codes as anchors and reads text nearby
"""
from typing import Dict, List, Tuple, Optional
import re


class HybridMapper:
    """
    Maps OCR results using numeric field codes as anchors
    """
    
    # Field codes and their names (from Bangladesh Export Declaration form)
    FIELD_CODES = {
        '101': 'Код офиса экспорта',
        '102': 'Регистрационный номер экспортера',
        '103': 'Год',
        '104': 'Наименование экспортера',
        '105': 'Адрес экспортера',
        '106': 'Телефон экспортера',
        '107': 'Регистрационный номер BIN',
        '15': 'Страна происхождения',
        '17': 'Страна конечного получателя',
        '20': 'Условия поставки',
        '21': 'Наименование авиакомпании',
        '22': 'Код валюты',
        '23': 'Общая стоимость',
        '24': 'Курс валют',
        '25': 'Тип транспорта',
        '26': 'Порт погрузки',
        '29': 'Код таможни/выпуска',
        '31': 'Номер места',
        '32': 'Номер товара',
        '33': 'Код ТН ВЭД',
        '34': 'Код страны происхождения',
        '35': 'Вес брутто',
        '36': 'Код агента',
        '37': 'Код CPC',
        '38': 'Вес нетто',
        '40': 'Описание товара',
        '41': 'Количество',
        '42': 'Количество мест',
        '43': 'VM',
        '44': 'Дополнительная информация',
        '45': 'Код товара',
        '46': 'Таможенная стоимость',
        '122': 'Код авиакомпании',
    }
    
    # Additional field mappings without numeric codes
    TEXT_FIELDS = {
        'consignor': 'Наименование экспортера',
        'consignee': 'Наименование получателя/грузополучателя',
        'declarant': 'Декларант/Агент',
        'bank': 'Наименование банка',
        'customs': 'Код таможни/тариф',
    }
    
    def __init__(self):
        pass
    
    def find_code_position(self, ocr_results: List[Dict], code: str) -> Optional[Tuple[int, int]]:
        """Find position of field code"""
        for result in ocr_results:
            text = result['text'].strip()
            if text == code:
                bbox = result['bbox']
                return (bbox[0][0], bbox[0][1])
        return None
    
    def get_text_near_position(self, ocr_results: List[Dict], 
                               x: int, y: int, 
                               x_offset: int = 150,
                               direction: str = 'right',
                               y_tolerance: int = 40) -> str:
        """Get text near position (to the right or left)"""
        texts = []
        for result in ocr_results:
            bbox = result['bbox']
            rx = (bbox[0][0] + bbox[2][0]) / 2
            ry = (bbox[0][1] + bbox[2][1]) / 2
            
            if direction == 'right':
                # Text to the right of anchor
                if x < rx < x + x_offset and abs(ry - y) < y_tolerance:
                    text = result['text'].strip()
                    if text and len(text) > 1:
                        texts.append(text)
            else:
                # Text to the left of anchor
                if x - x_offset < rx < x and abs(ry - y) < y_tolerance:
                    text = result['text'].strip()
                    if text and len(text) > 1:
                        texts.append(text)
        
        return ' '.join(texts[:2])  # Limit to 2 texts
    
    def find_text_label(self, ocr_results: List[Dict], patterns: List[str]) -> Optional[Tuple[int, int]]:
        """Find position of text label matching patterns"""
        for result in ocr_results:
            text = result['text'].strip().lower()
            for pattern in patterns:
                if pattern.lower() in text:
                    bbox = result['bbox']
                    return (bbox[0][0], bbox[0][1])
        return None
    
    def map_hybrid(self, ocr_results: List[Dict]) -> Dict[str, str]:
        """Map OCR results using hybrid approach"""
        mapped = {}
        
        # 1. Try numeric codes first
        for code, field_name in self.FIELD_CODES.items():
            pos = self.find_code_position(ocr_results, code)
            if pos:
                # Try right first, then left
                value = self.get_text_near_position(ocr_results, pos[0], pos[1], x_offset=200, direction='right')
                if not value:
                    value = self.get_text_near_position(ocr_results, pos[0], pos[1], x_offset=300, direction='left')
                if value:
                    mapped[field_name] = value
        
        # 2. Try text labels
        label_map = {
            'Наименование экспортера': ['consignor', 'exporter'],
            'Наименование получателя/грузополучателя': ['consignee', 'buyer'],
            'Декларант/Агент': ['declarant', 'agent'],
            'Наименование банка': ['bank'],
            'Код таможни/тариф': ['custom house'],
        }
        
        for field_name, patterns in label_map.items():
            pos = self.find_text_label(ocr_results, patterns)
            if pos:
                value = self.get_text_near_position(ocr_results, pos[0], pos[1], x_offset=300)
                if value:
                    mapped[field_name] = value
        
        return mapped


def test_hybrid_mapper():
    """Test hybrid mapper"""
    from ocr_reader import OCRReader
    
    img_path = 'EXD 784-63264471.jpg'
    
    reader = OCRReader()
    results = reader.read_image(img_path)
    
    mapper = HybridMapper()
    mapped = mapper.map_hybrid(results)
    
    print('Hybrid mapped fields:')
    for field, value in mapped.items():
        print(f'{field}: {value[:50]}...' if len(value) > 50 else f'{field}: {value}')


if __name__ == '__main__':
    test_hybrid_mapper()