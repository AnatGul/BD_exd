# -*- coding: utf-8 -*-
"""
Field Mapper Module - Maps OCR text to structured fields for Bangladesh Export Declarations
"""
import re
from typing import Dict, List, Tuple, Optional


class FieldMapper:
    """
    Maps extracted OCR text to structured declaration fields
    """
    
# Field mapping: pattern regex -> field name
    FIELD_PATTERNS = {
        # Document info - with OCR error variations
        r'^(?:EXP|Document|Customs).*?No\.?': 'Номер документа',
        r'^(?:Type|Tax|Type\s*Tax)': 'Тип документа',
        r'(?:Custom|House|Dhaka)': 'Код таможни/тариф',
        r'(?:Mode|Payment|ACCOUNT)': 'Код режима',
        r'^(?:Date|10/03|20/03)': 'Дата',
        
        # Exporter - common OCR variants
        r'(?:101|Consignor|Cuns)': 'Код офиса экспорта',
        r'(?:vintage|Vintage|Ltd)': 'Наименование экспортера',
        r'BIN:': 'Регистрационный номер BIN',
        r'(?:Gazipur|Bangladesh|Registration)': 'Адрес экспортера',
        
        # Consignee
        r'(?:Consignee|Consign|Cansl)': 'Наименование получателя/грузополучателя',
        r'(?:GLORIA|JSC|CORPORATION)': 'Наименование получателя/грузополучателя',
        r'(?:RUSSIA|Rostov|STACHKI)': 'Адрес получателя',
        
        # Country
        r'(?:Bangladesh|Russia)': 'Страна происхождения',
        
        # Declarant/Agent
        r'(?:Declarant|Dusl|AIN)': 'Декларант/Агент',
        r'(?:101121479|AIN\s*)': 'Код агента',
        
        # Delivery terms
        r'(?:Delivery|CZ-|FCA|CNF|CNl)': 'Условия поставки',
        
        # Carrier
        r'(?:Carrier|China|Cz|Airline)': 'Наименование авиакомпании',
        
        # Currency/Value
        r'(?:Currency|USD|Value|Total)': 'Код валюты',
        r'(?:Exchange|Exch|rate)': 'Курс валют',
        
        # Bank
        r'(?:Bank|Premier|Preinlei)': 'Наименование банка',
        r'(?:BDDAC|Dhaka|Branch)': 'Код банка',
        
        # Sector
        r'(?:Sector|Fund|043|Garments)': 'Сектор и фонд',
        
        # Package info
        r'(?:Packages|Pack|PanL)': 'Тип упаковки',
        r'(?:CT|Carrier|Carinr)': 'Тип упаковки',
        
        # Goods
        r'(?:HS|7607|Code)': 'Код ТН ВЭД',
        r'(?:Description|Men|Boys|PANTS)': 'Описание товара',
        
        # CRF/EXP
        r'(?:CRF|EXP|002023)': 'Номер CRF/EXP',
        
        # Additional
        r'(?:VM|43)': 'VM',
        r'(?:NMB|Total)': 'NMB',
    }
    
# Static field list (always present in order)
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
        'Дополнительная стоимость',
        'Номер коносамента',
        'Дата коносамента',
        'Общая декларируемая стоимость',
        'Регистрационный номер',
    ]
    
    def __init__(self):
        """Initialize field mapper"""
        self.fields = {}
    
    def detect_field_name(self, text: str) -> Optional[str]:
        """
        Detect field name from OCR text
        
        Args:
            text: Text from OCR
            
        Returns:
            Field name or None
        """
        text = text.strip().upper()
        
        for pattern, field_name in self.FIELD_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                return field_name
        
        return None
    
    def _is_company_name(self, text: str) -> bool:
        """Check if text looks like a company name"""
        text_upper = text.upper()
        company_patterns = ['LTD', 'LLC', 'INC', 'CORP', 'CO.', 'CORPORATION', 'LIMITED', 'ENTERPRISES']
        return any(p in text_upper for p in company_patterns)
    
    def map_extracted_data(self, ocr_results: List[Dict]) -> Dict[str, str]:
        """
        Map OCR results to structured fields.
        
        Args:
            ocr_results: List of OCR result dictionaries
            
        Returns:
            Dictionary of field names to values
        """
        mapped = {}
        
        # Labels that shouldn't stop value collection
        SKIP_LABELS = {'BIN:', 'TIN:', 'AIN:', 'NIA', 'CE', 'C.D.', 'Country'}
        
        for i, result in enumerate(ocr_results):
            text = result['text'].strip()
            if not text:
                continue
            
            field_name = self.detect_field_name(text)
            
            if field_name:
                # For name fields, prefer company name patterns
                name_fields = {'Наименование экспортера', 'Наименование получателя/грузополучателя'}
                values = []
                
                # First pass: look for company names
                if field_name in name_fields:
                    for j in range(i + 1, min(i + 15, len(ocr_results))):
                        next_text = ocr_results[j]['text'].strip()
                        if not next_text:
                            continue
                        if self._is_company_name(next_text):
                            mapped[field_name] = next_text
                            break
                
                # Second pass: if no company name found, collect regular values
                if field_name not in mapped:
                    for j in range(i + 1, min(i + 10, len(ocr_results))):
                        next_text = ocr_results[j]['text'].strip()
                        if not next_text:
                            continue
                        if next_text in SKIP_LABELS or next_text.isdigit():
                            continue
                        if self.detect_field_name(next_text):
                            break
                        values.append(next_text)
                        if len(values) >= 2:
                            break
                    
                    if values:
                        mapped[field_name] = ' '.join(values)
        
        return mapped
    
    def create_full_mapping(self) -> Dict[str, str]:
        """
        Create full field mapping with all static fields
        
        Returns:
            Dictionary of field names to empty strings
        """
        return {field: "" for field in self.STATIC_FIELDS}
    
    def merge_with_static(self, mapped_data: Dict[str, str]) -> Dict[str, str]:
        """
        Merge mapped data with static field structure
        
        Args:
            mapped_data: Mapped OCR data
            
        Returns:
            Complete field dictionary
        """
        full = self.create_full_mapping()
        full.update(mapped_data)
        return full


def test_mapper():
    """Test field mapping"""
    test_ocr_results = [
        {'text': 'Document No. EXD AFL-GJ-2026-005-M', 'confidence': 0.9, 'bbox': ((100, 100), (500, 100), (500, 150), (100, 150))},
        {'text': 'Custom House, Dhaka', 'confidence': 0.9, 'bbox': ((100, 200), (500, 200), (500, 250), (100, 250))},
        {'text': 'Asdwa Fashion Ltd.', 'confidence': 0.9, 'bbox': ((100, 400), (500, 400), (500, 450), (100, 450))},
    ]
    
    mapper = FieldMapper()
    mapped = mapper.map_extracted_data(test_ocr_results)
    
    print("Mapped fields:")
    for field, value in mapped.items():
        print(f"  {field}: {value}")
    
    full = mapper.merge_with_static(mapped)
    
    print("\nFull mapping with static fields:")
    for field, value in full.items():
        if value:
            print(f"  {field}: {value}")


if __name__ == '__main__':
    test_mapper()