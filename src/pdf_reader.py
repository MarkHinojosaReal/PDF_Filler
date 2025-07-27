"""
PDF Reader Module
Handles reading and analyzing PDF form fields
"""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("PyPDF2 is not installed. Please install it with: pip install PyPDF2")
    sys.exit(1)


class PDFReader:
    """A class to handle reading PDF form fields."""
    
    def __init__(self, pdf_path: str):
        """Initialize with the path to the PDF file."""
        self.pdf_path = Path(pdf_path)
        self.reader = None
        self.fields = {}
        
    def load_pdf(self) -> bool:
        """Load the PDF file and extract form fields."""
        try:
            if not self.pdf_path.exists():
                print(f"Error: PDF file not found at {self.pdf_path}")
                return False
                
            self.reader = PdfReader(str(self.pdf_path))
            
            # Check if the PDF has form fields
            if not self.reader.get_fields():
                print("Warning: This PDF does not appear to have fillable form fields.")
                return True
                
            # Extract form fields
            self.fields = self.reader.get_fields()
            return True
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False
    
    def get_fields(self) -> Dict[str, Any]:
        """Get all form fields from the PDF."""
        return self.fields
    
    def list_fields(self) -> None:
        """List all available form fields in the PDF."""
        if not self.fields:
            print("No form fields found in the PDF.")
            return
            
        print(f"\nFound {len(self.fields)} form fields:")
        print("-" * 50)
        
        for field_name, field in self.fields.items():
            field_type = field.get('/FT', 'Unknown')
            current_value = field.get('/V', '')
            print(f"Field: {field_name}")
            print(f"  Type: {field_type}")
            print(f"  Current Value: {current_value}")
            print()
    
    def get_field_names(self) -> list:
        """Get a list of all field names."""
        return list(self.fields.keys())
    
    def get_field_info(self, field_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific field."""
        if field_name not in self.fields:
            return None
            
        field = self.fields[field_name]
        return {
            'name': field_name,
            'type': field.get('/FT', 'Unknown'),
            'current_value': field.get('/V', ''),
            'field_object': field
        }


def read_pdf_fields(pdf_path: str) -> Dict[str, Any]:
    """Convenience function to quickly read fields from a PDF."""
    reader = PDFReader(pdf_path)
    if reader.load_pdf():
        return reader.get_fields()
    return {}


def display_fields(pdf_path: str) -> None:
    """Convenience function to display all fields from a PDF."""
    reader = PDFReader(pdf_path)
    if reader.load_pdf():
        reader.list_fields()