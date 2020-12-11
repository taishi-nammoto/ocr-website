from googletrans import Translator
from textblob import TextBlob

def haw_to_eng(hawaiian_text):
    blob = TextBlob(hawaiian_text)
    translation = blob.translate(to='en')

    if translation is None: # This is a backup for textblob
        translator = Translator()
        translation = translator.translate(hawaiian_text)
        translation = translation.text
    return str(translation)
