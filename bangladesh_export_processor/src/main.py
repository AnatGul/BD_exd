# -*- coding: utf-8 -*-
"""
Main Processor Module - Orchestrates OCR, mapping, and translation for Bangladesh Export Declarations
"""
import os
import glob
from typing import Dict, List, Optional, Tuple

from .ocr_reader import OCRReader
from .field_mapper import FieldMapper
from .translator import Translator
from .excel_writer import ExcelWriter
from .pdf_processor import PDFProcessor


class BangladeshExportProcessor:
    """
    Main processor for Bangladesh Export Declaration translation
    """
    
    def __init__(self, input_dir: str = None, output_dir: str = None):
        """
        Initialize processor
        
        Args:
            input_dir: Directory with input files
            output_dir: Directory for output files
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        self.ocr_reader = OCRReader()
        self.field_mapper = FieldMapper()
        self.translator = Translator()
        self.excel_writer = ExcelWriter()
        self.pdf_processor = PDFProcessor()
    
    def get_input_files(self, pattern: str = None) -> List[str]:
        """
        Get list of input files
        
        Args:
            pattern: File pattern (e.g., '*.jpg', '*.pdf')
            
        Returns:
            List of file paths
        """
        if pattern is None:
            pattern = '*'
        
        search_path = os.path.join(self.input_dir, pattern)
        return sorted(glob.glob(search_path))
    
    def process_single(self, input_path: str, name: str = None) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Process single declaration
        
        Args:
            input_path: Path to input file
            name: Optional name for output file
            
        Returns:
            Tuple of (original_fields, translated_fields)
        """
        if name is None:
            name = os.path.splitext(os.path.basename(input_path))[0]
        
        print(f"\n=== Processing: {name} ===")
        
        # OCR
        print("  Running OCR...")
        ocr_results = self.ocr_reader.read_document(input_path)
        print(f"  Found {len(ocr_results)} text elements")
        
        # Map fields
        print("  Mapping fields...")
        mapped_fields = self.field_mapper.map_extracted_data(ocr_results)
        full_mapped = self.field_mapper.merge_with_static(mapped_fields)
        
        # Используем данные из OCR
        print("  Using OCR data...")
        original_fields = full_mapped
        
        # Translate
        print("  Translating...")
        translated_fields = self.translator.translate_fields(original_fields)
        
        return original_fields, translated_fields
    
    def process_and_save(self, input_path: str, output_path: str = None) -> str:
        """
        Process single declaration and save to Excel
        
        Args:
            input_path: Path to input file
            output_path: Path to output Excel file
            
        Returns:
            Path to output file
        """
        original_fields, translated_fields = self.process_single(input_path, output_path)
        
        if output_path is None:
            if self.output_dir:
                os.makedirs(self.output_dir, exist_ok=True)
                name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(self.output_dir, f"{name} (перевод).xlsx")
            else:
                output_path = os.path.splitext(input_path)[0] + " (перевод).xlsx"
        
        print(f"  Writing to: {output_path}")
        self.excel_writer.write(original_fields, translated_fields, output_path)
        
        return output_path
    
    def process_all(self) -> List[str]:
        """
        Process all files in input directory
        
        Returns:
            List of output file paths
        """
        if not self.input_dir or not os.path.exists(self.input_dir):
            raise ValueError(f"Input directory not found: {self.input_dir}")
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Get all supported files
        files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif', '*.pdf']:
            files.extend(self.get_input_files(ext))
        
        if not files:
            print(f"No files found in {self.input_dir}")
            return []
        
        print(f"Found {len(files)} files to process")
        
        output_paths = []
        for input_path in files:
            try:
                output_path = self.process_and_save(input_path)
                output_paths.append(output_path)
            except Exception as e:
                print(f"  Error processing {input_path}: {e}")
        
        return output_paths
    
    def _get_sample_fields(self, name: str) -> Dict[str, str]:
        """
        Get sample field data - this would normally come from OCR
        
        Args:
            name: Declaration name
            
        Returns:
            Dictionary of field values
        """
        # Extract number from name (e.g., EXD AFL-GJ-2026-005-M -> 005)
        number = name.split('-')[-1].replace('M', '') if '-' in name else '000'
        
        # Sample data based on the scanned documents
        return {
            'Номер документа': name,
            'Тип документа': 'EX',
            'Код таможни/тариф': 'Custom House, Dhaka',
            'Код режима': '1',
            'Дата': '17/04/2026',
            'Код офиса экспорта': '#882',
            'Регистрационный номер экспортера': '9.00',
            'Год': '2026',
            'Наименование экспортера': 'Asdwa Fashion Ltd.',
            'Регистрационный номер BIN': '002006207-0306',
            'Адрес экспортера': 'Kandail, Satgram, Narsingdi Sadar; Madhabdi PS; Narshingdi-1603; Bangladesh',
            'Телефон экспортера': '712831161872',
            'Наименование получателя/грузополучателя': 'JSC "Gloria Jeans Corporation"',
            'Адрес получателя': 'Stachki avenue 184, 344090 Rostov-on-Don City, Russia',
            'Код страны получателя': 'BDI',
            'Страна происхождения': 'Bangladesh',
            'Адрес декларанта/агента': 'NATIONAL UNIVERSITY, GAZIPUR-1704',
            'Страна конечного получателя': 'Russia',
            'Декларант/Агент': 'S.A. CORPORATION',
            'Код агента': '101041166',
            'Условия поставки': 'FOB',
            'Код условий поставки': 'CZ-392',
            'Наименование авиакомпании': 'China Southern Airlines',
            'Код авиакомпании': 'CZ',
            'Код валюты': 'USD',
            'Общая стоимость': '12,320.00',
            'Курс валют': '122.7433',
            'Наименование банка': 'Pubali Bank Limited',
            'Код банка': 'BDDAC',
            'Порт погрузки': 'Dhaka',
            'Код таможни/выпуска': 'Custom House, Dhaka',
            'Сектор и фонд': '043 - Garments Credit',
            'Номер места': '6572/11',
            'Тип упаковки': 'Carton',
            'Код ТН ВЭД': '61062000',
            'Описание товара': "Women's Or Girls' Blouses, Etc, Of Man-Made Fibres, Knitted Or Crocheted",
            'Количество мест (ед)': '128.00',
            'Количество мест (ед.изм)': '104.82',
            'Код CPC': '1072',
            'Номер CRF/EXP': '009467',
            'Дата CRF/EXP': '16/04/2026',
            'UPIUD': '2026/2217/6',
            'NMB': '800.00',
            'VM': '2,320.00',
            'Дополнительная стоимость': '2.90',
            'Номер коносамента': name.replace('EXD ', 'AFL/GJ/2026/').replace('-M', '-M'),
            'Дата коносамента': '16/04/2026',
            'Общая декларируемая стоимость': '284,764.46',
            'Регистрационный номер': '101P0265',
        }


def process_directory(input_dir: str, output_dir: str = None) -> List[str]:
    """
    Process all declarations in directory
    
    Args:
        input_dir: Directory with input files
        output_dir: Directory for output files
        
    Returns:
        List of output file paths
    """
    processor = BangladeshExportProcessor(input_dir, output_dir)
    return processor.process_all()


def process_file(input_path: str, output_path: str = None) -> str:
    """
    Process single declaration
    
    Args:
        input_path: Path to input file
        output_path: Path to output Excel file
        
    Returns:
        Path to output file
    """
    processor = BangladeshExportProcessor()
    return processor.process_and_save(input_path, output_path)


# ============================================================================
# Main entry point
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Process Bangladesh Export Declarations')
    parser.add_argument('input', nargs='?', help='Input file or directory')
    parser.add_argument('-o', '--output', help='Output directory or file')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    
    args = parser.parse_args()
    
    if args.test:
        # Test mode - create sample output
        if os.path.exists(r'D:\opencode_deas'):
            input_dir = r'D:\opencode_deas'
            output_dir = r'D:\opencode_deas'
        else:
            input_dir = 'data/input'
            output_dir = 'data/output'
        
        print(f"Input: {input_dir}")
        print(f"Output: {output_dir}")
        
        processor = BangladeshExportProcessor(input_dir, output_dir)
        outputs = processor.process_all()
        
        print(f"\n=== Complete ===")
        print(f"Processed {len(outputs)} files")
        for path in outputs:
            print(f"  {path}")
    elif args.input:
        if os.path.isdir(args.input):
            output_dir = args.output or args.input
            outputs = process_directory(args.input, output_dir)
            print(f"Processed {len(outputs)} files")
        else:
            output_path = process_file(args.input, args.output)
            print(f"Created: {output_path}")
    else:
        parser.print_help()