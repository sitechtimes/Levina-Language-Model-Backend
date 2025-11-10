import whisper

import subprocess
import dotenv
import os
import shutil

dotenv.load_dotenv()

conda_bat = os.getenv("CONDA_BAT")
print(conda_bat)
audio_path = "data/corpus/audio.wav"

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
cmd = f'"{conda_bat}" run -n aligner mfa align "{mfa_info["corpus_dir"]}" "{mfa_info["dictionary"]}" "{mfa_info["acoustic_model"]}" "{mfa_info["output_dir"]}" --clean --verbose'

# cmd = f'"{conda_bat}" run -n aligner mfa version'

subprocess.run(cmd, shell=True, check=True)

