from flask import Flask, render_template, request
import docx2txt
from PyPDF2 import PdfReader
import os
import uuid
from googletrans import Translator
import openai
import requests

API_KEY = os.getenv('API_KEY')

app = Flask(__name__)

# Error handling function
def handle_error(error, custom_message=None):
    if isinstance(error, AttributeError):
        # Handle AttributeError with a custom error message
        error_message = custom_message if custom_message else "Attribute error occurred."
        return render_template('error.html', error=error_message)
    elif isinstance(error, requests.exceptions.ReadTimeout):
        # Handle ReadTimeout error with a custom error message
        error_message = custom_message if custom_message else "Request timed out."
        return render_template('error.html', error=error_message)
    else:
        # Handle other exceptions with a generic error message
        error_message = custom_message if custom_message else "An error occurred."
        return render_template('error.html', error=error_message)

# Extract text from the uploaded file
def extract_text(file_path):
    text = ''
    if file_path.endswith('.docx'):
        text = docx2txt.process(file_path)
    elif file_path.endswith('.pdf'):
        with open(file_path, 'rb') as f:
            pdf_reader = PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
    elif file_path.endswith('.txt'):
        with open(file_path, 'r') as f:
            text = f.read()
    else:
        return handle_error(Exception(), custom_message="Please select a .docx, .pdf, or .txt file.")
    return text

# Translate text using Google Translate
def translate_text(text):
    translator = Translator()
    translation = translator.translate(text, src='en', dest='no')
    if translation is not None and hasattr(translation, 'text'):
        translated_text = translation.text
        return translated_text
    else:
        raise AttributeError("Unable to translate the summary.")

# Process the uploaded file
def process_file(file):
    # Create the "uploads" folder if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    # Generate a unique filename
    filename = f"{uuid.uuid4().hex}"
    file_extension = os.path.splitext(file.filename)[1]  # Get the file extension
    filename_with_extension = f"{filename}{file_extension}"
    file_path = os.path.join('uploads', filename_with_extension)
    # Save the file to a temporary location
    file.save(file_path)

    # Extract the text from the uploaded file
    text = extract_text(file_path)
    if not text:
        raise Exception("No text found in the file.")
    return text, file_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            file = request.files['file']
            text, file_path = process_file(file)
            openai.api_key = API_KEY

            text_chunks = [text[i:i+4096] for i in range(0, len(text), 4096)]
            summaries = []
            for chunk in text_chunks:
                prompt = f"Please summarize the following article:\n{chunk}\n\nSummary:"
                completions = openai.Completion.create(
                    engine="text-davinci-002",
                    prompt=prompt,
                    max_tokens=300,
                )
                if completions is None:
                    return handle_error(Exception(), custom_message="Unable to generate a summary with OpenAI API.")
                else:
                    summary = completions.choices[0].text.strip()
                    summaries.append(summary)

            translated_summaries = []
            for summary in summaries:
                translated_text = translate_text(summary)
                translated_summaries.append(translated_text)

            if os.path.exists(file_path):
                os.remove(file_path)
            return render_template('index.html', summary=translated_summaries)
        except AttributeError as e:
            return handle_error(e)
        except requests.exceptions.ReadTimeout as e:
            return handle_error(e)
        except Exception as e:
            return handle_error(e)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
