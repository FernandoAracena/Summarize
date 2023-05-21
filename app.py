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

        if not text:
            return "Ingen tekst ble funnet i filen."
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
                        return "Kunne ikke generere et sammendrag med OpenAI API."
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
                            print("Translation failed: Unable to retrieve translated text") 
                            return "Kunne ikke oversette sammendraget."
                except AttributeError as e:
                    print("Google Translate error:", e)
                    return "Feil oppstod under oversettelsen av sammendraget."
                

            #prompt = f"Please summarize the following article:\n{text}\n\nSummary:"
            #try:
                #completions = openai.Completion.create(
                    #engine="text-davinci-002",
                    #prompt=prompt,
                    #max_tokens=200,
                    #timeout=120,
                #)
            except Exception as e:
                return f"OpenAI API error: {e}"
            except requests.exceptions.ReadTimeout as e:
                return f"Request timed out: {e}"
            #else:
                #if completions is None:
                    #return "Kunne ikke generere et sammendrag med OpenAI API."
                #else:
                    #summary = completions.choices[0].text.strip()
                    #if summary is None:
                        #return "Kunne ikke generere et sammendrag med OpenAI API."
                    
                    # Print the summary after translation
                    #translator = googletrans.Translator()
                    #try:
                        #translation = translator.translate(summary, src="en", dest="no")
                        #if translation is not None and hasattr(translation, 'text'):
                            #translated_text = translation.text
                            #if os.path.exists(file_path):
                                #os.remove(file_path)
                            #return render_template('index.html', summary=translated_text)
                        #else:
                            #print("Translation failed: Unable to retrieve translated text") 
                            #return "Kunne ikke oversette sammendraget."
                    #except AttributeError as e:
                        #print("Google Translate error:", e)
                        #return "Feil oppstod under oversettelsen av sammendraget."
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)