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
        r'^(?:EXP|Document|Customs).*?No\.?': 'Номер документа',
        r'^Type\b': 'Тип документа',
        r'^(?:Customs? ?House|CH)': 'Код таможни/тариф',
        r'^Mode\b': 'Код режима',
        r'^(?:Date|Дата)\b': 'Дата',
        r'^(?:Export\s*Office|EXPO|Office\s*Code)': 'Код офиса экспорта',
        r'^(?:Exporter\s*Code|EXPORTER|Exp\.?Code)': 'Регистрационный номер экспортера',
        r'^Year\b': 'Год',
        r'^(?:Exporter\s*Name|Exporter|Name\s*of\s*Exporter)': 'Наименование экспортера',
        r'^(?:BIN|VAT\s*Reg)': 'Регистрационный номер BIN',
        r'^(?:Exporter\s*Address|Address)': 'Адрес экспортера',
        r'^(?:Phone|Tel)': 'Телефон экспортера',
        r'^(?:Consignee|Buyer|Consignee\s*Name)': 'Наименование получателя/грузополучателя',
        r'^(?:Consignee\s*Address|Ship\s*To)': 'Адрес получателя',
        r'^(?:Country\s*Code|CC)': 'Код страны получателя',
        r'^(?:Country|Country\s*Name|Country\s*of\s*Origin)': 'Страна происхождения',
        r'^(?:Carrier|Forwarder|Agent|Declarant)': 'Декларант/Агент',
        r'^(?:Carrier\s*Code|Agent\s*Code)': 'Код агента',
        r'^(?:Declarant\s*Address|Agent\s*Address)': 'Адрес декларанта/агента',
        r'^(?:Terms?\s*of?\s*Delivery|INCOTERMS)': 'Условия поставки',
        r'^(?:Terms?\s*Code|Incoterms\s*Code)': 'Код условий поставки',
        r'^(?:Airline|Airlines)': 'Наименование авиакомпании',
        r'^(?:Airline\s*Code|Air\s*Line)': 'Код авиакомпании',
        r'^(?:Currency|Curr)': 'Код валюты',
        r'^(?:Total\s*Value|Value|FOB\s*Value)': 'Общая стоимость',
        r'^(?:Exchange\s*Rate|ER)': 'Курс валют',
        r'^(?:Bank\s*Name|Bank)': 'Наименование банка',
        r'^(?:Bank\s*Code)': 'Код банка',
        r'^(?:Port|Port\s*of\s*Shipment)': 'Порт погрузки',
        r'^(?:Customs\s*Station|Custom\s*Station)': 'Код таможни/выпуска',
        r'^(?:Sector|Fund)': 'Сектор и фонд',
        r'^(?:Marks?\s*&?\s*Numbers?|Marks?\s*No)': 'Номер места',
        r'^(?:Package|Pkg\s*Type|Type\s*of\s*Pack)': 'Тип упаковки',
        r'^(?:HS\s*Code|H\.?S\.?)': 'Код ТН ВЭД',
        r'^(?:Description|Desc|Goods\s*Description)': 'Описание товара',
        r'^(?:Quantity|No\.?\s*of\s*Packages)': 'Количество мест (ед)',
        r'^(?:Net\s*Weight|NW)': 'Количество мест (ед.изм)',
        r'^(?:CPC\b)': 'Код CPC',
        r'^(?:CRF|CSR)': 'Номер CRF/EXP',
        r'^(?:CRF\s*Date|CSR\s*Date)': 'Дата CRF/EXP',
        r'^(?:UPIUD)': 'UPIUD',
        r'^(?:NMB\b)': 'NMB',
        r'^(?:VM\b)': 'VM',
        r'^(?:Add\.?\s*Value|AV)': 'Дополнительная стоимость',
        r'^(?:BL|Shippig\s*Bill|AWB|Air\s*Way\s*Bill)': 'Номер коносамента',
        r'^(?:BL\s*Date|Shippig\s*Date)': 'Дата коносамента',
        r'^(?:Total\s*Declare|Total\s*Value)': 'Общая декларируемая стоимость',
        r'^(?:Register|Reg\s*No|Registration)': 'Регистрационный номер',
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
    
    def map_extracted_data(self, ocr_results: List[Dict]) -> Dict[str, str]:
        """
        Map OCR results to structured fields
        
        Args:
            ocr_results: List of OCR result dictionaries
            
        Returns:
            Dictionary of field names to values
        """
        mapped = {}
        current_field = None
        current_value = ""
        
        for result in ocr_results:
            text = result['text'].strip()
            
            if not text:
                continue
            
            field_name = self.detect_field_name(text)
            
            if field_name:
                if current_field and current_value:
                    mapped[current_field] = current_value.strip()
                
                current_field = field_name
                current_value = text
            elif current_field:
                current_value += " " + text
        
        if current_field and current_value:
            mapped[current_field] = current_value.strip()
        
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