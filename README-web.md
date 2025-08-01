# OCRmyPDF Web Interface

A simple Flask-based web interface for OCRmyPDF that allows you to upload PDF or image files, process them with OCR, and download the results.

## Features

- **Simple Upload**: Drag and drop or click to upload files
- **Multiple Formats**: Supports PDF, PNG, JPG, TIFF, BMP, and GIF files
- **OCR Options**: Configure language, optimization level, and processing options
- **Automatic Download**: Download processed files with one click
- **API Endpoint**: RESTful API for programmatic access
- **Docker Ready**: Easy deployment with Docker containers

## Quick Start with Docker

### Using Docker Compose (Recommended)

1. Clone the repository and navigate to the project directory
2. Build and run the container:

```bash
docker-compose up --build
```

3. Open your browser and go to `http://localhost:5000`

### Using Docker directly

```bash
# Build the image
docker build -f Dockerfile.web -t ocrmypdf-web .

# Run the container
docker run -p 5000:5000 ocrmypdf-web
```

## Manual Installation

If you prefer to run without Docker:

1. Install system dependencies (Ubuntu/Debian):

```bash
sudo apt-get update
sudo apt-get install -y \
  ghostscript \
  tesseract-ocr \
  tesseract-ocr-eng \
  tesseract-ocr-deu \
  tesseract-ocr-fra \
  tesseract-ocr-spa \
  tesseract-ocr-swe \
  unpaper \
  pngquant
```

2. Install Python dependencies:

```bash
pip install -r requirements-web.txt
pip install -e .
```

3. Run the web interface:

```bash
python web_interface.py
```

## Usage

### Web Interface

1. Open `http://localhost:5000` in your browser
2. Upload a PDF or image file
3. Configure OCR options:
   - **Language**: Select the primary language of your document
   - **Optimization**: Choose optimization level (affects file size and processing time)
   - **Force OCR**: Process all pages even if they already contain text
   - **Deskew**: Automatically straighten skewed pages
   - **Clean**: Clean up image artifacts before OCR
4. Click "Process with OCR"
5. Download the processed PDF

### API Usage

You can also use the RESTful API for programmatic access:

```bash
# Upload and process a file
curl -X POST \
  -F "file=@document.pdf" \
  -F "language=eng" \
  -F "force_ocr=false" \
  http://localhost:5000/api/process
```

Response:
```json
{
  "success": true,
  "download_url": "/download/abc123_output.pdf"
}
```

## Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key (change in production)
- `MAX_CONTENT_LENGTH`: Maximum upload file size in bytes (default: 100MB)

### Supported Languages

- English (eng)
- German (deu)
- French (fra)
- Spanish (spa)
- Swedish (swe)
- Italian (ita)
- Portuguese (por)
- Russian (rus)
- Chinese Simplified (chi_sim)
- Japanese (jpn)

Additional languages can be added by installing the corresponding Tesseract language packs.

## Security Notes

- Files are automatically deleted after download
- Temporary files use unique identifiers to prevent conflicts
- File uploads are limited to specific safe formats
- Consider using HTTPS in production
- Change the SECRET_KEY in production environments

## Troubleshooting

### Common Issues

1. **File too large**: Increase `MAX_CONTENT_LENGTH` in the configuration
2. **Language not available**: Install additional Tesseract language packs
3. **OCR fails**: Check that the input file is not corrupted and is a supported format
4. **Permission errors**: Ensure the application has write access to the temp directory

### Docker Issues

1. **Port already in use**: Change the port mapping in docker-compose.yml
2. **Build fails**: Ensure you have sufficient disk space and Docker is up to date

## Development

To modify the web interface:

1. Edit `web_interface.py` for backend changes
2. Edit templates in `templates/` for frontend changes
3. Rebuild the Docker image after changes

## License

This web interface follows the same license as OCRmyPDF (MPL-2.0).
