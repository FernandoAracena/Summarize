from googletrans import Translator


def translate_summaries(summaries):
    translator = Translator()
    translated_summaries = []
    for summary in summaries:
        translation = translator.translate(summary, src='en', dest='no')
        if translation is not None and hasattr(translation, 'text'):
            translated_summary = translation.text
            translated_summaries.append(translated_summary)
        else:
            translated_summaries.append("")  # Handle translation failure
    return translated_summaries