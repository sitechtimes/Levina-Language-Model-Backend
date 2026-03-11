import os
import json
import unicodedata
from pathlib import Path

from .g2p import g2p_with_alignment, apply_stress, stressed_positions
from .loading_bar import loading_bar



def create_stress_dictionary():
    json_file_path = "russian_dictionary.jsonl"
    out_path = os.getenv("OUTPUT_JSONL_PATH")

    seen = set()
    total_bytes = os.path.getsize(json_file_path)
    written = 0
    bytes_read = 0
    stress_dict = {}
    with open(json_file_path, "r", encoding="utf-8") as inf, open(out_path, "w", encoding="utf-8") as outf:
        english_characters = {"a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z",
                                 "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"}
        for lineno,line in enumerate(inf,start=1):
            obj = json.loads(line)
            forms = obj.get("forms")
            if not forms:
                bytes_read += len(line.encode("utf-8"))
                continue
            for form in forms:
                form_text = form.get("form")
                if any(char in english_characters for char in form_text):
                    continue
                if not form_text or " " in form_text:
                    continue
                stress_position = stressed_positions(form_text)
                decomposed = unicodedata.normalize('NFD', form_text)
                unstressed_form_text = unicodedata.normalize('NFC', decomposed.replace('\u0301', ''))
                key = (unstressed_form_text, tuple(stress_position))
                if key not in seen:
                    seen.add(key)
                    written += 1

            bytes_read += len(line.encode("utf-8"))
            if lineno % 1000 == 0:
                loading_bar(bytes_read, total_bytes)
            # if written > 1000:
            #     break
    with open(out_path, "w", encoding="utf-8") as outf:
        for line in seen:
            unstressed_form_text, stress_position = line
            outf.write(json.dumps({"form": unstressed_form_text, "stress_positions": stress_position}, ensure_ascii=False) + "\n")
    print("wrote total forms: ", written)



def apply_stress_to_dictionary():
    input_path = os.getenv("OUTPUT_JSONL_PATH")
    output_path = os.getenv("STRESSED_DICTIONARY_PATH")
    total_bytes = os.path.getsize(input_path)
    bytes_read = 0
    with open(input_path, "r", encoding="utf-8") as inf, open(output_path, "w", encoding="utf-8") as outf:
        unknown_characters = set()
        count = 0
        for line in inf:
            bytes_read += len(line.encode("utf-8"))
            obj = json.loads(line)
            form = obj.get("form")
            stress_positions = obj.get("stress_positions", [])
            aligned,unknown_characters_sample = g2p_with_alignment(form)
            unknown_characters.update(unknown_characters_sample)
            stressed_phonemes = apply_stress(aligned, stress_positions)
            outf.write(f"{form} {' '.join(stressed_phonemes)}\n")
            count += 1
            loading_bar(bytes_read, total_bytes)
            # if count > 1000:
            #     break
    if unknown_characters:
        print("Unknown characters encountered during G2P conversion:", unknown_characters)

    print("Stressed dictionary created at:", output_path)



def create_phoneme_word_mappings():
    #Function that makes a jsonl file with each word, then the stress positoin of hte phoneme, NOT the letter
    input_path = os.getenv("OUTPUT_JSONL_PATH")
    output_path = "Phoneme_word_mappings.jsonl"
    total_bytes = os.path.getsize(input_path)
    bytes_read = 0
    with open(input_path, "r", encoding="utf-8") as inf, open(output_path, "w", encoding="utf-8") as outf:
        unknown_characters = set()
        count = 0
        for line in inf:
            bytes_read += len(line.encode("utf-8"))
            obj = json.loads(line)
            form = obj.get("form")
            stress_positions = obj.get("stress_positions", [])
            aligned,unknown_characters_sample = g2p_with_alignment(form)
            unknown_characters.update(unknown_characters_sample)
            stressed_phonemes = apply_stress(aligned, stress_positions)

            phoneme_sequence = ""
            for Tuple in aligned:
                phoneme_sequence += Tuple[0]
            
            outf.write(f"{form} {phoneme_sequence} {stress_positions}\n")
            #phoneme sequence needs to be packaged into the dictinoary in order to check to make sure the word to phoneme actaull aligns with the phonemes outputed by MFA
            count += 1
            loading_bar(bytes_read, total_bytes)
            # if count > 100:
            #     break
    if unknown_characters:
        print("Unknown characters encountered during G2P conversion:", unknown_characters)

    print("Stressed dictionary created at:", output_path)


def normalize_dictionary():
    input_path = os.getenv("STRESSED_DICTIONARY_PATH")
    text = Path(input_path).read_text(encoding="utf-8")
    text = unicodedata.normalize("NFC", text)
    Path(input_path).write_text(text, encoding="utf-8")

