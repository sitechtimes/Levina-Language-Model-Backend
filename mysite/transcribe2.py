import whisper

import subprocess
import dotenv
import os
import shutil

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


    cmd = f'"{conda_bat}" run -n aligner mfa align "{mfa_info["corpus_dir"]}" "{mfa_info["dictionary"]}" "{mfa_info["acoustic_model"]}" "{mfa_info["output_dir"]}" --clean --verbose'

    # cmd = f'"{conda_bat}" run -n aligner mfa version'

    subprocess.run(cmd, shell=True, check=True)


#ADD in later somethjing about how fast speaker is vs a normal russian speaker
#ADD in later posibly adding a space if delta x is too big
text_grid_path = mfa_info["output_dir"] + "/audio.TextGrid"

with open(text_grid_path, "r", encoding="utf8") as f:
    phonemes = []
    text_grid_content = f.read()
    _,_,phoneme_text = text_grid_content.partition("item [2]:")
    intervals = phoneme_text.split("intervals [")[1:]
    print(intervals)
    for interval in intervals:
        if "text" in interval:
            _,_,text = interval.partition("text = ")
            phoneme = text.strip().strip('"')
            phonemes.append(phoneme)
    print("".join(phonemes))


