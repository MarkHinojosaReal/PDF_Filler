#!/usr/bin/env python3
"""
PDF Fields Reader Script
Reads and displays all form fields from the PDF in docs/ directory
"""

import sys
from pathlib import Path

# Add src directory to path to import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pdf_reader import PDFReader


def main():
    """Read and display PDF form fields."""
    pdf_path = "docs/Sample-Fillable-PDF.pdf"
    
    # Check if PDF exists
    if not Path(pdf_path).exists():
        print(f"Error: PDF file not found at {pdf_path}")
        return False
    
    print(f"Reading PDF fields from: {pdf_path}")
    print("=" * 60)
    
    # Create PDF reader instance
    reader = PDFReader(pdf_path)
    
    # Load and analyze the PDF
    if not reader.load_pdf():
        print("Failed to load PDF file.")
        return False
    
    # Display all fields
    reader.list_fields()
    
    # Get field names for summary
    field_names = reader.get_field_names()
    
    print("=" * 60)
    print(f"Summary: Found {len(field_names)} fields")
    if field_names:
        print("\nField names:")
        for i, field_name in enumerate(field_names, 1):
            print(f"  {i}. {field_name}")
    else:
        print("No fillable form fields found in this PDF.")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)