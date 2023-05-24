# file_processor.py
import os
import uuid
from functions.text_extractor import extract_text

def process_file(file):
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    filename = f"{uuid.uuid4().hex}"
    file_extension = os.path.splitext(file.filename)[1]

    if file_extension not in ['.docx', '.pdf', '.txt']:
        raise ValueError("No files selected or Unsupported file format. Please upload a .docx, .pdf, or .txt file.")

    filename_with_extension = f"{filename}{file_extension}"
    file_path = os.path.join('uploads', filename_with_extension)
    file.save(file_path)

    text = extract_text(file_path)
    if not text:
        raise Exception("No text found in the file.")
    return text, file_path
