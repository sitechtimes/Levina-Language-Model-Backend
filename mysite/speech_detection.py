import torch
import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-russian"


processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)

# make audio files into arrays
def speech_file_to_array_fn(file_path):
    speech_array, sampling_rate = librosa.load(file_path, sr=16_000)
    return speech_array

batch = speech_file_to_array_fn("audio.wav")
inputs = processor(batch, sampling_rate=16_000, return_tensors="pt", padding=True)
with torch.no_grad():
    logits = model(inputs.input_values, attention_mask=inputs.attention_mask).logits

predicted_ids = torch.argmax(logits, dim=-1)
predicted_sentences = processor.batch_decode(predicted_ids)

for i, predicted_sentence in enumerate(predicted_sentences):
    print("Prediction:", predicted_sentence)
