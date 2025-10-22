# import whisper

# model = whisper.load_model("turbo")
# result = model.transcribe("audio3.wav", language="ru")
# print(result["text"])


from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import soundfile as sf


processor = Wav2Vec2Processor.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-russian")
model = Wav2Vec2ForCTC.from_pretrained("jonatasgrosman/wav2vec2-large-xlsr-53-russian")
#NEEED TO CHANGE MODEL !!!!!!!!!!!!! FIND A GOOD ONE

audio_file = "audio3.wav"

#prepare audio

audio_input, sample_rate = sf.read(audio_file)
input_values = processor(audio_input, sampling_rate=sample_rate, return_tensors="pt").input_values

#retrieve logits

with torch.no_grad():
    logits = model(input_values).logits

predicted_ids = torch.argmax(logits, dim=-1)
transcription = processor.batch_decode(predicted_ids)[0]
print(transcription)