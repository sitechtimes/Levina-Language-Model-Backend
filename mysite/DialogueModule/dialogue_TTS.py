import torch
import numpy as np
import soundfile as sf

language='ru'
model_id='v5_ru'
sample_rate=48000
speaker='xenia'
device=torch.device('cpu')

model, example_text = torch.hub.load(
    repo_or_dir='snakers4/silero-models',
    model='silero_tts',
    language=language,
    speaker=model_id
)

model.to(device)

audio = model.apply_tts(
    text='Привет, как дела?',
    speaker=speaker,
    sample_rate=sample_rate
)

audio = audio.cpu().numpy().astype(np.float32)

sf.write(
    "output.wav",
    audio,
    sample_rate,
    subtype="PCM_16"
)