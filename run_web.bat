@echo off
REM Simple script to run the OCRmyPDF web interface locally on Windows

echo Starting OCRmyPDF Web Interface...
echo This will install Flask dependencies and run the web server.
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install Flask dependencies if not already installed
echo Installing Flask dependencies...
pip install Flask>=2.3.0 Werkzeug>=2.3.0

REM Check if OCRmyPDF is installed
python -c "import ocrmypdf" >nul 2>&1
if errorlevel 1 (
    echo Installing OCRmyPDF...
    pip install -e .
)

echo.
echo Starting web server on http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Run the web interface
python web_interface.py

pause
