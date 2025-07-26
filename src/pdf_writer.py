"""
PDF Writer Module
Handles filling and writing PDF forms
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    print("PyPDF2 is not installed. Please install it with: pip install PyPDF2")
    sys.exit(1)


class PDFWriter:
    """A class to handle filling and writing PDF forms."""
    
    def __init__(self, pdf_path: str):
        """Initialize with the path to the PDF file."""
        self.pdf_path = Path(pdf_path)
        self.reader = None
        self.writer = None
        self.fields = {}
        
    def load_pdf(self) -> bool:
        """Load the PDF file for writing."""
        try:
            if not self.pdf_path.exists():
                print(f"Error: PDF file not found at {self.pdf_path}")
                return False
                
            self.reader = PdfReader(str(self.pdf_path))
            self.writer = PdfWriter()
            self.fields = self.reader.get_fields()
            return True
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False
    
    def fill_single_field(self, field_name: str, value: str) -> bool:
        """Fill a single form field with a value."""
        if not self.reader or not self.writer:
            print("Error: PDF not loaded. Call load_pdf() first.")
            return False
            
        if field_name not in self.fields:
            print(f"Error: Field '{field_name}' not found in the PDF.")
            return False
            
        try:
            # Add all pages to the writer
            for page in self.reader.pages:
                self.writer.add_page(page)
            
            # Fill the field
            self.writer.update_page_form_field_values(
                self.writer.pages[0], {field_name: value}
            )
            return True
            
        except Exception as e:
            print(f"Error filling field '{field_name}': {e}")
            return False
    
    def fill_multiple_fields(self, field_values: Dict[str, str]) -> bool:
        """Fill multiple form fields at once."""
        if not self.reader or not self.writer:
            print("Error: PDF not loaded. Call load_pdf() first.")
            return False
            
        try:
            # Add all pages to the writer
            for page in self.reader.pages:
                self.writer.add_page(page)
            
            # Fill all fields
            self.writer.update_page_form_field_values(
                self.writer.pages[0], field_values
            )
            return True
            
        except Exception as e:
            print(f"Error filling multiple fields: {e}")
            return False
    
    def save_pdf(self, output_path: str) -> bool:
        """Save the filled PDF to a new file."""
        if not self.writer:
            print("Error: No PDF writer available. Fill some fields first.")
            return False
            
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as output_file:
                self.writer.write(output_file)
            
            print(f"Filled PDF saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"Error saving PDF: {e}")
            return False
    
    def get_available_fields(self) -> list:
        """Get a list of available field names."""
        return list(self.fields.keys()) if self.fields else []


def fill_pdf_form(input_path: str, field_values: Dict[str, str], output_path: str) -> bool:
    """Convenience function to fill a PDF form and save it."""
    writer = PDFWriter(input_path)
    
    if not writer.load_pdf():
        return False
        
    if not writer.fill_multiple_fields(field_values):
        return False
        
    return writer.save_pdf(output_path)


def fill_single_field(input_path: str, field_name: str, value: str, output_path: str) -> bool:
    """Convenience function to fill a single field and save the PDF."""
    writer = PDFWriter(input_path)
    
    if not writer.load_pdf():
        return False
        
    if not writer.fill_single_field(field_name, value):
        return False
        
    return writer.save_pdf(output_path)