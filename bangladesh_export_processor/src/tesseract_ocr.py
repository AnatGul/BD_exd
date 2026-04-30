# -*- coding: utf-8 -*-
"""
Tesseract OCR integration for Bangladesh Export Declarations
"""
import subprocess
from typing import List, Dict
from PIL import Image


class TesseractOCR:
    """Wrapper for Tesseract OCR"""
    
    def __init__(self, tesseract_path: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
        """
        Initialize Tesseract OCR
        
        Args:
            tesseract_path: Path to tesseract executable
        """
        self.tesseract_cmd = tesseract_path
    
    def read_image(self, image_path: str) -> str:
        """
        Read text from image using Tesseract
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        cmd = [self.tesseract_cmd, image_path, 'stdout']
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=120
        )
        return result.stdout
    
    def read_image_with_boxes(self, image_path: str) -> List[Dict]:
        """
        Read text with bounding boxes
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of dicts with text and bbox
        """
        # Use hocr output for better structure
        cmd = [self.tesseract_cmd, image_path, 'stdout', 'hocr']
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=120
        )
        
        # Parse hocr to extract text and boxes
        results = []
        import re
        
        # Extract bbox from hocr spans
        # Format: <span class='ocrx_word' title='bbox 100 200 300 400; ...'>text</span>
        bbox_pattern = r"title='bbox (\d+) (\d+) (\d+) (\d+)"
        word_pattern = r"<span class='ocrx_word'[^>]*>([^<]+)</span>"
        
        # Alternative: use tesseract with psm for better results
        # For now return simple text
        return [{'text': result.stdout, 'bbox': None}]
    
    def extract_text_blocks(self, image_path: str) -> List[Dict]:
        """
        Extract text in blocks (paragraphs)
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of text blocks
        """
        cmd = [self.tesseract_cmd, image_path, 'stdout']
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=120
        )
        
        # Split by lines and filter empty
        lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        
        blocks = []
        for i, line in enumerate(lines):
            blocks.append({
                'text': line,
                'line_num': i
            })
        
        return blocks


def test_tesseract():
    """Test Tesseract OCR"""
    ocr = TesseractOCR()
    
    # Test on sample image
    text = ocr.read_image('EXD 784-63264471.jpg')
    
    print('=== Tesseract OCR Result ===')
    print(text[:1000])
    print('...')
    print(f'\nTotal lines: {len(text.split(chr(10)))}')


if __name__ == '__main__':
    test_tesseract()