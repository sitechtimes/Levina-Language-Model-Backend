import pandas as pd
import os
import subprocess
import shutil
import dotenv
import copy
from pydub import AudioSegment

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
    for path in os.listdir("training_data/aligned_output/"):
        if path.endswith(".TextGrid"):
            with open(os.path.join("training_data/aligned_output/", path), "r", encoding="utf-8") as f:
                content = f.read()
            single_file_data = extract_phonemes(content)
            full_data = full_data + single_file_data
    full_data_no_whitespace = copy.deepcopy(full_data)
    for phoneme, duration in full_data:
        if phoneme == '':
            full_data_no_whitespace.remove((phoneme, duration))
    phoneme_df = pd.DataFrame(full_data_no_whitespace, columns=["phoneme", "duration"])
    phoneme_counts = phoneme_df['phoneme'].value_counts().reset_index()
    phoneme_counts.columns = ['phoneme', 'count']
    phoneme_avg_durations = phoneme_df.groupby('phoneme')['duration'].mean().reset_index()
    phoneme_avg_durations.columns = ['phoneme', 'avg_duration']
    phoneme_stats = pd.merge(phoneme_counts, phoneme_avg_durations, on='phoneme')
    print(phoneme_stats)

# formulate_data(5)
# align()
organize_phonemes()
