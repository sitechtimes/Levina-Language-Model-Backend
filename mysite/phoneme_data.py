import pandas as pd
import os
import subprocess
import shutil
import dotenv
import copy
from pydub import AudioSegment
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import unicodedata
import json
from pathlib import Path
import re, unicodedata
import ast


dotenv.load_dotenv()
mfa_info = {
    "corpus_dir": "training_data/corpus",
    "output_dir": "training_data/aligned_output",
    "dictionary": "russian_mfa",
    "acoustic_model": "russian_mfa",
}

RUS_MFA_G2P = {
    # vowels
    "а": ["a"],
    "о": ["o"],
    "у": ["u"],
    "ы": ["ɨ"],
    "э": ["e"],
    "и": ["i"],
    "е": ["e"],
    "ё": ["ɐ", "o"],
    "ю": ["j", "u"],
    "я": ["j", "a"],

    "б": ["b"],
    "в": ["v"],
    "г": ["ɡ"],
    "д": ["d̪"],
    "ж": ["ʐ"],
    "з": ["z̪"],
    "й": ["j"],
    "к": ["k"],
    "л": ["l"],
    "м": ["m"],
    "н": ["n̪"],
    "п": ["p"],
    "р": ["r"],
    "с": ["s̪"],
    "т": ["t̪"],
    "ф": ["f"],
    "х": ["x"],
    "ц": ["t̪s̪"],
    "ч": ["tɕ"],
    "ш": ["ʂ"],
    "щ": ["ɕ"],
    "ь": [],
    "ъ": [],

    #old letters

    "ѣ": ["e"],
    "ѵ": ["i"],
    "ѳ": ["f"],
    "ѝ": ["i"],
}


def convert_to_wav(file_name):
    file_name = file_name.split(".mp3")[0]
    input_mp3 = "training_data/corpus/" + file_name + ".mp3"
    output_wav = "training_data/corpus/" + file_name + ".wav"
    audio = AudioSegment.from_mp3(input_mp3).set_frame_rate(16000).set_channels(1).set_sample_width(2)
    audio.export(output_wav, format="wav")
    os.remove(input_mp3)



def clean(text):
    #currently not used only if corpus needs to be cleaned
    text = unicodedata.normalize("NFC", text)
    text = text.lower()
    text = text.replace("ё", "е")  # OR keep ё everywhere, choose one , even though in russian language they are different letters
    text = re.sub(r"[^а-я\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

for txt in Path("training_data/corpus").rglob("*.txt"):
    txt.write_text(clean(txt.read_text(encoding="utf-8")), encoding="utf-8")


def formulate_data(files:int):
    tsv_file_path = os.getenv("TSV_FILE_TRAIN_PATH")
    df = pd.read_csv(tsv_file_path, sep='\t')
    df_train = df[df["age"].isin(["twenties", "teens"])]
    df_train = df_train[:files]
    for row in df_train.itertuples():
        full_path = tsv_file_path.rsplit("/", 1)[0] + "/clips/"
        shutil.copy(full_path + row.path, "training_data/corpus/")
        convert_to_wav(row.path)
        path = (full_path + row.path).rsplit(".", 1)[0] + ".lab"
        path = path.split("clips/", 1)[1]
        path = os.path.join("training_data/corpus/", path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(row.sentence)
    print("Moved All Files! Total Files Moved: ", len(df_train))


def align():
    conda_bat = os.getenv("CONDA_BAT")
    # dictionary_output_path = os.getenv("STRESSED_DICTIONARY_PATH")
    # dictionary_output_path_trimmed = os.path.splitext(os.path.basename(dictionary_output_path))[0]  # 'russian_mfa_stressed_output_new'
    # print(conda_bat)
    # print(dictionary_output_path_trimmed)
    audio_path = "data/corpus/audio.wav"

    # cmd = f'"{conda_bat}" run -n aligner mfa --help'
    # subprocess.run(cmd, shell=True, check=True)

    # cmd = f'"{conda_bat}" run -n aligner mfa align "{mfa_info["corpus_dir"]}" "{mfa_info["dictionary"]}" "{mfa_info["acoustic_model"]}" "{mfa_info["output_dir"]}" --verbose --single_speaker --output_per_utterance_log_likelihoods true --output_per_phone_log_likelihoods true"'
    
    
    # cmd = f'"{conda_bat}" run -n aligner mfa validate_dictionary {dictionary_output_path_trimmed}'

    #main production script below
    cmd = f"{conda_bat} run -n aligner mfa align training_data/corpus russian_mfa russian_mfa training_data/aligned_output --clean --verbose"
    
    #working one below
    # cmd = f"{conda_bat} run -n aligner mfa align training_data/corpus russian_mfa russian_mfa training_data/aligned_output --clean --verbose"
    
    # cmd = f'"{conda_bat}" run -n aligner mfa version'

    subprocess.run(cmd, shell=True, check=True)

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

def organize_phonemes():
    full_data = []
    full_data_separated = []
    mapping = create_mapping_dictionary()
    file_count_path = Path("training_data/aligned_output/")
    files_count = len([p for p in file_count_path.rglob('*') if p.is_file()])
    print(files_count)
    count = 0
    loading_bar(count, files_count)
    for path in os.listdir("training_data/aligned_output/"):
        count += 1
        if count % 10 == 0:
            loading_bar(count, files_count)
        if path.endswith(".TextGrid"):
            with open(os.path.join("training_data/aligned_output/", path), "r", encoding="utf-8") as f:
                content = f.read()
            single_file_data = extract_phonemes(content,mapping)
            full_data = full_data + single_file_data
            full_data_separated.append(single_file_data)
    full_data_no_whitespace = [(p, d) for p, d in full_data if p != '']

    phoneme_df = pd.DataFrame(full_data_no_whitespace, columns=["phoneme", "duration"])
    return phoneme_df,full_data_separated


def run_phoneme_stats():
    phoneme_df,separated_data = organize_phonemes()
    phoneme_counts = phoneme_df['phoneme'].value_counts().reset_index()
    phoneme_counts.columns = ['phoneme', 'count']
    phoneme_avg_durations = phoneme_df.groupby('phoneme')['duration'].mean().reset_index()
    phoneme_avg_durations.columns = ['phoneme', 'avg_duration']
    phoneme_std_deviations = phoneme_df.groupby('phoneme')['duration'].std().reset_index()
    phoneme_std_deviations.columns = ['phoneme', 'std_deviation']
    phoneme_std_deviations = phoneme_std_deviations.round(6)
    phoneme_stats = pd.merge(phoneme_counts, phoneme_avg_durations, on='phoneme').merge(phoneme_std_deviations, on='phoneme')
    # print(phoneme_stats)


    # make the normalized durations
    clip_means = []
    for clip in separated_data:
        clip_df = pd.DataFrame(clip, columns=["phoneme", "duration"])
        clip_mean = clip_df['duration'].mean()
        clip_means.append(clip_mean)
    total_mean = sum(clip_means) / len(clip_means)

    separated_data_normalized = []

    for i, clip_phonemes in enumerate(separated_data):
        clip_mean = clip_means[i]
        normalization_factor = total_mean / clip_mean
        normalized_clip = []
        
        for phoneme, duration in clip_phonemes:
            if phoneme == "":
                continue
            normalized_duration = duration * normalization_factor
            normalized_clip.append((phoneme, normalized_duration))
        
        separated_data_normalized.append(normalized_clip)

    #add the rest of that data to the pandas dataframe
    # print(separated_data_normalized)
    normalized_phonemes_dict = {}
    for clip in separated_data_normalized:
        for phoneme, duration in clip:
            if phoneme not in normalized_phonemes_dict:
                normalized_phonemes_dict[phoneme] = []
            normalized_phonemes_dict[phoneme].append(duration)
    normalized_averages = {}
    normalized_stddevs = {}
    # counts = {}
    for phoneme,durations in normalized_phonemes_dict.items():
        normalized_averages[phoneme] = sum(durations) / len(durations)
        mean = normalized_averages[phoneme]
        variance = sum((x - mean) ** 2 for x in durations) / len(durations)
        normalized_stddevs[phoneme] = variance ** 0.5
        # counts[phoneme] = len(durations)
    print(normalized_averages)
    print(normalized_stddevs)
    # print(counts)
    normalized_averages = pd.DataFrame(list(normalized_averages.items()), columns=['phoneme', 'normalized_avg_duration'])
    normalized_stddevs = pd.DataFrame(list(normalized_stddevs.items()), columns=['phoneme', 'normalized_std_deviation'])
    # counts = pd.DataFrame(list(counts.items()), columns=['phoneme', 'normalized_count'])
    normalized_phoneme_stats = pd.merge(normalized_averages, normalized_stddevs, on='phoneme')
    normalized_phoneme_stats = normalized_phoneme_stats.merge(phoneme_stats, on='phoneme')
    normalized_phoneme_stats.to_csv("phoneme_stats_normalized.csv", index=False)
    print(normalized_phoneme_stats)


def plot_phoneme_durations(phoneme_stats):
    plt.figure(figsize=(12, 6))
    mean_counts = phoneme_stats['count'].mean()
    for i, row in phoneme_stats.sort_values('count').iterrows():
        count = row['count']
        color_intensity = count/mean_counts
        plt.bar(row['phoneme'], row['avg_duration'], color=cm.Reds(color_intensity), edgecolor = "black", linewidth = 0.8, yerr=row['std_deviation'], capsize=2)

    # plt.bar(phoneme_stats['phoneme'], phoneme_stats['avg_duration'], yerr=phoneme_stats['std_deviation'], capsize=5)
    plt.xlabel('Phoneme')
    plt.ylabel('Average Duration (s)')
    plt.title('Average Phoneme Durations with Standard Deviation')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

def stressed_positions(word: str):
    positions = []
    base_index = -1

    for char in word:
        if not unicodedata.combining(char):
            base_index += 1  
        if char == "\u0301":
            positions.append(base_index)
    return positions

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

def loading_bar(current,total):
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    percent = (current / total) * 100
    print(f'\r|{bar}| {percent:.2f}% Complete ({current/1000000:.2f} MB out of {total/1000000:.2f} MB)', end='\r', flush=True)
    if current == total:
        print()


def g2p_with_alignment(word):
    aligned = []
    unknown_characters = set()
    for i, ch in enumerate(word):
        phones = RUS_MFA_G2P.get(ch.lower())
        if phones is None:
            # raise ValueError(f"Unknown character: {ch}")
            unknown_characters.add(ch)
            continue
        for p in phones:
            aligned.append((p, [i]))
    return aligned,unknown_characters

VOWELS = set(["a","o","u","ɨ","e","i","ɐ"])

def apply_stress(aligned, stress_positions):
    stressed = []
    for p, idxs in aligned:
        if p in VOWELS and any(i in stress_positions for i in idxs):
            stressed.append(p + "ˈ")  # new stressed phoneme
        else:
            stressed.append(p)
    return stressed


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


def test_dictionary():
    #checked out to be fine so now not used in code
    # load dictionary words
    dict_words = set()
    with open("russian_mfa_stressed_output.dict", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                dict_words.add(line.split()[0])

    # scan corpus
    unknown = set()
    for txt in Path("training_data/corpus").rglob("*.txt"):
        for w in txt.read_text(encoding="utf-8").split():
            if w not in dict_words:
                unknown.add(w)

    print("UNKNOWN WORD COUNT:", len(unknown))
    print("SAMPLE:", list(unknown)[:40])


#TRY NORMALIZED VS NON NORMALIZED THEN DO T TEST!!!

# test_dictionary()

# print("STEP 1: Creating stress dictionary (will read russian_dictionary.jsonl and write OUTPUT_JSONL_PATH)")
# create_stress_dictionary()

# print("STEP 2: Converting JSONL -> stressed dictionary (apply_stress_to_dictionary will write STRESSED_DICTIONARY_PATH)")
# apply_stress_to_dictionary()

# print("STEP 3: Normalizing stressed dictionary file (normalize_dictionary)")
# normalize_dictionary()

# print("STEP 4: Creating phoneme->word mappings (create_phoneme_word_mappings -> Phoneme_word_mappings.jsonl)")
# create_phoneme_word_mappings()

# print("STEP 5: Preparing corpus and copying clips + generating .lab files (formulate_data)")
# formulate_data(100000000000000)

# print("STEP 6: Running MFA alignment (align) to produce TextGrid outputs in training_data/aligned_output")
# align()

# print("STEP 7: Computing phoneme statistics from aligned TextGrids (run_phoneme_stats)")
# run_phoneme_stats()

print("STEP 8: Plotting phoneme durations from phoneme_stats_normalized.csv (plot_phoneme_durations)")
plot_phoneme_durations(pd.read_csv("phoneme_stats_normalized.csv"))

