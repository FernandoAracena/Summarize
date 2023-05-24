from flask import Flask, render_template, request
from functions.file_processor import process_file
from functions.chunks_processor import process_chunks
from functions.summaries_translator import translate_summaries
import os

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        text, file_path = process_file(file)

        summaries = process_chunks(text)

        translated_summaries = translate_summaries(summaries)

        if os.path.exists(file_path):
            os.remove(file_path)

        return render_template('index.html', summary=translated_summaries)
        
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
