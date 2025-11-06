import torch
from dataclasses import dataclass
from dotenv import load_dotenv
import json
from Config.config import config
from transformers import LlamaTokenizer, AutoTokenizer, AutoModelForCausalLM, GenerationConfig, TextIteratorStreamer, GPTQConfig

print('Loading feedback.py')
print(torch.__version__)
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))

@dataclass
class env:
    model_name = config["generate_model"]["model"]
    model_basename = config["generate_model"]["basename"]
    load_quantized_model = config["generate_model"]["load_quantized_model"]
    quantized_model_directory = config["generate_model"]["quantized_model"]
    bits = config["generate_model"]["bits"]
    group_size = config["generate_model"]["group_size"]

class model_gen:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(env.model_name, use_fast=True)
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.max_length = 16000
        # load model once; adjust device_map/quantization as needed for your setup
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                env.quantized_model_directory,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
            )
            # ensure the model is on the right device if device_map wasn't used
            try:
                self.model.to(self.device)
            except Exception:
                pass
        except Exception as e:
            print("Model load failed:", e)
            self.model = None

    def fetch_prompt(self):
        with open("dynamic-prompt.txt", "r", encoding="utf-8") as f:
            return f.read().strip()

    def generate_response(self):
        torch.cuda.empty_cache()

        if self.model is None:
            raise RuntimeError("Model not loaded")

        print('test 1')

        prompt = self.fetch_prompt()
        if not prompt:
            raise ValueError("Prompt is empty")

        tokens = self.tokenizer(
            prompt,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )
        # move each tensor to device
        input_tokens = {k: v.to(self.device) for k, v in tokens.items()}

        print('test 2')

        # IMPORTANT: set a generation limit
        print(next(self.model.parameters()).device)
        output_ids = self.model.generate(
            input_ids=input_tokens.get("input_ids"),
            attention_mask=input_tokens.get("attention_mask"),
            max_new_tokens=1024,      # limit generated tokens
            do_sample=False,          # deterministic; set True to sample
            num_beams=1,
            temperature=0.7,
            top_k=50,
            top_p=0.9,
            early_stopping=True,
        )

        print('test 3')

        response = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return response
    
if __name__ == "__main__":
    model_instance = model_gen()
    response = model_instance.generate_response()
    dynamic_prompt = model_instance.fetch_prompt()
    print(response)