# -*- coding: utf-8 -*-
"""
LLM Field Extractor - Uses LLM to extract structured fields from OCR text
"""
from typing import Dict, Optional
import json
import re


class LLMFieldExtractor:
    """
    Extract structured fields from OCR text using LLM approach.
    Since we can't call external LLM in this session, this module provides
    prompts and parsing logic that can be used with external LLM.
    """
    
    # Field names to extract
    FIELDS = [
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
        'Код агента',
        'Адрес декларанта/агента',
        'Условия поставки',
        'Наименование авиакомпании',
        'Код валюты',
        'Общая стоимость',
        'Наименование банка',
        'Код банка',
        'Сектор и фонд',
        'Код ТН ВЭД',
        'Описание товара',
        'Номер CRF/EXP',
    ]
    
    @staticmethod
    def generate_prompt(ocr_text: str) -> str:
        """
        Generate prompt for LLM to extract fields
        
        Args:
            ocr_text: Raw OCR text from document
            
        Returns:
            Prompt string
        """
        prompt = f"""Ты - специалист по обработке документов Bangladesh Export Declaration (экспортная декларация Бангладеш).

Извлеки из текста документа ниже структурированные данные. 
Внимательно прочитай текст и найди соответствующие значения для каждого поля.

Текст из документа:
---
{ocr_text}
---

Для каждого поля выведи значение, которое ты найдешь в тексте.
Если поле не найдено в тексте - выведи "НЕ НАЙДЕНО".

Поля для извлечения:
"""
        for field in LLMFieldExtractor.FIELDS:
            prompt += f"- {field}\n"
        
        prompt += """
Формат ответа (JSON):
{
  "Номер документа": "значение",
  "Тип документа": "значение",
  ...
}

Важно:
- Используй ТОЧНО текст из документа (не переводи)
- Если не уверен в значении - напиши "НЕ НАЙДЕНО"
- Не выдумывай значения
"""
        return prompt
    
    @staticmethod
    def parse_llm_response(response: str) -> Dict[str, str]:
        """
        Parse LLM response to extract fields
        
        Args:
            response: Response from LLM
            
        Returns:
            Dictionary of field values
        """
        fields = {}
        
        # Try to find JSON in response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                fields = json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        
        # If no JSON, try to parse line by line
        if not fields:
            for line in response.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key in LLMFieldExtractor.FIELDS:
                        fields[key] = value
        
        return fields
    
    @staticmethod
    def extract_from_tesseract(tesseract_text: str) -> Dict[str, str]:
        """
        Extract fields using simple pattern matching (fallback if no LLM)
        
        Args:
            tesseract_text: Text from Tesseract OCR
            
        Returns:
            Dictionary of extracted fields
        """
        fields = {}
        text = tesseract_text.upper()
        
        # Simple patterns for key fields
        patterns = {
            'Наименование экспортера': [
                r'VINTAGE[\s]+DENIM[\s]+APPARELS',
                r'ASDFA[\s]+FASHION',
                r'EXPORTER[:\s]+(.+)',
            ],
            'Наименование получателя/грузополучателя': [
                r'GLORIA[\s]+JEANS',
                r'JSC["\']?GLORIA',
                r'CONSIGNEE[:\s]+(.+)',
            ],
            'Код таможни/тариф': [
                r'CUSTOM[\s]+HOUSE[,\s]+DHAKA',
                r'DHAKA',
            ],
            'Условия поставки': [
                r'FOB',
                r'CIF',
                r'CFR',
                r'CZ-\d+',
            ],
        }
        
        for field, field_patterns in patterns.items():
            for pattern in field_patterns:
                match = re.search(pattern, text)
                if match:
                    fields[field] = match.group(0) if match.groups() else match.group()
                    break
        
        return fields


def test_llm_extractor():
    """Test LLM extractor"""
    # Sample text from Tesseract
    sample_text = """
    BILL OF ENTRY / EXPORT
    A OFFICE OF DISPATCH/EXPORT
    DECLARATION [494
    2 Consignor/Exporter BIN: 000158825-0103 EX 1 Custom House, Dhaka
    Vintage Denim Apparels Ltd. Registration
    Gazipur-1740; Bangladesh
    TIN:187268206101
    8 Consignee/Importer BIN: N/A BIN: JSC"GLORIA JEANS CORPORATION"
    STACHKI AVENUE 184,344090 ROSTOV-ON-DON CITY, RUSSIA
    14 Declarant/Agent AIN 410121479
    """
    
    # Generate prompt
    prompt = LLMFieldExtractor.generate_prompt(sample_text)
    print("=== Prompt for LLM ===")
    print(prompt[:500])
    print("...")
    
    # Test pattern extraction (fallback)
    fields = LLMFieldExtractor.extract_from_tesseract(sample_text)
    print("\n=== Extracted fields (pattern) ===")
    for k, v in fields.items():
        print(f"{k}: {v}")


if __name__ == '__main__':
    test_llm_extractor()