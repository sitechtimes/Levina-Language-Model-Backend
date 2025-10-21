import re
import random
import wikipedia
from googletrans import Translator
import asyncio
import pandas as pd

def simple_clean_text(s):
    s = s.strip()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[\x00-\x1f\x7f]', '', s)
    return s

def is_simple_sentence(s, min_words=5, max_words=20, min_chars=20, max_chars=180):
    s = s.strip()
    if len(s) < min_chars or len(s) > max_chars:
        return False
    if re.search(r'http[s]?://', s):
        return False
    words = s.split()
    if len(words) < min_words or len(words) > max_words:
        return False
    if len(re.findall(r'[\;:—–]', s)) > 2:
        return False
    if len([w for w in words if w.isupper() and len(w) > 1]) > 0:
        return False
    return True



def load_simple_english_sentences(text_samples):
    wikipedia.set_lang("simple")
    samples = []
    page_titles = wikipedia.random(pages=text_samples)
    for page in page_titles:
        content = wikipedia.page(page).content
        samples.append(content)  
    return samples
# print(load_simple_english_sentences(5))

async def google_translate(text):
    translator = Translator()
    translation = await translator.translate(text, dest="ru")
    return translation.text

# print(asyncio.run(google_translate("Hello, how are you?")))


def create_translation_dataset(num_samples):
    dataset = pd.DataFrame(columns=['russian_text','Translator or Human'])
    text_samples = load_simple_english_sentences(num_samples)
    translated_texts = []
    for text in text_samples:
        cleaned_text = simple_clean_text(text)
        translated_text = asyncio.run(google_translate(cleaned_text))
        translated_texts.append(translated_text)
        dataset = dataset.append({'russian_text': translated_text, 'Translator or Human': 0}, ignore_index=True)

create_translation_dataset(10)