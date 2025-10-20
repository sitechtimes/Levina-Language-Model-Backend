import re
import random
import wikipedia


def simple_clean_text(s: str) -> str:
    s = s.strip()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[\x00-\x1f\x7f]', '', s)
    return s

def is_simple_sentence(s: str, min_words=5, max_words=20, min_chars=20, max_chars=180) -> bool:
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
    print(page_titles)
    for page in page_titles:
        content = wikipedia.page(page).content
        samples.append(content)
    return samples
print(load_simple_english_sentences(5))
