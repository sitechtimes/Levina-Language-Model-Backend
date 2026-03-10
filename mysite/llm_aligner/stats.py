from pathlib import Path
import os
import pandas as pd
from typing import List, Tuple, Dict, Iterable
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import unicodedata, re, ast
from g2p import g2p_with_alignment


from loading_bar import loading_bar

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
