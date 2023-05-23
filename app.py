from flask import Flask, render_template, request
import openai
import requests
from helpers import translate_text
from file_processor import process_file
from error_handler import handle_error
import os

API_KEY = os.getenv('API_KEY')

app = Flask(__name__)

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
