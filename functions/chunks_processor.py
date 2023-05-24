import openai
import os
from functions.error_handler import handle_error

API_KEY = os.getenv('API_KEY')

def process_chunks(text):
    # Authenticate with OpenAI API and summarize the text
    openai.api_key = API_KEY

    # Split the input text into smaller chunks and process each chunk separately
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
            return None  # Handle OpenAI API error
        else:
            summary = completions.choices[0].text.strip()
            summaries.append(summary)

    if summaries is None:
        return handle_error(Exception(), custom_message="Unable to generate a summary with OpenAI API.")

    return summaries
