"""
PDF Form Filler Package
A modular Python package for reading and filling PDF forms using PyPDF2
"""

from .main import PDFFormFillerApp
from .pdf_reader import PDFReader, display_fields, read_pdf_fields
from .pdf_writer import PDFWriter, fill_pdf_form, fill_single_field

__version__ = "0.1.0"
__author__ = "PDF Filler Team"

__all__ = [
    "PDFReader",
    "PDFWriter", 
    "PDFFormFillerApp",
    "display_fields",
    "read_pdf_fields",
    "fill_pdf_form",
    "fill_single_field"
] 