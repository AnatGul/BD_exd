# -*- coding: utf-8 -*-
"""
Enhanced Field Mapper v4 - Label-based positional mapping
Based on corrected document structure from EXD analysis
"""
import re
from typing import Dict, List, Optional, Tuple


class FieldMapper:
    """
    Maps extracted OCR text to structured declaration fields using label-based approach
    """
    
    # Label definitions: pattern -> field name
    # Key changes from v3:
    # - Search by LABELS (like "2 Consignor/Exporter", not company names)
    # - Value extraction relative to label position
    # - Correct field structure (34=Gross weight, not C.O. Code!)
    # - Field 8 contains ALL together (name + address + country)
    # - Field 35 is separate from field 31
    
    LABEL_DEFINITIONS = {
        # === Поле 1: Шапка документа ===
        'Тип документа': {
            'label_pattern': r'BILL\s*OF\s*ENTRY\s*/\s*EXPORT',
            'label_y_range': (20, 60),
            'value_pos': 'same_line',
        },
        'Код таможни/тариф': {
            'label_pattern': r'OFFICE\s*OF\s*DISPATCH',
            'label_y_range': (20, 60),
            'value_pos': 'same_line',
        },
        'Код режима': {
            'label_pattern': r'DECLARATION\s*\[?\d{3}\]?',
            'label_y_range': (20, 60),
            'value_pos': 'same_line',
        },
        
        # === Поле 2: Экспортер ===
        'Наименование экспортера': {
            'label_pattern': r'2\s+Consignor\s*/\s*Exporter',
            'label_y_range': (150, 250),
            'value_pos': 'below',
            'value_y_offset': (40, 100),
            'value_x_range': (200, 1200),
        },
        'Регистрационный номер BIN': {
            'label_pattern': r'BIN:\s*([0-9\-]+)',
            'label_y_range': (150, 250),
            'value_pos': 'same_line_right',
            'value_x_offset': (50, 200),
        },
        
        # === Поле 3: Дата ===
        'Дата': {
            'label_pattern': r'Registration|[0-9]{2}/[0-9]{2}/2026',
            'label_y_range': (210, 280),
            'value_pos': 'below',
            'value_y_offset': (20, 50),
            'value_x_range': (1700, 2400),
        },
        'Регистрационный номер экспортера': {
            'label_pattern': r'C\s+\d+|Custom\s+House',
            'label_y_range': (250, 320),
            'value_pos': 'right_column',
            'value_x_range': (1700, 2400),
        },
        'Год': {
            'label_pattern': r'2026',
            'label_y_range': (200, 350),
            'value_pos': 'extract_year',
        },
        
        # === Поля 5-7: Справочные ===
        'Код офиса экспорта': {
            'label_pattern': r'^5\s+|5$',
            'label_y_range': (380, 450),
            'value_pos': 'right_column',
            'value_x_range': (1350, 1450),
        },
        'Код региона': {
            'label_pattern': r'^6\s+|6$',
            'label_y_range': (380, 450),
            'value_pos': 'right_column',
            'value_x_range': (1550, 1700),
        },
        'Номер коносамента': {
            'label_pattern': r'Agent\s+Reference|Reference',
            'label_y_range': (380, 480),
            'value_pos': 'right_column',
            'value_x_range': (1800, 2200),
        },
        
        # === Поле 8: Получатель (ВСЕ ВМЕСТЕ!) ===
        'Наименование получателя/грузополучателя': {
            'label_pattern': r'8\s+Consignee\s*/\s*importer',
            'label_y_range': (500, 600),
            'value_pos': 'below',
            'value_y_offset': (20, 160),
            'value_x_range': (200, 1200),
        },
        
        # === Поле 14: Декларант ===
        'Декларант/Агент': {
            'label_pattern': r'14\s+Dectarant\s*/\s*Agent',
            'label_y_range': (840, 920),
            'value_pos': 'below',
            'value_y_offset': (15, 30),
            'value_x_range': (200, 900),
        },
        'Код агента': {
            'label_pattern': r'AIN\s*([0-9]+)',
            'label_y_range': (840, 920),
            'value_pos': 'same_line_right',
            'value_x_offset': (50, 200),
        },
        
        # === Поля 15-17: Страны ===
        'Страна происхождения': {
            'label_pattern': r'Country\s*of\s*export',
            'label_y_range': (840, 900),
            'value_pos': 'right_column',
            'value_x_range': (1350, 1600),
        },
        'Адрес получателя': {
            'label_pattern': r'Country\s*of\s*origin',
            'label_y_range': (960, 1000),
            'value_pos': 'right_column',
            'value_x_range': (1350, 1600),
        },
        'Код страны получателя': {
            'label_pattern': r'Country\s*of\s*destination',
            'label_y_range': (960, 1000),
            'value_pos': 'right_column',
            'value_x_range': (1900, 2100),
        },
        
        # === Поля 18-23: Перевозчик ===
        'Код условий поставки': {
            'label_pattern': r'18\s+identity',
            'label_y_range': (1100, 1160),
            'value_pos': 'below',
            'value_y_offset': (20, 60),
            'value_x_range': (200, 1100),
        },
        'Условия поставки': {
            'label_pattern': r'20\s+Delivery\s+terms',
            'label_y_range': (1100, 1160),
            'value_pos': 'below',
            'value_y_offset': (60, 70),
            'value_x_range': (200, 1100),
        },
        'Наименование авиакомпании': {
            'label_pattern': r'21\s+Carrier',
            'label_y_range': (1210, 1260),
            'value_pos': 'below',
            'value_y_offset': (50, 70),
            'value_x_range': (200, 900),
        },
        'Код авиакомпании': {
            'label_pattern': r'CZ-\d+|CZ$|CA$',
            'label_y_range': (1150, 1300),
            'value_pos': 'below',
            'value_y_offset': (50, 80),
            'value_x_range': (200, 500),
        },
        'Код валюты': {
            'label_pattern': r'Currency',
            'label_y_range': (1210, 1260),
            'value_pos': 'right_column',
            'value_x_range': (1400, 1500),
        },
        'Общая стоимость': {
            'label_pattern': r'Total\s+invoiced\s+Value|Total\s+Value',
            'label_y_range': (1210, 1260),
            'value_pos': 'right_column',
            'value_x_range': (1500, 1700),
        },
        'Курс валют': {
            'label_pattern': r'Exch\.\s*rate',
            'label_y_range': (1210, 1260),
            'value_pos': 'right_column',
            'value_x_range': (1900, 2100),
        },
        
        # === Поля 25-30: Банк/Таможня ===
        'Порт погрузки': {
            'label_pattern': r'25\s+Place\s+of',
            'label_y_range': (1345, 1380),
            'value_pos': 'below',
            'value_y_offset': (50, 70),
            'value_x_range': (200, 900),
        },
        'Наименование банка': {
            'label_pattern': r'Bank\s+Name|of\s+The\s+Premier',
            'label_y_range': (1450, 1480),
            'value_pos': 'right_column',
            'value_x_range': (1350, 2100),
        },
        'Код банка': {
            'label_pattern': r'BDDAC|DAC',
            'label_y_range': (1345, 1450),
            'value_pos': 'right_column',
            'value_x_range': (800, 1100),
        },
        'Код таможни/выпуска': {
            'label_pattern': r'29\s+Office',
            'label_y_range': (1465, 1500),
            'value_pos': 'right_column',
            'value_x_range': (200, 700),
        },
        'Сектор и фонд': {
            'label_pattern': r'Sector\s*&\s*Fund',
            'label_y_range': (1500, 1530),
            'value_pos': 'right_column',
            'value_x_range': (1350, 1900),
        },
        
        # === Поля 31-40: Товары ===
        'Код ТН ВЭД': {
            'label_pattern': r'33\s+HS\s+Code',
            'label_y_range': (1560, 1620),
            'value_pos': 'right_column',
            'value_x_range': (1650, 1850),
        },
        'Тип упаковки': {
            'label_pattern': r'CT$|Carton',
            'label_y_range': (1700, 1800),
            'value_pos': 'right_column',
            'value_x_range': (850, 1000),
        },
        'Описание товара': {
            'label_pattern': r'Description\s+of\s+Goods',
            'label_y_range': (1920, 1970),
            'value_pos': 'below',
            'value_y_offset': (30, 50),
            'value_x_range': (200, 1200),
        },
        'Код CPC': {
            'label_pattern': r'37\s+CPC',
            'label_y_range': (1650, 1700),
            'value_pos': 'right_column',
            'value_x_range': (800, 1000),
        },
        'Количество мест (ед)': {
            'label_pattern': r'Nber\s*of\s*Pkgs',
            'label_y_range': (1700, 1800),
            'value_pos': 'right_column',
            'value_x_range': (450, 700),
        },
        'Количество мест (ед.изм)': {
            'label_pattern': r'Quantity|Units',
            'label_y_range': (1900, 2000),
            'value_pos': 'right_column',
            'value_x_range': (1750, 1950),
        },
        
        # === Поля 44-52: Дополнительно ===
        'Номер CRF/EXP': {
            'label_pattern': r'crrexp\s*No|cRFIEXPNo',
            'label_y_range': (2100, 2150),
            'value_pos': 'right_column',
            'value_x_range': (230, 500),
        },
        'Дата CRF/EXP': {
            'label_pattern': r'[0-9]{2}/[0-9]{2}/2026',
            'label_y_range': (2100, 2150),
            'value_pos': 'right_column',
            'value_x_range': (700, 1000),
        },
        'UPIUD': {
            'label_pattern': r'62132024017-074,88',
            'label_y_range': (1800, 2200),
            'value_pos': 'right_column',
            'value_x_range': (1650, 1850),
        },
        'NMB': {
            'label_pattern': r'\bNMB\b',
            'label_y_range': (2100, 2150),
            'value_pos': 'right_column',
            'value_x_range': (1750, 1950),
        },
        'VM': {
            'label_pattern': r'Vina\s*Ref|VM',
            'label_y_range': (1700, 1800),
            'value_pos': 'right_column',
            'value_x_range': (2000, 2200),
        },
        'Дополнительная стоимость': {
            'label_pattern': r'45\s+Adjustment',
            'label_y_range': (2150, 2190),
            'value_pos': 'right_column',
            'value_x_range': (2100, 2400),
        },
        'Общая декларируемая стоимость': {
            'label_pattern': r'46\s+fem\s+Value|Assessable\s+Value',
            'label_y_range': (2270, 2310),
            'value_pos': 'right_column',
            'value_x_range': (2000, 2300),
        },
        'Регистрационный номер': {
            'label_pattern': r'48\s+Doferred\s+payment|101P\d+',
            'label_y_range': (2270, 2310),
            'value_pos': 'right_column',
            'value_x_range': (2100, 2400),
        },
    }
    
    # Known values from training data
    KNOWN_VALUES = {
        'Наименование экспортера': ['187268206101', '196798206334', '000158825', 'Vintage Denim', 'GLORIA'],
        'Номер коносамента': ['2026 #733', '2026 #731', '2026 #760', '2026 #791', '2026 #792'],
        'Наименование получателя/грузополучателя': ['GLORIA JEANS', 'JSC', 'Глория Джинс'],
        'Адрес получателя': ['344090', 'ROSTOV', 'Россия'],
        'Код агента': ['101121479'],
        'Условия поставки': ['FOB', 'Дакка'],
        'Код валюты': ['USD'],
        'Курс валют': ['122.7'],
        'Наименование авиакомпании': ['China Southern', 'BDDAC'],
        'Код банка': ['101WH01', 'Premier Bank'],
        'Код ТН ВЭД': ['62046200', '61091000'],
        'Сектор и фонд': ['Garments', '043'],
        'Декларант/Агент': ['T.N. CORPORATION'],
    }
    
    STATIC_FIELDS = [
        'Номер документа',
        'Тип документа',
        'Код таможни/тариф',
        'Код режима',
        'Дата',
        'Код офиса экспорта',
        'Регистрационный номер экспортера',
        'Год',
        'Наименование экспортера',
        'Регистрационный номер BIN',
        'Адрес экспортера',
        'Телефон экспортера',
        'Наименование получателя/грузополучателя',
        'Адрес получателя',
        'Код страны получателя',
        'Страна происхождения',
        'Декларант/Агент',
        'Адрес декларанта/агента',
        'Код агента',
        'Условия поставки',
        'Код условий поставки',
        'Наименование авиакомпании',
        'Код авиакомпании',
        'Код валюты',
        'Общая стоимость',
        'Курс валют',
        'Наименование банка',
        'Код банка',
        'Порт погрузки',
        'Код таможни/выпуска',
        'Сектор и фонд',
        'Номер места',
        'Тип упаковки',
        'Код ТН ВЭД',
        'Описание товара',
        'Количество мест (ед)',
        'Количество мест (ед.изм)',
        'Код CPC',
        'Номер CRF/EXP',
        'Дата CRF/EXP',
        'UPIUD',
        'NMB',
        'VM',
        'Дополнительная стоимость',
        'Номер коносамента',
        'Дата коносамента',
        'Общая декларируемая стоимость',
        'Регистрационный номер',
    ]
    
    def __init__(self):
        """Initialize field mapper"""
        self.fields = {}
    
    def create_full_mapping(self) -> Dict[str, str]:
        """Create complete mapping with empty values"""
        return {field: "" for field in self.STATIC_FIELDS}
    
    def merge_with_static(self, mapped_data: Dict[str, str]) -> Dict[str, str]:
        """Merge mapped data with static field structure"""
        full = self.create_full_mapping()
        full.update(mapped_data)
        return full
    
    def find_known_values(self, ocr_text: str) -> Dict[str, str]:
        """Поиск известных значений из обучающей выборки в OCR тексте"""
        found = {}
        ocr_lower = ocr_text.lower()
        
        for field_name, known_values in self.KNOWN_VALUES.items():
            for value in known_values:
                if value.lower() in ocr_lower:
                    found[field_name] = value
                    break
        
        return found
    
    def _get_bbox_center(self, bbox: Tuple) -> Tuple[int, int]:
        """Get center coordinates of bbox"""
        x1, y1 = bbox[0]
        x2, y2 = bbox[1]
        return ((x1 + x2) // 2, (y1 + y2) // 2)
    
    def find_label(self, ocr_results: List[Dict], label_pattern: str, y_range: Tuple[int, int]) -> Optional[Dict]:
        """Найти label поля в OCR результатах"""
        for result in ocr_results:
            text = result.get('text', '')
            bbox = result.get('bbox', ((0,0), (0,0), (0,0), (0,0)))
            
            if not text:
                continue
            
            x_center, y_center = self._get_bbox_center(bbox)
            
            # Check Y range
            if y_range[0] <= y_center <= y_range[1]:
                if re.search(label_pattern, text, re.IGNORECASE):
                    return {
                        'text': text,
                        'bbox': bbox,
                        'y': y_center,
                        'x': x_center,
                    }
        
        return None
    
    def extract_value(self, ocr_results: List[Dict], label_info: Dict, 
                      value_pos: str, x_range: Tuple = None, 
                      x_offset: Tuple = None, y_offset: Tuple = None) -> str:
        """Извлечь значение поля из зоны относительно label"""
        
        if not label_info:
            return ""
        
        label_y = label_info['y']
        label_x = label_info['x']
        
        if value_pos == 'same_line':
            return label_info['text']
        
        zone_words = []
        
        for result in ocr_results:
            text = result.get('text', '')
            bbox = result.get('bbox', ((0,0), (0,0), (0,0), (0,0)))
            
            if not text:
                continue
            
            x_center, y_center = self._get_bbox_center(bbox)
            
            # Apply position-specific filters
            if value_pos == 'same_line_right':
                if abs(y_center - label_y) > 20:  # Same line tolerance
                    continue
                if x_center <= label_x:  # Must be to the right
                    continue
                zone_words.append(text)
            
            elif value_pos == 'below':
                if y_offset:
                    if not (label_y + y_offset[0] <= y_center <= label_y + y_offset[1]):
                        continue
                else:
                    if y_center <= label_y:
                        continue
                if x_range:
                    if not (x_range[0] <= x_center <= x_range[1]):
                        continue
                zone_words.append(text)
            
            elif value_pos == 'right_column':
                if x_range:
                    if not (x_range[0] <= x_center <= x_range[1]):
                        continue
                # Within reasonable Y distance from label
                if abs(y_center - label_y) > 80:
                    continue
                zone_words.append(text)
        
        return ' '.join(zone_words)[:100]  # Limit length
    
    def map_by_labels(self, ocr_results: List[Dict]) -> Dict[str, str]:
        """Основной метод маппинга через label-якоря"""
        mapped = {}
        
        for field_name, label_def in self.LABEL_DEFINITIONS.items():
            label_info = self.find_label(
                ocr_results,
                label_def['label_pattern'],
                label_def['label_y_range']
            )
            
            if label_info:
                value = self.extract_value(
                    ocr_results,
                    label_info,
                    label_def['value_pos'],
                    label_def.get('value_x_range'),
                    label_def.get('value_x_offset'),
                    label_def.get('value_y_offset')
                )
                
                if value and len(value) > 1:
                    mapped[field_name] = self._clean_value(field_name, value)
        
        return mapped
    
    def _clean_value(self, field_name: str, value: str) -> str:
        """Очистка значения поля"""
        # Remove extra spaces
        value = re.sub(r'\s+', ' ', value).strip()
        
        # Remove common OCR noise
        noise_patterns = [
            r'^\d+\s+\d+\s+\d+.*',  # Too many numbers
            r'.*[A-Z]{3,}.*[A-Z]{3,}.*',  # Multiple uppercase clusters
        ]
        
        for pattern in noise_patterns:
            if re.match(pattern, value) and len(value) > 30:
                # Try to extract meaningful part
                match = re.search(r'([A-Z][a-z].*?)(?=\s{2,}|$)', value)
                if match:
                    value = match.group(1)
        
        return value[:100]  # Limit length
    
    def detect_field_name(self, text: str) -> Optional[str]:
        """Detect field name from OCR text (fallback method)"""
        text = text.strip().upper()
        
        for pattern, label_def in self.LABEL_DEFINITIONS.items():
            label_pattern = label_def.get('label_pattern', '')
            if re.search(label_pattern, text, re.IGNORECASE):
                return pattern
        
        return None
    
    def map_extracted_data(self, ocr_results: List[Dict]) -> Dict[str, str]:
        """Map OCR results to structured fields using label-based approach"""
        
        # First try label-based mapping
        mapped = self.map_by_labels(ocr_results)
        
        # Fallback to text-based pattern matching for fields not found
        SKIP_LABELS = {'BIN:', 'TIN:', 'AIN:', 'NIA', 'CE', 'C.D.', 'Country'}
        
        for i, result in enumerate(ocr_results):
            text = result['text'].strip()
            if not text:
                continue
            
            field_name = self.detect_field_name(text)
            
            if field_name and field_name not in mapped:
                name_fields = {'Наименование экспортера', 'Наименование получателя/грузополучателя'}
                values = []
                
                for j in range(i + 1, min(i + 3, len(ocr_results))):
                    next_text = ocr_results[j]['text'].strip()
                    next_field = self.detect_field_name(next_text)
                    if next_field and next_field not in name_fields:
                        break
                    if next_text and not any(skip in next_text.upper() for skip in SKIP_LABELS):
                        values.append(next_text)
                
                if field_name in name_fields and values:
                    mapped[field_name] = values[0]
                elif not values:
                    mapped[field_name] = text
                else:
                    mapped[field_name] = text + " " + " ".join(values)
        
        return mapped


def test_mapper():
    """Test field mapping"""
    test_ocr_results = [
        {'text': 'BILL OF ENTRY / EXPORT', 'confidence': 0.9, 'bbox': ((0, 25), (100, 25), (100, 45), (0, 45))},
        {'text': '2 Consignor/Exporter BIN: 000158825-0103', 'confidence': 0.9, 'bbox': ((0, 160), (100, 160), (100, 180), (0, 180))},
        {'text': 'Vintage Denim Apparels Ltd.', 'confidence': 0.9, 'bbox': ((0, 215), (100, 215), (100, 235), (0, 235))},
    ]
    
    mapper = FieldMapper()
    mapped = mapper.map_extracted_data(test_ocr_results)
    
    print("Mapped fields:")
    for field, value in mapped.items():
        print(f"  {field}: {value}")


if __name__ == '__main__':
    test_mapper()