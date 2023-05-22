from flask import Flask, render_template, request
import docx2txt
import openai
import googletrans
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


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded file from the user
        file = request.files['file']
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

        if not text:
            return handle_error(Exception(), custom_message="No text found in the file.")
        else:
            # Authenticate with the OpenAI API and generate a summary of the text
            openai.api_key = API_KEY

            # Split the input text into smaller chunks and process each chunk separately
            try:
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

                translator = Translator()
                try:
                    for summary in summaries:
                        translation = translator.translate(summary, src='en', dest='no')
                        if translation is not None and hasattr(translation, 'text'):
                            translated_text = translation.text
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            return render_template('index.html', summary=translated_text)
                        else:
                            return handle_error(AttributeError(), custom_message="Unable to translate the summary.")
                except AttributeError as e:
                    return handle_error(e)
            except Exception as e:
                return handle_error(e)
            except requests.exceptions.ReadTimeout as e:
                return handle_error(e)
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
