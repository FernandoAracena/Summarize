from flask import Flask, render_template, request
import docx2txt
import openai
import googletrans
import requests
import os
from PyPDF2 import PdfReader
import shutil
import time

API_KEY = os.getenv('API_KEY')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded file from the user
        file = request.files['file']
        # Create the "uploads" folder if it doesn't exist
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        else:
            # Clear the contents of the "uploads" folder
            shutil.rmtree('uploads')
            os.makedirs('uploads')
        # Generate a unique filename based on the current timestamp
        filename = f"{int(time.time())}_{file.filename}"
        file_path = os.path.join('uploads', filename)
        file.save(file_path)

        # Rest of your code...
        # Extract the text from the uploaded file
        # Authenticate with the OpenAI API and generate a summary of the text
        # Perform translation
        # Render the template with the translated summary

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
