#!/usr/bin/env python3
"""
Simple Flask web interface for OCRmyPDF
Allows uploading PDF/image files, running OCR, and downloading the result.
"""

import os
import tempfile
import uuid
import zipfile
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

def generate_output_filename(original_filename, upload_folder):
    """Generate output filename based on input, always with _ocr suffix."""
    # Remove extension and add _ocr.pdf
    base_name = Path(original_filename).stem
    output_name = f"{base_name}_ocr.pdf"
    output_path = Path(upload_folder) / output_name
    
    # If that exists, add a number
    counter = 2
    while output_path.exists():
        output_name = f"{base_name}_ocr_{counter}.pdf"
        output_path = Path(upload_folder) / output_name
        counter += 1
    
    return output_name

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
        # Generate unique filename for temporary input file to prevent conflicts
        temp_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        input_path = Path(app.config['UPLOAD_FOLDER']) / f"{temp_id}_input_{filename}"
        
        # Generate output filename based on input name
        output_filename = generate_output_filename(filename, app.config['UPLOAD_FOLDER'])
        output_path = Path(app.config['UPLOAD_FOLDER']) / output_filename
        
        # Save uploaded file
        file.save(input_path)
        
        # Get OCR options from form
        language = request.form.get('language', 'eng')
        force_ocr = 'force_ocr' in request.form
        deskew = 'deskew' in request.form
        clean = 'clean' in request.form
        regular_pdf = 'regular_pdf' in request.form
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
                output_type='pdf' if regular_pdf else 'pdfa',
                progress_bar=False
            )
            
            # Clean up input file
            input_path.unlink()
            
            # Get file size for display
            file_size = output_path.stat().st_size
            
            # Redirect to results page with single file
            file_info = {
                'output_file': output_filename,
                'original_name': filename,
                'size': format_file_size(file_size)
            }
            
            return render_template('results.html', 
                                 processed_files=[file_info],
                                 file_ids=output_filename)
            
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
            download_name=filename,
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
    
    # Generate unique filename for temporary input file to prevent conflicts
    temp_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    input_path = Path(app.config['UPLOAD_FOLDER']) / f"{temp_id}_input_{filename}"
    
    # Generate output filename based on input name
    output_filename = generate_output_filename(filename, app.config['UPLOAD_FOLDER'])
    output_path = Path(app.config['UPLOAD_FOLDER']) / output_filename
    
    # Save uploaded file
    file.save(input_path)
    
    # Get OCR options from form
    language = request.form.get('language', 'eng')
    force_ocr = 'force_ocr' in request.form
    deskew = 'deskew' in request.form
    clean = 'clean' in request.form
    regular_pdf = 'regular_pdf' in request.form
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
            output_type='pdf' if regular_pdf else 'pdfa',
            progress_bar=False
        )
        
        # Clean up input file
        input_path.unlink()
        
        # Get file size for display
        file_size = output_path.stat().st_size
        
        return jsonify({
            'success': True,
            'output_file': output_filename,
            'original_name': filename,
            'size': format_file_size(file_size),
            'download_url': url_for('download_file', filename=output_filename)
        })
        
    except Exception as e:
        # Clean up files on error
        if input_path.exists():
            input_path.unlink()
        if output_path.exists():
            output_path.unlink()
        
        return jsonify({'error': str(e)}), 500

def format_file_size(bytes):
    """Format file size in human readable format."""
    if bytes == 0:
        return '0 Bytes'
    k = 1024
    sizes = ['Bytes', 'KB', 'MB', 'GB']
    i = 0
    while bytes >= k and i < len(sizes) - 1:
        bytes /= k
        i += 1
    return f"{bytes:.1f} {sizes[i]}"

@app.route('/results')
def results():
    """Display results page with download links for multiple files."""
    filenames = request.args.get('files', '').split(',')
    filenames = [fname.strip() for fname in filenames if fname.strip()]
    
    if not filenames:
        flash('No files found', 'error')
        return redirect(url_for('index'))
    
    processed_files = []
    for filename in filenames:
        file_path = Path(app.config['UPLOAD_FOLDER']) / filename
        if file_path.exists():
            file_size = file_path.stat().st_size
            # Clean up display name by removing _ocr suffix and numbers
            display_name = filename
            if filename.endswith('_ocr.pdf'):
                display_name = filename.replace('_ocr.pdf', '.pdf')
            elif '_ocr_' in filename and filename.endswith('.pdf'):
                # Handle _ocr_2.pdf, _ocr_3.pdf, etc.
                base_part = filename.split('_ocr_')[0]
                display_name = f"{base_part}.pdf"
            
            processed_files.append({
                'output_file': filename,
                'original_name': display_name,
                'size': format_file_size(file_size)
            })
    
    if not processed_files:
        flash('No processed files found', 'error')
        return redirect(url_for('index'))
    
    return render_template('results.html', 
                         processed_files=processed_files,
                         file_ids=','.join(filenames))

@app.route('/download_all/<filenames>')
def download_all(filenames):
    """Download all processed files as a ZIP archive."""
    filename_list = filenames.split(',')
    filename_list = [fname.strip() for fname in filename_list if fname.strip()]
    
    if not filename_list:
        flash('No files specified', 'error')
        return redirect(url_for('index'))
    
    # Create a temporary ZIP file
    zip_path = Path(app.config['UPLOAD_FOLDER']) / f"ocr_batch_{uuid.uuid4()}.zip"
    
    try:
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for filename in filename_list:
                filename = filename.strip()
                if filename:
                    file_path = Path(app.config['UPLOAD_FOLDER']) / filename
                    if file_path.exists():
                        zip_file.write(file_path, filename)
        
        return send_file(
            zip_path,
            as_attachment=True,
            download_name="ocr_batch.zip",
            mimetype='application/zip'
        )
    
    except Exception as e:
        flash(f'Error creating ZIP file: {str(e)}', 'error')
        return redirect(url_for('index'))
    
    finally:
        # Clean up ZIP file after a delay (you might want to implement this differently)
        pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
