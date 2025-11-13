import whisper

import subprocess
import dotenv
import os
import shutil
import pandas as pd

dotenv.load_dotenv()
def transcribe():
    model = whisper.load_model("turbo")
    result = model.transcribe(audio_path, language="ru")
    print(result["text"])  
    with open("data/corpus/audio.lab", "w", encoding="utf8") as f:
        f.write(result["text"].strip())


mfa_info = {
    "corpus_dir": "data/corpus",
    "output_dir": "data/aligned_output",
    "dictionary": "russian_mfa",
    "acoustic_model": "russian_mfa",
}


def align():
    conda_bat = os.getenv("CONDA_BAT")
    print(conda_bat)
    audio_path = "data/corpus/audio.wav"


    cmd = f'"{conda_bat}" run -n aligner mfa align "{mfa_info["corpus_dir"]}" "{mfa_info["dictionary"]}" "{mfa_info["acoustic_model"]}" "{mfa_info["output_dir"]}" --clean --verbose --output_per_utterance_log_likelihoods false'

    # cmd = f'"{conda_bat}" run -n aligner mfa version'

    subprocess.run(cmd, shell=True, check=True)


#ADD in later somethjing about how fast speaker is vs a normal russian speaker
#ADD in later posibly adding a space if delta x is too big

def extract_phonemes(text_grid_content):
    phonemes = []
    _,_,phoneme_text = text_grid_content.partition("item [2]:")
    intervals = phoneme_text.split("intervals [")[1:]
    for interval in intervals:
        if "text" in interval:
            _,_,text = interval.partition("text = ")
            phoneme = text.strip().strip('"')
            phonemes.append(phoneme)
    return "".join(phonemes)

def adjusted_llh():
    csv = pd.read_csv(mfa_info["output_dir"] + "/alignment_analysis.csv")
    adjusted_llh = csv["overall_log_likelihood"] / csv["end"]
    print("Adjusted Log Likelihood:", adjusted_llh.iloc[0])
    #TRY PER PHONEME BECAUSE A SLOWER SPEAKER WILL HAVE A HIGHER LOG LIKELIHOOD BUT IF YOU DIVIDE BY TIME IT WILL BE LOWER

def analyze_textgrid():

    text_grid_path = mfa_info["output_dir"] + "/audio.TextGrid"
    with open(text_grid_path, "r", encoding="utf8") as f:
        text_grid_content = f.read()
    phonemes = extract_phonemes(text_grid_content)
    print(phonemes)
    adjusted_llh()
        


analyze_textgrid()


