from flask import render_template
import requests

def handle_error(error, custom_message=None):
    if isinstance(error, AttributeError):
        error_message = custom_message if custom_message else "Attribute error occurred."
        return render_template('error.html', error=error_message)
    elif isinstance(error, requests.exceptions.ReadTimeout):
        error_message = custom_message if custom_message else "Request timed out."
        return render_template('error.html', error=error_message)
    elif isinstance(error, ValueError) and "Unsupported file format" in str(error):
        error_message = custom_message if custom_message else "No files selected or Unsupported file format. Please upload a .docx, .pdf, or .txt file."
        return render_template('error.html', error=error_message)
    else:
        error_message = custom_message if custom_message else "An error occurred."
        return render_template('error.html', error=error_message)
