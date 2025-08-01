#!/usr/bin/env python3
"""
Simple Flask web interface for OCRmyPDF
Allows uploading PDF/image files, running OCR, and downloading the result.
"""

import os
import tempfile
import uuid
from pathlib import Path
from flask import Flask, request, render_template, send_file, flash, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
import ocrmypdf
from ocrmypdf.exceptions import ExitCode

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'tif', 'bmp', 'gif'}

# Directory for temporary files
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and OCR processing."""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))
    
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload PDF, PNG, JPG, TIFF, BMP, or GIF files.', 'error')
        return redirect(url_for('index'))
    
    if file:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        input_path = Path(app.config['UPLOAD_FOLDER']) / f"{file_id}_input_{filename}"
        output_path = Path(app.config['UPLOAD_FOLDER']) / f"{file_id}_output.pdf"
        
        # Save uploaded file
        file.save(input_path)
        
        # Get OCR options from form
        language = request.form.get('language', 'eng')
        force_ocr = 'force_ocr' in request.form
        deskew = 'deskew' in request.form
        clean = 'clean' in request.form
        optimize = int(request.form.get('optimize', '1'))
        
        try:
            # Run OCR
            ocrmypdf.ocr(
                input_file=input_path,
                output_file=output_path,
                language=[language],
                force_ocr=force_ocr,
                deskew=deskew,
                clean=clean,
                optimize=optimize,
                skip_text=False if force_ocr else None,
                progress_bar=False
            )
            
            # Clean up input file
            input_path.unlink()
            
            # Return success page with download link
            return render_template('success.html', 
                                 output_file=output_path.name,
                                 original_filename=filename)
            
        except Exception as e:
            # Clean up files on error
            if input_path.exists():
                input_path.unlink()
            if output_path.exists():
                output_path.unlink()
            
            error_msg = f"OCR processing failed: {str(e)}"
            flash(error_msg, 'error')
            return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    """Download processed file."""
    file_path = Path(app.config['UPLOAD_FOLDER']) / filename
    
    if not file_path.exists():
        flash('File not found or has expired', 'error')
        return redirect(url_for('index'))
    
    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"ocr_{filename}",
            mimetype='application/pdf'
        )
    finally:
        # Clean up file after download
        try:
            file_path.unlink()
        except:
            pass  # Ignore cleanup errors

@app.route('/api/process', methods=['POST'])
def api_process():
    """API endpoint for programmatic access."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    input_path = Path(app.config['UPLOAD_FOLDER']) / f"{file_id}_input_{filename}"
    output_path = Path(app.config['UPLOAD_FOLDER']) / f"{file_id}_output.pdf"
    
    # Save uploaded file
    file.save(input_path)
    
    # Get OCR options
    language = request.form.get('language', 'eng')
    force_ocr = request.form.get('force_ocr', 'false').lower() == 'true'
    
    try:
        # Run OCR
        ocrmypdf.ocr(
            input_file=input_path,
            output_file=output_path,
            language=[language],
            force_ocr=force_ocr,
            progress_bar=False
        )
        
        # Clean up input file
        input_path.unlink()
        
        return jsonify({
            'success': True,
            'download_url': url_for('download_file', filename=output_path.name)
        })
        
    except Exception as e:
        # Clean up files on error
        if input_path.exists():
            input_path.unlink()
        if output_path.exists():
            output_path.unlink()
        
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
