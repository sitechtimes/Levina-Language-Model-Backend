import os
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset

device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

print("Loading Whisper model...")

class STT:
    def __init__(self):
        self.model_id = "openai/whisper-large-v3-turbo"

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id, dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
        )
        self.model.to(device)

        self.processor = AutoProcessor.from_pretrained(self.model_id)

    def generate_sst(self):
        pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            dtype=torch_dtype,
            device=device,
            return_timestamps=True
        )

        print('CWD: ', os.getcwd())

        audio_file1 = "DialogueModule/RURU/RURU001.mp3"
        result = pipe(audio_file1)
        # print('001: ', result["text"])

        audio_file2 = "DialogueModule/RURU/RURU091.mp3"
        result1 = pipe(audio_file2)
        # print('091: ', result1["text"])

        return result1["text"]