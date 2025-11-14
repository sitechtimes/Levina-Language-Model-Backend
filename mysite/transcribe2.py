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

def adjusted_llh(csv,phonemes):
    llh_second = csv["overall_log_likelihood"] / csv["end"]
    llh_second = llh_second.iloc[0]
    print("Log Likelihood Per Second:", llh_second)
    llh_phoneme = csv["overall_log_likelihood"] / len([p for p in phonemes if p != "" or p != " " or p != "sil" or p != "sp" or p != "pau"])
    llh_phoneme = llh_phoneme.iloc[0]
    print("Log Likelihood Per Phoneme:", llh_phoneme)
    return llh_second, llh_phoneme
# def calculate_speaking_rate(phonemes, total_time):
#     num_phonemes = len([p for p in phonemes if p != ""])
#     speaking_rate = num_phonemes / total_time
#     print("Speaking Rate (phonemes per second):", speaking_rate)
#     return speaking_rate

def analyze_audio_quality(csv):
    snr = csv["snr"].iloc[0]
    snr_scores = {3:"Super Noisy/ Unusable",6:"Noisy But Usable",10:"Usable/ Slight Noise",15:"Excellent/ No Noise"}
    for i in snr_scores:
        if snr < i:
            return snr_scores[i],snr

def phoneme_timing(csv):
    pdd = csv["phone_duration_deviation"].iloc[0]
    duration_scores = {.7:"Great/Native",1:"Good/Acceptable",1.5:"Noticably Off",4:"Very Bad/Non-Native"}
    for i in duration_scores:
        if pdd < i:
            return duration_scores[i],pdd
def analyze_textgrid():
    text_grid_path = mfa_info["output_dir"] + "/audio.TextGrid"
    with open(text_grid_path, "r", encoding="utf8") as f:
        text_grid_content = f.read()
    phonemes = extract_phonemes(text_grid_content)
    print(phonemes)
    csv = pd.read_csv(mfa_info["output_dir"] + "/alignment_analysis.csv")
    llh_second,llh_phoneme = adjusted_llh(csv,phonemes)
    phoneme_rating, phoneme_timing_score = phoneme_timing(csv)
    print("Phoneme Timing Score:", phoneme_timing_score, "-", phoneme_rating)
    audio_quality = analyze_audio_quality(csv)
    print("Audio Quality:", audio_quality[1], "dB -", audio_quality[0])





analyze_textgrid()


