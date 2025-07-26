#!/bin/bash
# Test script to simulate the GitHub Action workflow locally

set -e  # Exit on any error

echo "🧪 Testing PDF Reader Workflow Locally"
echo "======================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first."
    echo "Visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

echo "✅ uv is installed"

# Check if PDF file exists
if [ ! -f "docs/License-Transfer-Form.pdf" ]; then
    echo "❌ PDF file not found at docs/License-Transfer-Form.pdf"
    exit 1
fi

echo "✅ PDF file found"

# Install dependencies
echo "📦 Installing dependencies with uv..."
uv sync

# Run the PDF reader
echo "📖 Running PDF reader..."
python src/read_fields.py

echo "✅ Test completed successfully!" 