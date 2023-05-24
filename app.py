from flask import Flask, render_template, request
import requests
from functions.file_processor import process_file
from functions.error_handler import handle_error
from functions.chunks_processor import process_chunks
from functions.summaries_translator import translate_summaries
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            # Input
            file = request.files['file']

            # Process file and extract text
            text, file_path = process_file(file)

            #Split text in chunks
            summaries = process_chunks(text)

            #Translate summaries
            translated_summaries = translate_summaries(summaries)

            # Clear cache
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