#!/bin/bash
# Simple script to run the OCRmyPDF web interface locally

echo "Starting OCRmyPDF Web Interface..."
echo "This will install Flask dependencies and run the web server."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Install Flask dependencies if not already installed
echo "Installing Flask dependencies..."
pip3 install Flask>=2.3.0 Werkzeug>=2.3.0

# Check if OCRmyPDF is installed
if ! python3 -c "import ocrmypdf" &> /dev/null; then
    echo "Installing OCRmyPDF..."
    pip3 install -e .
fi

echo ""
echo "Starting web server on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# Run the web interface
python3 web_interface.py
