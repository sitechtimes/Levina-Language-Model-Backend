import whisper

import subprocess
import dotenv
import os

dotenv.load_dotenv()

conda_base_path = os.getenv("CONDA_BASE_PATH")

audio_path = "data/corpus/audio.wav"

model = whisper.load_model("turbo")
result = model.transcribe(audio_path, language="ru")
print(result["text"])

with open("data/corpus/audio.lab", "w", encoding="utf8") as f:
    f.write(result["text"].strip())

path_to_mfa_env = conda_base_path + r"\envs\aligner\Scripts\activate.bat"
print(path_to_mfa_env)
subprocess.run([
    path_to_mfa_env,
    "align",
    r"data/corpus",
    "russian_mfa",
    'russian_mfa',
    r"data/aligned"
])