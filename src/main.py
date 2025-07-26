#!/usr/bin/env python3
"""
Main PDF Form Filler Application
Orchestrates reading and writing PDF forms using modular components
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Import our modules
from pdf_reader import PDFReader, display_fields
from pdf_writer import PDFWriter, fill_pdf_form


class PDFFormFillerApp:
    """Main application class that orchestrates PDF form operations."""
    
    def __init__(self, pdf_path: str):
        """Initialize the application with a PDF path."""
        self.pdf_path = pdf_path
        self.reader = PDFReader(pdf_path)
        self.writer = PDFWriter(pdf_path)
        
    def analyze_pdf(self) -> bool:
        """Analyze the PDF and display available fields."""
        print(f"Analyzing PDF: {self.pdf_path}")
        print("=" * 50)
        
        if not self.reader.load_pdf():
            return False
            
        self.reader.list_fields()
        return True
    
    def fill_form(self, field_values: Dict[str, str], output_path: str = None) -> bool:
        """Fill the PDF form with provided values."""
        if not output_path:
            # Generate default output path
            input_path = Path(self.pdf_path)
            output_path = input_path.parent / f"filled_{input_path.name}"
        
        print(f"Filling form fields...")
        print(f"Output will be saved to: {output_path}")
        
        if not self.writer.load_pdf():
            return False
            
        if not self.writer.fill_multiple_fields(field_values):
            return False
            
        return self.writer.save_pdf(str(output_path))
    
    def fill_single_field(self, field_name: str, value: str, output_path: str = None) -> bool:
        """Fill a single field in the PDF form."""
        if not output_path:
            # Generate default output path
            input_path = Path(self.pdf_path)
            output_path = input_path.parent / f"filled_{input_path.name}"
        
        print(f"Filling field '{field_name}' with value '{value}'...")
        print(f"Output will be saved to: {output_path}")
        
        if not self.writer.load_pdf():
            return False
            
        if not self.writer.fill_single_field(field_name, value):
            return False
            
        return self.writer.save_pdf(str(output_path))
    
    def get_available_fields(self) -> list:
        """Get list of available field names."""
        if not self.reader.load_pdf():
            return []
        return self.reader.get_field_names()


def main():
    """Main function demonstrating the modular PDF form filler."""
    # Configuration
    pdf_path = "docs/Sample-Fillable-PDF.pdf"
    
    # Create the application
    app = PDFFormFillerApp(pdf_path)
    
    # Step 1: Analyze the PDF and show available fields
    print("Step 1: Analyzing PDF form fields...")
    if not app.analyze_pdf():
        print("Failed to analyze PDF. Exiting.")
        return
    
    # Step 2: Get available fields for reference
    available_fields = app.get_available_fields()
    print(f"\nAvailable field names: {available_fields}")
    
    # Step 3: Example of filling form fields
    print("\nStep 2: Filling form fields...")
    
    # Example field values - modify these based on your actual field names
    field_values = {
        # Add your field names and values here
        # Example:
        # "Name": "John Doe",
        # "Address": "123 Main St",
        # "Phone": "555-1234",
        # "Email": "john.doe@example.com"
    }
    
    if field_values:
        if app.fill_form(field_values):
            print("Successfully filled and saved the PDF form!")
        else:
            print("Failed to fill the form.")
    else:
        print("No field values provided. Please modify the field_values dictionary in main().")
        print("Available fields to fill:")
        for field in available_fields:
            print(f"  - {field}")


def interactive_mode():
    """Interactive mode for filling PDF forms."""
    pdf_path = "docs/Sample-Fillable-PDF.pdf"
    app = PDFFormFillerApp(pdf_path)
    
    # Analyze the PDF first
    if not app.analyze_pdf():
        return
    
    available_fields = app.get_available_fields()
    
    print("\nInteractive Mode:")
    print("Enter field values (press Enter with empty field name to finish):")
    
    field_values = {}
    while True:
        field_name = input(f"\nEnter field name (or press Enter to finish): ").strip()
        if not field_name:
            break
            
        if field_name not in available_fields:
            print(f"Warning: Field '{field_name}' not found in PDF.")
            continue
            
        value = input(f"Enter value for '{field_name}': ").strip()
        field_values[field_name] = value
    
    if field_values:
        output_path = input("Enter output path (or press Enter for default): ").strip()
        if not output_path:
            output_path = None
            
        if app.fill_form(field_values, output_path):
            print("Successfully filled and saved the PDF form!")
        else:
            print("Failed to fill the form.")
    else:
        print("No fields to fill.")


if __name__ == "__main__":
    # You can choose between main() for programmatic use or interactive_mode() for user input
    main()
    
    # Uncomment the line below to use interactive mode instead
    # interactive_mode()