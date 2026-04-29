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
        # Document info
        r'^(?:EXP|Document|Customs).*?No\.?': 'Номер документа',
        r'^Type\b': 'Тип документа',
        r'Type\s*Tax\s*base': 'Тип документа',
        r'Custom\s*House': 'Код таможни/тариф',
        r'Mode\s*of\s*payment': 'Код режима',
        r'^(?:Date|Дата)\b': 'Дата',
        
        # Exporter
        r'^101\b': 'Код офиса экспорта',
        r'^(?:Export\s*Office|EXPO|Office\s*Code)': 'Код офиса экспорта',
        r'Exporter\s*Code': 'Регистрационный номер экспортера',
        r'^(?:Year\b|2026)': 'Год',
        r'Consignor.*Exporter': 'Наименование экспортера',
        r'^(?:Exporter\s*Name|Exporter|Name\s*of\s*Exporter)': 'Наименование экспортера',
        r'^BIN:': 'Регистрационный номер BIN',
        r'^(?:Exporter\s*Address|Registration)': 'Адрес экспортера',
        
        # Consignee
        r'Consignee.*Importer': 'Наименование получателя/грузополучателя',
        r'^(?:Consignee|Buyer|Consignee\s*Name)': 'Наименование получателя/грузополучателя',
        r'^(?:Consignee\s*Address|STACHKI)': 'Адрес получателя',
        r'Country\s*Code': 'Код страны получателя',
        
        # Country
        r'Country\s*of\s*export': 'Страна происхождения',
        r'Country\s*origin': 'Страна происхождения',
        r'Country\s*destination': 'Страна конечного получателя',
        
        # Declarant/Agent
        r'^(?:Declarant\s*Agent|Agent\b)': 'Декларант/Агент',
        r'^AIN\s*\d': 'Код агента',
        r'^(?:Declarant\s*Address|Agent\s*Address)': 'Адрес декларанта/агента',
        
        # Delivery terms
        r'Delivery\s*terms': 'Условия поставки',
        r'^(?:Terms?\s*of?\s*Delivery|INCOTERMS)': 'Условия поставки',
        r'^CZ-': 'Код условий поставки',
        
        # Carrier
        r'^Carrier\b': 'Наименование авиакомпании',
        r'^(?:Airline|Airlines)': 'Наименование авиакомпании',
        r'^(?:Airline\s*Code|Air\s*Line)': 'Код авиакомпании',
        
        # Currency/Value
        r'^Currency\b': 'Код валюты',
        r'Total\s*Invoiced\s*Value': 'Общая стоимость',
        r'^Exchange\s*rate': 'Курс валют',
        
        # Bank
        r'^(?:Bank\s*Name|Bank)\b': 'Наименование банка',
        r'^(?:Bank\s*Code|BDDAC)': 'Код банка',
        
        # Port
        r'^(?:Port|Port\s*of\s*Shipment|Place\s*of\s*loading)': 'Порт погрузки',
        
        # Customs station
        r'^(?:Customs\s*Station|Custom\s*Station)': 'Код таможни/выпуска',
        
        # Sector
        r'^(?:Sector|Fund)\b': 'Сектор и фонд',
        
        # Package info
        r'^(?:Marks?\s*&?\s*Numbers?|Marks?\s*No)': 'Номер места',
        r'^Packages\b': 'Тип упаковки',
        r'^(?:Package|Pkg\s*Type|Type\s*of\s*Pack)': 'Тип упаковки',
        
        # Goods
        r'^HS\s*Code': 'Код ТН ВЭД',
        r'^(?:Description|Desc|Goods\s*Description)': 'Описание товара',
        r'^(?:Quantity|No\.?\s*of\s*Packages|Quantity.*Units)': 'Количество мест (ед)',
        r'^(?:Net\s*Weight|NW|Gross\s*weight)': 'Количество мест (ед.изм)',
        
        # CPC
        r'^(?:CPC\b|37\b)': 'Код CPC',
        
        # CRF/EXP
        r'^(?:CRF|CSR)\s*No': 'Номер CRF/EXP',
        r'^(?:CRF|CSR)\b': 'Номер CRF/EXP',
        r'^(?:CRF\s*Date|CSR\s*Date)': 'Дата CRF/EXP',
        
        # UPIUD, NMB, VM
        r'^(?:UPIUD)\b': 'UPIUD',
        r'^(?:NMB|Total\s*Value)\b': 'NMB',
        r'^(?:VM\b|43\b)': 'VM',
        
        # Additional costs
        r'^(?:Add\.?\s*Value|AV)': 'Дополнительная стоимость',
        
        # Bill of lading
        r'^(?:BL|Cargo\s*Lading)': 'Номер коносамента',
        r'^(?:BL\s*Date|Date\s*of)': 'Дата коносамента',
        
        # Total declared
        r'^(?:Total\s*Declare|Total\s*Value)': 'Общая декларируемая стоимость',
        
        # Registration
        r'^(?:Register|Reg\s*No|Registration)\b': 'Регистрационный номер',
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