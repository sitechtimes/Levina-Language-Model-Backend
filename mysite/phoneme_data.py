import pandas as pd
import os
import subprocess
import shutil
import dotenv

dotenv.load_dotenv()
mfa_info = {
    "corpus_dir": "training_data/corpus",
    "output_dir": "training_data/aligned_output",
    "dictionary": "russian_mfa",
    "acoustic_model": "russian_mfa",
}


def formulate_data():
    tsv_file_path = os.getenv("TSV_FILE_TRAIN_PATH")
    print(tsv_file_path)
    df = pd.read_csv(tsv_file_path, sep='\t')
    # print(df.head())
    df_train = df[df["age"].isin(["twenties", "teens"])]
    print(df_train.head(20))
    print(len(df_train))
    small_df = df_train[:3]
    for row in small_df.itertuples():
        full_path = tsv_file_path.rsplit("/", 1)[0] + "/"
        shutil.copy(full_path + row.path, "training_data/corpus/")
    wav_path = ""
    transcriptoin_path = ""


def align():
    conda_bat = os.getenv("CONDA_BAT")
    print(conda_bat)
    audio_path = "data/corpus/audio.wav"


    cmd = f'"{conda_bat}" run -n aligner mfa align "{mfa_info["corpus_dir"]}" "{mfa_info["dictionary"]}" "{mfa_info["acoustic_model"]}" "{mfa_info["output_dir"]}" --verbose --single_speaker --output_per_utterance_log_likelihoods true --output_per_phone_log_likelihoods true"'

    # cmd = f'"{conda_bat}" run -n aligner mfa version'

    subprocess.run(cmd, shell=True, check=True)


formulate_data()