#!/usr/bin/env python3
"""
Example usage of the modular PDF form filler
"""

from pdf_reader import PDFReader, display_fields
from pdf_writer import PDFWriter, fill_pdf_form
from main import PDFFormFillerApp


def example_read_only():
    """Example of reading PDF fields only."""
    print("=== Example: Reading PDF Fields ===")
    
    pdf_path = "docs/License-Transfer-Form.pdf"
    
    # Method 1: Using the PDFReader class
    reader = PDFReader(pdf_path)
    if reader.load_pdf():
        fields = reader.get_fields()
        print(f"Found {len(fields)} fields using PDFReader class")
    
    # Method 2: Using convenience function
    print("\n--- Using convenience function ---")
    display_fields(pdf_path)


def example_fill_form():
    """Example of filling a PDF form."""
    print("\n=== Example: Filling PDF Form ===")
    
    pdf_path = "docs/License-Transfer-Form.pdf"
    output_path = "docs/example_filled_form.pdf"
    
    # First, let's see what fields are available
    reader = PDFReader(pdf_path)
    if reader.load_pdf():
        available_fields = reader.get_field_names()
        print(f"Available fields: {available_fields}")
        
        # Example field values (modify these based on your actual field names)
        field_values = {
            # Add your field names and values here
            # Example:
            # "Name": "John Doe",
            # "Address": "123 Main St",
            # "Phone": "555-1234"
        }
        
        if field_values:
            # Method 1: Using convenience function
            if fill_pdf_form(pdf_path, field_values, output_path):
                print(f"Successfully filled form and saved to {output_path}")
            else:
                print("Failed to fill form")
        else:
            print("No field values provided. Please modify the field_values dictionary.")


def example_using_app():
    """Example using the main application class."""
    print("\n=== Example: Using PDFFormFillerApp ===")
    
    pdf_path = "docs/License-Transfer-Form.pdf"
    
    # Create the application
    app = PDFFormFillerApp(pdf_path)
    
    # Analyze the PDF
    if app.analyze_pdf():
        # Get available fields
        fields = app.get_available_fields()
        print(f"Available fields: {fields}")
        
        # Example: Fill a single field
        if fields:
            # Fill the first available field as an example
            first_field = fields[0]
            print(f"\nFilling single field: {first_field}")
            
            if app.fill_single_field(first_field, "Example Value"):
                print("Successfully filled single field")
            else:
                print("Failed to fill single field")


def example_step_by_step():
    """Example showing step-by-step process."""
    print("\n=== Example: Step-by-Step Process ===")
    
    pdf_path = "docs/License-Transfer-Form.pdf"
    output_path = "docs/step_by_step_filled.pdf"
    
    # Step 1: Read the PDF
    print("Step 1: Reading PDF...")
    reader = PDFReader(pdf_path)
    if not reader.load_pdf():
        print("Failed to load PDF")
        return
    
    # Step 2: Display fields
    print("Step 2: Available fields:")
    reader.list_fields()
    
    # Step 3: Prepare field values
    print("Step 3: Preparing field values...")
    available_fields = reader.get_field_names()
    
    # Example field values (modify these based on your actual field names)
    field_values = {
        # Add your field names and values here
        # Example:
        # "Name": "John Doe",
        # "Address": "123 Main St"
    }
    
    if not field_values:
        print("No field values provided. Available fields:")
        for field in available_fields:
            print(f"  - {field}")
        return
    
    # Step 4: Fill the form
    print("Step 4: Filling form...")
    writer = PDFWriter(pdf_path)
    if not writer.load_pdf():
        print("Failed to load PDF for writing")
        return
    
    if not writer.fill_multiple_fields(field_values):
        print("Failed to fill fields")
        return
    
    # Step 5: Save the filled PDF
    print("Step 5: Saving filled PDF...")
    if writer.save_pdf(output_path):
        print(f"Successfully saved filled PDF to {output_path}")
    else:
        print("Failed to save PDF")


if __name__ == "__main__":
    # Run all examples
    example_read_only()
    example_fill_form()
    example_using_app()
    example_step_by_step() 