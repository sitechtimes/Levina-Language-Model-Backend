# import whisper

# model = whisper.load_model("turbo")
# result = model.transcribe("audio3.wav", language="ru")
# print(result["text"])


from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import librosa

processor = Wav2Vec2Processor.from_pretrained("kosuke-kitahara/wav2vec2-large-xlsr-53-phoneme")
model = Wav2Vec2ForCTC.from_pretrained("kosuke-kitahara/wav2vec2-large-xlsr-53-phoneme")
#NEEED TO CHANGE MODEL !!!!!!!!!!!!! FIND A GOOD ONE

audio_file = "audio3.wav"

#prepare audio

audio_input, sample_rate = librosa.load(audio_file, sr=None, mono=False)

#sampling rate needs to be 16000 for the model cuz it was trained that way
if sample_rate != 16000:
    audio_input = librosa.resample(audio_input, orig_sr=sample_rate, target_sr=16000)

print(audio_input)

print(sample_rate)
input_values = processor(audio_input, sampling_rate=16000, return_tensors="pt").input_values

#retrieve logits

with torch.no_grad():
    logits = model(input_values).logits

predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.batch_decode(predicted_ids)[0]
print(transcription)