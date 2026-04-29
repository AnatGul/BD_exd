# -*- coding: utf-8 -*-
"""
PDF Processor Module - Handles PDF files for Bangladesh Export Declarations
"""
import os
from typing import List, Optional
import sys


class PDFProcessor:
    """
    Processes PDF files for export declarations
    """
    
    def __init__(self):
        """Initialize PDF processor"""
        self.supported_formats = ['.pdf']
    
    def is_supported(self, file_path: str) -> bool:
        """
        Check if file is supported
        
        Args:
            file_path: Path to file
            
        Returns:
            True if supported
        """
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_formats
    
    def convert_to_images(self, pdf_path: str, output_dir: str = None,
                        dpi: int = 300, first_page: int = None,
                        last_page: int = None) -> List[str]:
        """
        Convert PDF to images
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Output directory
            dpi: DPI for conversion
            first_page: First page to convert
            last_page: Last page to convert
            
        Returns:
            List of paths to converted images
        """
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise ImportError("pdf2image required. Install: pip install pdf2image")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        if output_dir is None:
            output_dir = os.path.dirname(pdf_path)
        
        os.makedirs(output_dir, exist_ok=True)
        
        kwargs = {'dpi': dpi}
        
        if first_page:
            kwargs['first_page'] = first_page
        if last_page:
            kwargs['last_page'] = last_page
        
        images = convert_from_path(pdf_path, **kwargs)
        
        if not images:
            raise ValueError(f"Could not convert PDF: {pdf_path}")
        
        output_paths = []
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        for i, image in enumerate(images):
            output_path = os.path.join(output_dir, f"{base_name}_page{i+1}.png")
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            image.save(output_path, 'PNG')
            output_paths.append(output_path)
        
        return output_paths
    
    def extract_text(self, pdf_path: str, page_numbers: List[int] = None) -> str:
        """
        Extract text from PDF using pdfplumber
        
        Args:
            pdf_path: Path to PDF file
            page_numbers: List of page numbers to extract from
            
        Returns:
            Extracted text
        """
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber required. Install: pip install pdfplumber")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        text = ""
        
        with pdfplumber.open(pdf_path) as pdf:
            pages = pdf.pages
            
            if page_numbers:
                pages = [pages[i-1] for i in page_numbers if 0 < i <= len(pages)]
            
            for page in pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        return text
    
    def get_page_count(self, pdf_path: str) -> int:
        """
        Get number of pages in PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of pages
        """
        try:
            import pdfplumber
        except ImportError:
            raise ImportError("pdfplumber required. Install: pip install pdfplumber")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        with pdfplumber.open(pdf_path) as pdf:
            return len(pdf.pages)


def test_pdf_processor():
    """Test PDF processor"""
    import glob
    
    test_pdfs = glob.glob(os.path.join(os.path.dirname(__file__), '..', 'data', 'input', '*.pdf'))
    
    if not test_pdfs:
        print("No test PDFs found")
        return
    
    processor = PDFProcessor()
    
    for pdf_path in test_pdfs:
        print(f"\n=== Processing: {os.path.basename(pdf_path)} ===")
        
        page_count = processor.get_page_count(pdf_path)
        print(f"Pages: {page_count}")
        
        text = processor.extract_text(pdf_path, page_numbers=[1])
        print(f"First page text (first 500 chars):")
        print(text[:500])


if __name__ == '__main__':
    test_pdf_processor()