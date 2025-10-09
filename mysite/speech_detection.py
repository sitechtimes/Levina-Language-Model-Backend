import torch
import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

class SpeechDetection:
    def __init__(self):

        MODEL_ID = "jonatasgrosman/wav2vec2-large-xlsr-53-russian"
        self.processor = Wav2Vec2Processor.from_pretrained(MODEL_ID)
        self.model = Wav2Vec2ForCTC.from_pretrained(MODEL_ID)


    def transcribe(self,audio_file_path):
        self.audio_file_path = audio_file_path
        batch = self.speech_file_to_array_fn(self.audio_file_path)
        return self.audio_to_text(batch)


    def speech_file_to_array_fn(self,file_path):
        speech_array, sampling_rate = librosa.load(file_path, sr=16_000)
        return speech_array


    def audio_to_text(self, batch):
        inputs = self.processor(batch, sampling_rate=16_000, return_tensors="pt", padding=True)
        with torch.no_grad():
            logits = self.model(inputs.input_values, attention_mask=inputs.attention_mask).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        predicted_sentence = self.processor.batch_decode(predicted_ids)
        return predicted_sentence[0]
        # predictions = []
        # for i, predicted_sentence in enumerate(predicted_sentences):
        #     predictions.append(predicted_sentence)
        # return predictions