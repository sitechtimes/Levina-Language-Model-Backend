import whisper

model = whisper.load_model("turbo")
result = model.transcribe("audio3.wav", language="ru")
print(result["text"])