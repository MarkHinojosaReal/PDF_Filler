"""
PDF Field Analyzer using PyMuPDF and LangChain Google GenAI.
Analyzes non-fillable PDFs to identify potential fillable fields.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import fitz  # PyMuPDF
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from config import Config


@dataclass
class FieldCandidate:
    """Represents a potential fillable field identified in the PDF."""
    field_name: str
    field_type: str  # text, checkbox, dropdown, signature, date, etc.
    description: str
    page_number: int
    confidence: float
    suggested_default: str = ""
    required: bool = False


class PDFFieldAnalyzer:
    """Analyzes PDF documents to identify potential fillable fields using AI."""
    
    def __init__(self):
        """Initialize the PDF Field Analyzer."""
        # Validate Google GenAI configuration
        api_key = Config.get_google_genai_key()
        
        # Initialize the LangChain Google GenAI model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict[int, str]:
        """
        Extract text from PDF using PyMuPDF.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary mapping page numbers to extracted text
        """
        doc = fitz.open(pdf_path)
        page_texts = {}
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text = page.get_text()
            page_texts[page_num + 1] = text  # 1-indexed page numbers
        
        doc.close()
        return page_texts
    
    def create_analysis_prompt(self, page_texts: Dict[int, str]) -> str:
        """
        Create a prompt for the AI to analyze the PDF text and identify fields.
        
        Args:
            page_texts: Dictionary of page numbers to text content
            
        Returns:
            Formatted prompt string
        """
        full_text = "\n\n".join([f"Page {page}: {text}" for page, text in page_texts.items()])
        
        prompt = f"""
Analyze the following PDF document text and identify potential fillable fields that could be added to make this a fillable form.

Look for:
1. Labels followed by blank spaces or lines
2. Text that appears to be requesting user input
3. Checkboxes or option lists
4. Signature areas
5. Date fields
6. Name/address fields
7. Any other areas where a user would typically enter information

For each potential field, provide:
- field_name: A descriptive name for the field
- field_type: The type of field (text, checkbox, dropdown, signature, date, email, phone, etc.)
- description: What this field is for
- page_number: Which page the field appears on
- confidence: Your confidence level (0.0 to 1.0) that this should be a fillable field
- required: Whether this field appears to be required
- suggested_default: Any default value that might be appropriate

Please respond with a JSON array of field objects. Here's an example format:
[
    {{
        "field_name": "applicant_name",
        "field_type": "text",
        "description": "Name of the license transfer applicant",
        "page_number": 1,
        "confidence": 0.9,
        "required": true,
        "suggested_default": ""
    }}
]

PDF Content:
{full_text}

Respond only with the JSON array, no additional text.
"""
        return prompt
    
    def analyze_fields(self, pdf_path: str) -> List[FieldCandidate]:
        """
        Analyze a PDF to identify potential fillable fields.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of FieldCandidate objects
        """
        # Extract text from PDF
        page_texts = self.extract_text_from_pdf(pdf_path)
        
        # Create analysis prompt
        prompt = self.create_analysis_prompt(page_texts)
        
        # Get AI analysis
        message = HumanMessage(content=prompt)
        response = self.llm.invoke([message])
        
        # Parse the JSON response
        try:
            # Clean the response content by removing markdown code blocks
            content = response.content.strip()
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json
            if content.endswith('```'):
                content = content[:-3]  # Remove ```
            content = content.strip()
            
            fields_data = json.loads(content)
            
            # Convert to FieldCandidate objects
            field_candidates = []
            for field_data in fields_data:
                candidate = FieldCandidate(
                    field_name=field_data.get("field_name", ""),
                    field_type=field_data.get("field_type", "text"),
                    description=field_data.get("description", ""),
                    page_number=field_data.get("page_number", 1),
                    confidence=field_data.get("confidence", 0.0),
                    suggested_default=field_data.get("suggested_default", ""),
                    required=field_data.get("required", False)
                )
                field_candidates.append(candidate)
            
            return field_candidates
            
        except json.JSONDecodeError as e:
            print(f"Error parsing AI response: {e}")
            print(f"Response content: {response.content}")
            return []
    
    def save_analysis_report(self, field_candidates: List[FieldCandidate], output_path: str):
        """
        Save the field analysis to a JSON report file.
        
        Args:
            field_candidates: List of identified field candidates
            output_path: Path where to save the report
        """
        report_data = []
        for candidate in field_candidates:
            report_data.append({
                "field_name": candidate.field_name,
                "field_type": candidate.field_type,
                "description": candidate.description,
                "page_number": candidate.page_number,
                "confidence": candidate.confidence,
                "suggested_default": candidate.suggested_default,
                "required": candidate.required
            })
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    def print_analysis_summary(self, field_candidates: List[FieldCandidate]):
        """
        Print a summary of the field analysis.
        
        Args:
            field_candidates: List of identified field candidates
        """
        print(f"\n=== PDF Field Analysis Summary ===")
        print(f"Total potential fields identified: {len(field_candidates)}")
        print(f"\nField Details:")
        print("-" * 80)
        
        for i, candidate in enumerate(field_candidates, 1):
            print(f"{i}. {candidate.field_name}")
            print(f"   Type: {candidate.field_type}")
            print(f"   Description: {candidate.description}")
            print(f"   Page: {candidate.page_number}")
            print(f"   Confidence: {candidate.confidence:.2f}")
            print(f"   Required: {candidate.required}")
            if candidate.suggested_default:
                print(f"   Suggested Default: {candidate.suggested_default}")
            print()


def main():
    """Main function to demonstrate the field analyzer."""
    try:
        # Initialize the analyzer
        analyzer = PDFFieldAnalyzer()
        
        # Analyze the sample PDF
        pdf_path = "docs/License-Transfer-Form.pdf"
        
        if not Path(pdf_path).exists():
            print(f"Error: PDF file not found at {pdf_path}")
            return
        
        print(f"Analyzing PDF: {pdf_path}")
        
        # Perform analysis
        field_candidates = analyzer.analyze_fields(pdf_path)
        
        # Print summary
        analyzer.print_analysis_summary(field_candidates)
        
        # Save report
        report_path = "field_analysis_report.json"
        analyzer.save_analysis_report(field_candidates, report_path)
        print(f"\nDetailed report saved to: {report_path}")
        
    except Exception as e:
        print(f"Error during analysis: {e}")


if __name__ == "__main__":
    main()