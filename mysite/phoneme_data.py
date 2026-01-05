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
dotenv.load_dotenv()
mfa_info = {
    "corpus_dir": "training_data/corpus",
    "output_dir": "training_data/aligned_output",
    "dictionary": "russian_mfa",
    "acoustic_model": "russian_mfa",
}


def convert_to_wav(file_name):
    print(file_name)
    file_name = file_name.split(".mp3")[0]
    input_mp3 = "training_data/corpus/" + file_name + ".mp3"
    output_wav = "training_data/corpus/" + file_name + ".wav"
    audio = AudioSegment.from_mp3(input_mp3).set_frame_rate(16000).set_channels(1).set_sample_width(2)
    audio.export(output_wav, format="wav")
    os.remove(input_mp3)


def formulate_data(files:int):
    tsv_file_path = os.getenv("TSV_FILE_TRAIN_PATH")
    print(tsv_file_path)
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
    print(conda_bat)
    audio_path = "data/corpus/audio.wav"

    # cmd = f'"{conda_bat}" run -n aligner mfa --help'
    # subprocess.run(cmd, shell=True, check=True)

    # cmd = f'"{conda_bat}" run -n aligner mfa align "{mfa_info["corpus_dir"]}" "{mfa_info["dictionary"]}" "{mfa_info["acoustic_model"]}" "{mfa_info["output_dir"]}" --verbose --single_speaker --output_per_utterance_log_likelihoods true --output_per_phone_log_likelihoods true"'
    cmd = f"{conda_bat} run -n aligner mfa align training_data/corpus russian_mfa russian_mfa training_data/aligned_output --clean"
    # cmd = f'"{conda_bat}" run -n aligner mfa version'

    subprocess.run(cmd, shell=True, check=True)

def extract_phonemes(text_grid_content):
    phonemes = []
    durations = []
    _,_,phoneme_text = text_grid_content.partition("item [2]:")
    intervals = phoneme_text.split("intervals [")[1:]
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
            phonemes.append(phoneme)
    phoneme_data = list(zip(phonemes, durations))
    return phoneme_data

def organize_phonemes():
    full_data = []
    full_data_separated = []
    for path in os.listdir("training_data/aligned_output/"):
        if path.endswith(".TextGrid"):
            with open(os.path.join("training_data/aligned_output/", path), "r", encoding="utf-8") as f:
                content = f.read()
            single_file_data = extract_phonemes(content)
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
        for lineno,line in enumerate(inf,start=1):
            obj = json.loads(line)
            forms = obj.get("forms")
            if not forms:
                bytes_read += len(line.encode("utf-8"))
                continue
            for form in forms:
                form_text = form.get("form")
                if not form_text or " " in form_text:
                    continue
                stress_position = stressed_positions(form_text)
                key = (form_text, tuple(stress_position))
                if key not in seen:
                    seen.add(key)
                    outf.write(json.dumps({"form": form_text, "stress_positions": stress_position}, ensure_ascii=False) + "\n")
                    written += 1

            bytes_read += len(line.encode("utf-8"))
            if lineno % 1000 == 0:
                loading_bar(bytes_read, total_bytes)
            # if written > 1000:
            #     break
    print("wrote total forms: ", written)

def loading_bar(current,total):
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    percent = (current / total) * 100
    print(f'\r|{bar}| {percent:.2f}% Complete ({current/1000000} megabytes out of {total/1000000} megabytes)', end='\r')
    if current == total:
        print()

# formulate_data(500)
# align()
# run_phoneme_stats()
# plot_phoneme_durations(pd.read_csv("phoneme_stats_normalized.csv"))
create_stress_dictionary()
