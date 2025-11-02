import whisper

import subprocess


audio_path = "data/corpus/audio.wav"

model = whisper.load_model("turbo")
result = model.transcribe(audio_path, language="ru")
print(result["text"])

with open("data/corpus/audio.lab", "w", encoding="utf8") as f:
    f.write(result["text"].strip())


subprocess.run([
    r"C:\mconda\envs\aligner\Scripts\mfa.exe",
    "align",
    r"data/corpus",
    "russian_mfa",
    'russian_mfa',
    r"data/aligned"
])