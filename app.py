from flask import Flask, render_template, request
import docx2txt
import openai
import googletrans
import requests
import os
from PyPDF2 import PdfReader
import os
from azure.storage.blob import BlobServiceClient, BlobClient


connection_string = os.getenv('CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connection_string)


API_KEY = os.getenv('API_KEY')

# Use the api_key in your code


app = Flask(__name__)

 
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded file from the user
        file = request.files['file']
        # Save the file to a temporary location
        file_path = os.path.join('uploads', file.filename)
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

        if not text:
            return "Ingen tekst ble funnet i filen."
        else:
            # Authenticate with the OpenAI API and generate a summary of the text
            openai.api_key = API_KEY

            prompt = f"Please summarize the following article:\n{text}\n\nSummary:"
            try:
                completions = openai.Completion.create(
                    engine="text-davinci-002",
                    prompt=prompt,
                    max_tokens=200,
                    timeout=120,
                )
            except Exception as e:
                return f"OpenAI API error: {e}"
            except requests.exceptions.ReadTimeout as e:
                return f"Request timed out: {e}"
            else:
                if completions is None:
                    return "Kunne ikke generere et sammendrag med OpenAI API."
                else:
                    summary = completions.choices[0].text.strip()

                    if summary is None:
                        return "Kunne ikke generere et sammendrag med OpenAI API."

                    # Print the summary before and after translation
                    print(f"Summary before translation: {summary}")
                    translator = googletrans.Translator()
                    try:
                        translated_text = translator.translate(
                            summary, src="en", dest="no").text
                    except AttributeError as e:
                        print(f"Google Translate error: {e}")
                        print(f"Summary after translation: {translated_text}")
                        return "Kunne ikke oversette sammendraget."
                    else:
                        return render_template('index.html', summary=translated_text)

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
