import torch
import numpy as np
import soundfile as sf

language = 'ru'
sample_rate = 48000
device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(device)

model, example_text = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language=language,
    speaker='ru_kseniya'
)

model = model.to(device)

audio = model.apply_tts(
    texts=['Меня зовут Лева Королев. Я из готов. И я уже готов открыть все ваши замки любой сложности!'],
    model=model,
    sample_rate=sample_rate,
    device=device
)

audio = torch.cat(audio, dim=0)
audio = audio.cpu().numpy().astype(np.float32)

sf.write(
    "output.wav",
    audio,
    sample_rate,
    subtype="PCM_16"
)