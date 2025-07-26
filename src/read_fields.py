#!/usr/bin/env python3
"""
Simple script to read and display PDF form fields
Can be run in GitHub Actions or locally
"""

import sys
import os
from pathlib import Path

try:
    from PyPDF2 import PdfReader
except ImportError:
    print("PyPDF2 is not installed. Please install it with: uv add pypdf2")
    sys.exit(1)


def read_pdf_fields(pdf_path: str):
    """Read and display all form fields from a PDF."""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found at {pdf_path}")
        return False
    
    try:
        reader = PdfReader(str(pdf_path))
        fields = reader.get_fields()
        
        if not fields:
            print("No form fields found in this PDF.")
            return True
        
        print(f"Found {len(fields)} form fields in {pdf_path.name}:")
        print("=" * 60)
        
        for i, (field_name, field) in enumerate(fields.items(), 1):
            field_type = field.get('/FT', 'Unknown')
            current_value = field.get('/V', '')
            print(f"{i}. Field Name: {field_name}")
            print(f"   Type: {field_type}")
            print(f"   Current Value: {current_value}")
            print()
        
        return True
            
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return False


def main():
    """Main function to read PDF fields."""
    # Check if running in GitHub Actions
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    
    if is_github_actions:
        print("Running in GitHub Actions environment")
        print(f"Working directory: {os.getcwd()}")
        print(f"Files in docs/: {list(Path('docs').glob('*')) if Path('docs').exists() else 'docs/ not found'}")
    
    # Path to the PDF file
    pdf_path = "docs/License-Transfer-Form.pdf"
    
    print(f"Attempting to read PDF: {pdf_path}")
    
    # Read and display fields
    success = read_pdf_fields(pdf_path)
    
    if success:
        print("✅ PDF fields read successfully!")
    else:
        print("❌ Failed to read PDF fields")
        sys.exit(1)


if __name__ == "__main__":
    main() 