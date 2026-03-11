import unicodedata
import re
import ast
from pathlib import Path
from .g2p import g2p_with_alignment



def get_words_from_textgrid(text_grid_content: str):
    """
    Return a list of non-empty word strings from the 'words' (item [1]) tier of a TextGrid content.
    """
    # isolate the item [1] block (words) up to item [2]
    _, _, words_block = text_grid_content.partition("item [1]:")
    if not words_block:
        return []
    words_block, _, _ = words_block.partition("item [2]:")
    # extract all text = "..." occurrences and filter out empty strings
    texts = re.findall(r'text\s*=\s*"([^"]*)"', words_block)
    return [t for t in texts if t.strip() != ""]



def create_mapping_dictionary():
    
    mapping = {}
    if Path("Phoneme_word_mappings.jsonl").exists():
        with open("Phoneme_word_mappings.jsonl", "r", encoding="utf-8") as mf:
            for line in mf:
                line = line.strip()
                if not line:
                    continue
                parts = line.split(" ", 2)
                if len(parts) < 3:
                    continue
                form, phon_seq, stress_str = parts
                try:
                    stress_positions = list(ast.literal_eval(stress_str))
                except Exception:
                    print("error parsing stress array")
                    stress_positions = []
                # normalize, just in case
                form_norm = unicodedata.normalize("NFC", unicodedata.normalize("NFD", form).replace("\u0301", "")).lower()
                mapping[form_norm] = stress_positions
    if mapping == {}:
        print("Mapping dictionary is empty. Please run create_phoneme_word_mappings() first to generate the mapping file.")
        raise ValueError("Mapping dictionary is empty. Please run create_phoneme_word_mappings() first to generate the mapping file.")
    return mapping




def extract_phonemes(text_grid_content,mapping):
    phonemes = []
    durations = []
    words = get_words_from_textgrid(text_grid_content)
    phoneme_stress_idxs_combined = []
    word_phoneme_counts = []
    for word in words:
        # normalize textgrid word: remove combining acute, NFC, lowercase
        word_norm = unicodedata.normalize("NFC", unicodedata.normalize("NFD", word).replace("\u0301", "")).lower()
        letter_stresses = mapping.get(word_norm, [])
        # convert letter stress positions -> phoneme indices via g2p alignment (ex. the letter л to the phoneme for that letter)
        phoneme_stress_idxs = set()
        aligned, _ = g2p_with_alignment(word_norm)
        for pi, (p, letter_idxs) in enumerate(aligned):
            if any(i in letter_stresses for i in letter_idxs):
                phoneme_stress_idxs.add(pi)
        phoneme_stress_idxs_combined.append(phoneme_stress_idxs)
        word_phoneme_counts.append(len(aligned))

    # compute global stressed phoneme indices across words
    stressed_global_indices = set()
    offset = 0
    for count, idxset in zip(word_phoneme_counts, phoneme_stress_idxs_combined):
        for idx in idxset:
            stressed_global_indices.add(offset + idx)
        offset += count

    # print(f"Global stressed phoneme indices: {sorted(stressed_global_indices)}")

    #phoneme_stress_idxs_combined encompasses the indexes of stress
    _,_,phoneme_text = text_grid_content.partition("item [2]:")
    intervals = phoneme_text.split("intervals [")[1:]
    phoneme_index = 0  # counts only non-empty phoneme tokens to align with g2p output
    for interval in intervals:
        if "text" in interval:
            _,_,text = interval.partition("text = ")
            phoneme = text.strip().strip('"')

            _,_,xmin = interval.partition("xmin = ")
            xmin,_,_ = xmin.partition("\n")
            xmin = float(xmin.strip())
            _,_,xmax = interval.partition("xmax = ")
            xmax,_,_ = xmax.partition("\n")
            xmax = float(xmax.strip())
            duration = xmax - xmin
            durations.append(duration)

            # decide stressed marking only for non-empty phonemes "error handling"
            if phoneme != "":
                if phoneme_index in stressed_global_indices:
                    phoneme_marked = f"{phoneme} 1"
                else:
                    phoneme_marked = phoneme
                phoneme_index += 1
            else:
                phoneme_marked = phoneme

            phonemes.append(phoneme_marked)

            if len(phonemes) != len(durations):
                raise ValueError("Mismatched phonemes and durations lengths")
    phoneme_data = list(zip(phonemes, durations))
    return phoneme_data

