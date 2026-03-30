import torch
from .dialogue_TTS import TTS

class Listening:
    def __init__(self):
        self.device=torch.device('cuda')

    def listening(self):
        tts = TTS()

        text = "Как тебя зовут?"
        tts.generate_tts("text")

        print("Listen carefully...")

        audio = tts.generate_tts(text)

        #need to add play_audio somewhere in backend
        self.play_audio(audio, tts.sample_rate)

        answer = input("What did you hear?")

        if text.lower() in answer.lower():
            print("Correct!")
        else:
            print(f"Incorrect. Correct answer: {text}")