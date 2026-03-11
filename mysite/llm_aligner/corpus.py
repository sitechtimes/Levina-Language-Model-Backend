import os
import re
import shutil
import unicodedata
from pathlib import Path
from pydub import AudioSegment
import pandas as pd

from .loading_bar import loading_bar


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
