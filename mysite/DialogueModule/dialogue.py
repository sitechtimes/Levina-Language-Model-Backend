import torch
from dialogue_STT import STT
from dialogue_TTS import TTS

print('Loading dialogue.py')
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))

if __name__ == "__main__":
    stt = STT()
    tts = TTS()

    while True:
        stt.generate_sst()
        tts.generate_tts()