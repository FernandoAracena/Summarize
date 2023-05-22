from flask import Flask, render_template, request
import docx2txt
import openai
import requests
import os
from PyPDF2 import PdfReader
import uuid
from googletrans import Translator


API_KEY = os.getenv('API_KEY')

app = Flask(__name__)

# Error handling route
@app.errorhandler(Exception)
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


def save_file(file):
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
    return file_path


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
    return text


def generate_summary(text):
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
            raise Exception("Unable to generate a summary with OpenAI API.")
        
        summary = completions.choices[0].text.strip()
        summaries.append(summary)
    
    return summaries


def translate_summary(summary):
    translator = Translator()
    translation = translator.translate(summary, src='en', dest='no')
    
    if translation is not None and hasattr(translation, 'text'):
        return translation.text
    
    raise AttributeError("Unable to translate the summary.")


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        try:
            file_path = save_file(file)
            text = extract_text(file_path)
            
            if not text:
                raise Exception("No text found in the file.")
            
            summaries = generate_summary(text)
            translated_summaries = []
            
            for summary in summaries:
                translated_summary = translate_summary(summary)
                translated_summaries.append(translated_summary)
            
            os.remove(file_path)
            return render_template('index.html', summary=translated_summaries)
        
        except AttributeError as e:
            return handle_error(e)
        
        except Exception as e:
            return handle_error(e, custom_message="Something went wrong during processing.")
    
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
