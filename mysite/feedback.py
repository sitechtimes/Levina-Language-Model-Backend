import torch
from dataclasses import dataclass
from dotenv import load_dotenv
import json
from Config.config import config
from transformers import LlamaTokenizer, AutoTokenizer, AutoModelForCausalLM, GenerationConfig, TextIteratorStreamer, GPTQConfig, BitsAndBytesConfig
# from gptqmodel import GPTQModel

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
            gptq_config = GPTQConfig(
                bits=env.bits,
                dataset="c4",
                group_size=env.group_size,
                model_basename=env.model_basename,
                tokenizer=self.tokenizer
            )
            print("Loading quantized model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                env.quantized_model_directory,
                quantization_config=gptq_config,
                device_map="auto" if torch.cuda.is_available() else None,
                low_cpu_mem_usage=True,
                trust_remote_code=True,
            )
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

        input_tokens = tokens.to(self.device)

        simple_gen = self.model.generate(**self.tokenizer("Hello", return_tensors="pt").to(self.device), max_new_tokens=256)
        print('1 - Simple Generative Output: ', simple_gen)

        print('test 2')

        # IMPORTANT: set a generation limit
        output_ids = self.model.generate(
            input_ids=input_tokens.get("input_ids"),
            attention_mask=input_tokens.get("attention_mask"),
            max_new_tokens=256,      # limit generated tokens
            do_sample=False,          # deterministic; set True to sample
            num_beams=1,
            early_stopping=True,
        )

        simple_gen = self.model.generate(**self.tokenizer("Hello", return_tensors="pt").to(self.device), max_new_tokens=256)
        print('2 - Simple Generative Output: ', simple_gen)

        print('test 3')

        response = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return response
    
if __name__ == "__main__":
    model_instance = model_gen()
    response = model_instance.generate_response()
    dynamic_prompt = model_instance.fetch_prompt()
    print(response)