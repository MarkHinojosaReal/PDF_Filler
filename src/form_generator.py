"""
PDF Form Generator using PyMuPDF and LangChain Google GenAI.
Creates fillable PDF forms based on field analysis reports.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import fitz  # PyMuPDF
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import Config


@dataclass
class FieldPosition:
    """Represents the position and properties of a field on the PDF."""
    field_name: str
    field_type: str
    x: float
    y: float
    width: float
    height: float
    page_number: int
    description: str
    required: bool = False


class PDFFormGenerator:
    """Generates fillable PDF forms based on field analysis data."""
    
    def __init__(self):
        """Initialize the PDF Form Generator."""
        # Validate Google GenAI configuration
        api_key = Config.get_google_genai_key()
        
        # Initialize the LangChain Google GenAI model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
    
    def load_field_analysis(self, analysis_path: str) -> List[Dict[str, Any]]:
        """
        Load field analysis data from JSON file.
        
        Args:
            analysis_path: Path to the field analysis JSON file
            
        Returns:
            List of field analysis dictionaries
        """
        with open(analysis_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def extract_text_with_positions(self, pdf_path: str) -> Dict[int, List[Dict]]:
        """
        Extract text from PDF with position information.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary mapping page numbers to text blocks with positions
        """
        doc = fitz.open(pdf_path)
        page_data = {}
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            # Get text blocks with position data
            text_blocks = page.get_text("dict")["blocks"]
            
            formatted_blocks = []
            for block in text_blocks:
                if "lines" in block:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            formatted_blocks.append({
                                "text": span["text"],
                                "bbox": span["bbox"],  # [x0, y0, x1, y1]
                                "font": span["font"],
                                "size": span["size"]
                            })
            
            page_data[page_num + 1] = formatted_blocks
        
        doc.close()
        return page_data
    
    def create_position_prompt(self, page_data: Dict[int, List[Dict]], 
                             field_analysis: List[Dict[str, Any]]) -> str:
        """
        Create a prompt for AI to determine field positions.
        
        Args:
            page_data: Text blocks with positions from PDF
            field_analysis: List of identified fields
            
        Returns:
            Formatted prompt string
        """
        # Format the text blocks for the prompt
        text_layout = ""
        for page_num, blocks in page_data.items():
            text_layout += f"\nPage {page_num} Text Layout:\n"
            for i, block in enumerate(blocks):
                text = block["text"].strip()
                if text:  # Only include non-empty text
                    bbox = block["bbox"]
                    text_layout += f"  Block {i}: '{text}' at position (x:{bbox[0]:.1f}, y:{bbox[1]:.1f}, width:{bbox[2]-bbox[0]:.1f}, height:{bbox[3]-bbox[1]:.1f})\n"
        
        # Format the fields to place
        fields_to_place = ""
        for field in field_analysis:
            fields_to_place += f"- {field['field_name']} ({field['field_type']}): {field['description']}\n"
        
        prompt = f"""
You are helping to create a fillable PDF form by positioning form fields based on the document layout and field analysis.

Document Text Layout:
{text_layout}

Fields to Position:
{fields_to_place}

For each field, analyze the text layout and determine where the field should be positioned. Look for:
1. Labels or text that correspond to each field
2. Blank spaces or lines where users would write
3. Appropriate positioning near related text

For each field, provide the position as JSON with this format:
{{
    "field_name": "field_name_here",
    "field_type": "field_type_here", 
    "x": x_coordinate,
    "y": y_coordinate,
    "width": field_width,
    "height": field_height,
    "page_number": page_number,
    "description": "field_description_here",
    "required": true_or_false
}}

Guidelines for positioning:
- Text fields: width 150-200, height 20-25
- Date fields: width 100-120, height 20-25  
- Email/phone fields: width 150-180, height 20-25
- Signature fields: width 200-250, height 30-40
- Checkbox fields: width 15-20, height 15-20
- Dropdown fields: width 150-200, height 25-30

Position fields slightly to the right of labels or in obvious blank spaces.
Y coordinates increase downward (0 is top of page).

Respond with a JSON array of field position objects only, no additional text.
"""
        return prompt
    
    def determine_field_positions(self, pdf_path: str, 
                                field_analysis: List[Dict[str, Any]]) -> List[FieldPosition]:
        """
        Use AI to determine optimal field positions on the PDF.
        
        Args:
            pdf_path: Path to the original PDF
            field_analysis: List of field analysis data
            
        Returns:
            List of FieldPosition objects
        """
        # Extract text with positions
        page_data = self.extract_text_with_positions(pdf_path)
        
        # Create positioning prompt
        prompt = self.create_position_prompt(page_data, field_analysis)
        
        # Get AI analysis
        message = HumanMessage(content=prompt)
        response = self.llm.invoke([message])
        
        # Parse the JSON response
        try:
            # Clean the response content
            content = response.content.strip()
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            positions_data = json.loads(content)
            
            # Convert to FieldPosition objects
            field_positions = []
            for pos_data in positions_data:
                position = FieldPosition(
                    field_name=pos_data.get("field_name", ""),
                    field_type=pos_data.get("field_type", "text"),
                    x=float(pos_data.get("x", 0)),
                    y=float(pos_data.get("y", 0)),
                    width=float(pos_data.get("width", 150)),
                    height=float(pos_data.get("height", 25)),
                    page_number=int(pos_data.get("page_number", 1)),
                    description=pos_data.get("description", ""),
                    required=pos_data.get("required", False)
                )
                field_positions.append(position)
            
            return field_positions
            
        except json.JSONDecodeError as e:
            print(f"Error parsing position response: {e}")
            print(f"Response content: {response.content}")
            return []
    
    def create_fillable_form(self, original_pdf_path: str, 
                           field_positions: List[FieldPosition], 
                           output_path: str):
        """
        Create a fillable PDF form by adding form fields to the original PDF.
        
        Args:
            original_pdf_path: Path to the original PDF
            field_positions: List of field positions
            output_path: Path where to save the fillable form
        """
        # Open the original PDF
        doc = fitz.open(original_pdf_path)
        
        # Group fields by page
        fields_by_page = {}
        for field_pos in field_positions:
            page_num = field_pos.page_number - 1  # Convert to 0-indexed
            if page_num not in fields_by_page:
                fields_by_page[page_num] = []
            fields_by_page[page_num].append(field_pos)
        
        # Add form fields to each page
        for page_num, fields in fields_by_page.items():
            if page_num < doc.page_count:
                page = doc[page_num]
                
                for field_pos in fields:
                    # Create field rectangle
                    rect = fitz.Rect(
                        field_pos.x, 
                        field_pos.y,
                        field_pos.x + field_pos.width,
                        field_pos.y + field_pos.height
                    )
                    
                    # Determine field widget type
                    if field_pos.field_type == "text":
                        widget_type = fitz.PDF_WIDGET_TYPE_TEXT
                    elif field_pos.field_type == "checkbox":
                        widget_type = fitz.PDF_WIDGET_TYPE_CHECKBOX
                    elif field_pos.field_type == "dropdown":
                        widget_type = fitz.PDF_WIDGET_TYPE_COMBOBOX
                    elif field_pos.field_type == "signature":
                        widget_type = fitz.PDF_WIDGET_TYPE_SIGNATURE
                    elif field_pos.field_type in ["date", "email", "phone"]:
                        widget_type = fitz.PDF_WIDGET_TYPE_TEXT
                    else:
                        widget_type = fitz.PDF_WIDGET_TYPE_TEXT
                    
                    # Create the form field using PyMuPDF's Widget approach
                    try:
                        # Create Widget object first
                        widget_dict = {
                            "field_type": widget_type,
                            "rect": rect,
                            "field_name": field_pos.field_name,
                            "field_value": "",
                        }
                        
                        # Add field-specific properties
                        if field_pos.field_type == "dropdown" and "role" in field_pos.field_name.lower():
                            widget_dict["choice_values"] = [
                                "Designated Executive Broker",
                                "Executive Broker", 
                                "Associate Broker",
                                "Salesperson"
                            ]
                        
                        # Create widget and add to page
                        widget = fitz.Widget()
                        for key, value in widget_dict.items():
                            if hasattr(widget, key):
                                setattr(widget, key, value)
                        
                        annot = page.add_widget(widget)
                        
                    except Exception as e:
                        print(f"Error adding field {field_pos.field_name}: {e}")
                        continue
        
        # Save the fillable form
        doc.save(output_path)
        doc.close()
        
        print(f"Fillable form saved to: {output_path}")
    
    def generate_form_from_analysis(self, original_pdf_path: str, 
                                  analysis_path: str, 
                                  output_path: str = None):
        """
        Generate a fillable form from an analysis report.
        
        Args:
            original_pdf_path: Path to the original PDF
            analysis_path: Path to the field analysis JSON file
            output_path: Path where to save the fillable form (optional)
        """
        if output_path is None:
            base_name = Path(original_pdf_path).stem
            output_path = f"{base_name}_fillable.pdf"
        
        print(f"Loading field analysis from: {analysis_path}")
        field_analysis = self.load_field_analysis(analysis_path)
        
        print(f"Determining field positions using AI...")
        field_positions = self.determine_field_positions(original_pdf_path, field_analysis)
        
        if not field_positions:
            print("No field positions could be determined.")
            return
        
        print(f"Creating fillable form with {len(field_positions)} fields...")
        self.create_fillable_form(original_pdf_path, field_positions, output_path)
        
        return output_path


def main():
    """Main function to demonstrate the form generator."""
    try:
        # Initialize the generator
        generator = PDFFormGenerator()
        
        # File paths
        original_pdf = "docs/License-Transfer-Form.pdf"
        analysis_file = "field_analysis_report.json"
        output_file = "docs/License-Transfer-Form_fillable.pdf"
        
        # Check if files exist
        if not Path(original_pdf).exists():
            print(f"Error: Original PDF not found at {original_pdf}")
            return
        
        if not Path(analysis_file).exists():
            print(f"Error: Analysis file not found at {analysis_file}")
            return
        
        print("=== PDF Form Generator ===")
        print(f"Original PDF: {original_pdf}")
        print(f"Analysis file: {analysis_file}")
        print(f"Output file: {output_file}")
        
        # Generate the fillable form
        result_path = generator.generate_form_from_analysis(
            original_pdf, 
            analysis_file, 
            output_file
        )
        
        if result_path:
            print(f"\n✅ Successfully created fillable form: {result_path}")
        else:
            print("\n❌ Failed to create fillable form")
        
    except Exception as e:
        print(f"Error during form generation: {e}")


if __name__ == "__main__":
    main()