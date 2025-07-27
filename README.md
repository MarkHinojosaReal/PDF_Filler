# PDF Form Filler

A Python-based application for reading, analyzing, and filling PDF forms programmatically. This tool allows you to extract form field information from PDFs and automatically populate them with data.

## Features

- **PDF Form Analysis**: Extract and analyze form fields from PDF documents
- **Automated Form Filling**: Programmatically fill PDF forms with specified data
- **Field Validation**: Analyze field types, requirements, and constraints
- **Interactive Mode**: Fill forms interactively through command-line interface
- **Batch Processing**: Fill multiple forms or fields efficiently

## Architecture

The application follows a modular design with three core components:

- **`PDFReader`** (`src/pdf_reader.py`): Handles PDF loading and form field extraction
- **`PDFWriter`** (`src/pdf_writer.py`): Manages form filling and PDF output generation
- **`PDFFormFillerApp`** (`src/main.py`): Main orchestration class combining read/write operations

## Requirements

- Python 3.13+
- uv for dependency management

## Installation

```bash
uv sync
```

## Usage

### Basic Usage

```bash
python src/main.py
```

### Programmatic Usage

```python
from src.main import PDFFormFillerApp

# Initialize the application
app = PDFFormFillerApp("path/to/your/form.pdf")

# Analyze the PDF form
app.analyze_pdf()

# Fill the form with data
field_values = {
    "field_name_1": "value_1",
    "field_name_2": "value_2"
}
app.fill_form(field_values, "output_filled_form.pdf")
```

### Field Analysis

To analyze available fields in a PDF:

```python
from src.pdf_reader import PDFReader

reader = PDFReader("your_form.pdf")
reader.load_pdf()
reader.list_fields()
```

## Project Structure

```
PDF_Filler/
├── src/
│   ├── main.py              # Main application orchestrator
│   ├── pdf_reader.py        # PDF reading and field extraction
│   ├── pdf_writer.py        # PDF form filling and output
│   ├── field_analyzer.py    # Advanced field analysis
│   └── config.py           # Configuration settings
├── docs/
│   └── *.pdf               # Sample PDF forms
├── scripts/
│   └── test_workflow.sh    # Testing utilities
└── pyproject.toml          # Project dependencies and metadata
```

## Development

The project uses modern Python tooling:

- **uv**: Fast dependency management and virtual environments
- **ruff**: Code formatting and linting
- **isort**: Import sorting

### Running Tests

```bash
./scripts/test_workflow.sh
```

### Code Formatting

```bash
ruff format src/
isort src/
```

## Sample Files

The `docs/` directory contains sample PDF forms for testing:
- `License-Transfer-Form.pdf`: Example fillable form
- `Sample-Fillable-PDF.pdf`: Additional test form

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and formatting
5. Submit a pull request

## License

[Add your license information here]