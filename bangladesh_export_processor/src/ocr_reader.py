# -*- coding: utf-8 -*-
"""
OCR Reader Module - EasyOCR integration for Bangladesh Export Declarations
"""
import os
import sys
from typing import List, Dict, Tuple
from PIL import Image
import numpy as np


# Fix for Windows encoding issue with EasyOCR
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass


class OCRReader:
    """
    OCR reader using EasyOCR for text extraction from export declaration images
    """
    
    def __init__(self, languages: List[str] = ['en', 'bn']):
        """
        Initialize OCR reader
        
        Args:
            languages: List of languages for OCR (default: English, Bengali)
        """
        self.languages = languages
        
        # Initialize with verbose=False to avoid encoding issues
        import easyocr
        self.reader = easyocr.Reader(languages, gpu=False, verbose=False)
    
    def read_image(self, image_path: str) -> List[Dict]:
        """
        Read text from image file

        Args:
            image_path: Path to image file

        Returns:
            List of dictionaries with text, coordinates and confidence
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Используем PIL для загрузки изображения (поддержка кириллицы в путях)
        # и передаём numpy array в EasyOCR вместо пути к файлу
        try:
            img = Image.open(image_path)
            img_array = np.array(img)
            results = self.reader.readtext(img_array)
        except Exception as e:
            # Если PIL не сработал, пробуем напрямую (для совместимости)
            results = self.reader.readtext(image_path)
        
        parsed_results = []
        for (bbox, text, confidence) in results:
            parsed_results.append({
                'text': text.strip(),
                'confidence': confidence,
                'bbox': bbox,
                'raw': text
            })
        
        return parsed_results
    
    def read_image_with_zones(self, image_path: str, zones: Dict[str, Tuple[int, int, int, int]]) -> Dict[str, str]:
        """
        Read text from specific zones of the image

        Args:
            image_path: Path to image file
            zones: Dictionary of zone names to (x1, y1, x2, y2) coordinates

        Returns:
            Dictionary of zone names to extracted text
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Используем PIL для загрузки изображения (поддержка кириллицы)
        try:
            img = Image.open(image_path)
            img_array = np.array(img)
            results = self.reader.readtext(img_array)
        except Exception as e:
            results = self.reader.readtext(image_path)
        zone_results = {zone: "" for zone in zones}
        
        for (bbox, text, confidence) in results:
            x_center = (bbox[0][0] + bbox[2][0]) / 2
            y_center = (bbox[0][1] + bbox[2][1]) / 2
            
            for zone_name, (x1, y1, x2, y2) in zones.items():
                if x1 <= x_center <= x2 and y1 <= y_center <= y2:
                    zone_results[zone_name] += text + " "
        
        return {k: v.strip() for k, v in zone_results.items()}
    
    def read_pdf_first_page(self, pdf_path: str, output_dir: str = None) -> str:
        """
        Convert first page of PDF to image and return path
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save converted image
            
        Returns:
            Path to converted image file
        """
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise ImportError("pdf2image required for PDF processing. Install: pip install pdf2image")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path)
        
        images = convert_from_path(pdf_path, first_page=1, last_page=1)
        
        if not images:
            raise ValueError(f"Could not convert PDF: {pdf_path}")
        
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f"{base_name}_page1.png")
        
        images[0].save(output_path, 'PNG')
        
        return output_path
    
    def read_document(self, doc_path: str) -> List[Dict]:
        """
        Read document (image or PDF)
        
        Args:
            doc_path: Path to image or PDF file
            
        Returns:
            List of OCR results
        """
        ext = os.path.splitext(doc_path)[1].lower()
        
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']:
            return self.read_image(doc_path)
        elif ext == '.pdf':
            image_path = self.read_pdf_first_page(doc_path)
            return self.read_image(image_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    def extract_all_text(self, doc_path: str) -> str:
        """
        Extract all text from document as single string
        
        Args:
            doc_path: Path to document
            
        Returns:
            Extracted text
        """
        results = self.read_document(doc_path)
        return " ".join([r['text'] for r in results])


def get_default_zones() -> Dict[str, Tuple[int, int, int, int]]:
    """
    Get default zone coordinates for Bangladesh Export Declaration
    
    Returns:
        Dictionary of zone names to (x1, y1, x2, y2) coordinates
    """
    return {
        'header': (0, 0, 2500, 400),
        'exporter': (0, 400, 1200, 1200),
        'consignee': (1200, 400, 2500, 1200),
        'carrier': (0, 1200, 1200, 1800),
        'bank': (1200, 1200, 2500, 1800),
        'goods': (0, 1800, 2500, 3500),
    }


def test_ocr():
    """Test OCR on sample documents"""
    import glob
    
    test_images = glob.glob(os.path.join(os.path.dirname(__file__), '..', 'data', 'input', '*.jpg'))
    
    if not test_images:
        print("No test images found. Place images in data/input directory")
        return
    
    reader = OCRReader()
    
    for img_path in test_images:
        print(f"\n=== Processing: {os.path.basename(img_path)} ===")
        results = reader.read_image(img_path)
        
        print(f"Found {len(results)} text elements")
        
        for i, result in enumerate(results[:20]):
            confidence_pct = result['confidence'] * 100
            print(f"  {i+1}: [{confidence_pct:.1f}%] {result['text']}")


if __name__ == '__main__':
    test_ocr()