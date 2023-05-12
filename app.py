from flask import Flask, render_template, request
import docx2txt
import openai
import googletrans
import requests
import os
from PyPDF2 import PdfReader
from azure.storage.blob import BlobServiceClient

API_KEY = os.getenv('API_KEY')
STORAGE_CONNECTION_STRING = os.getenv('STORAGE_CONNECTION_STRING')
STORAGE_CONTAINER_NAME = os.getenv('STORAGE_CONTAINER_NAME')

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get the uploaded file from the user
        file = request.files['file']

        # Extract the text from the uploaded file
        text = ''
        if file.filename.endswith('.docx'):
            text = docx2txt.process(file)
        elif file.filename.endswith('.pdf'):
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text()
        elif file.filename.endswith('.txt'):
            text = file.read().decode('utf-8')

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
                        # Store the file in Azure Blob Storage
                        blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
                        container_client = blob_service_client.get_container_client(STORAGE_CONTAINER_NAME)
                        blob_client = container_client.upload_blob(name=file.filename, data=file.read())

                        return render_template('index.html', summary=translated_text)

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
