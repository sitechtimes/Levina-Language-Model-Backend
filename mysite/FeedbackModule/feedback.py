import torch
import os
from dataclasses import dataclass
from dotenv import load_dotenv
import json
from Config.config import config
from transformers import LlamaTokenizer, AutoTokenizer, AutoModelForCausalLM, GenerationConfig, TextIteratorStreamer, BitsAndBytesConfig
from threading import Thread

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
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        # load model once; adjust device_map/quantization as needed for your setup
        try:
            """ generative_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
            ) """
            print("Loading quantized model...")
            self.model = AutoModelForCausalLM.from_pretrained(
                env.quantized_model_directory,
                device_map={"":"cuda:0"},
                low_cpu_mem_usage=True,
                trust_remote_code=True,
            )
            self.model.eval()

            self.messages = [
                {"role": "system", "content": self.fetch_prompt()},
                {"role": "user", "content": self.fetch_essay()}
            ]

        except Exception as e:
            print("Model load failed:", e)
            self.model = None

    def fetch_prompt(self):
        feedback_prompt_path = os.path.join(self.base_dir, "dynamic-prompt.txt")
        dialogue_prompt_path = os.path.join(self.base_dir, "dialogue-prompt.txt")
        prompt_path = os.path.join(self.base_dir, dialogue_prompt_path)
        with open(prompt_path, "r", encoding="utf-8") as f:
            base_prompt =  f.read().strip()
            return base_prompt.replace("{Specific Dialogue Scenario}", "Say HOLA after every other word")
        
    def fetch_essay(self):
        essay_path = os.path.join(self.base_dir, "essay-text.txt")
        with open(essay_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def generate_response(self, user_message: str, essay_analysis: bool):
        torch.cuda.empty_cache()

        if self.model is None:
            raise RuntimeError("Model not loaded")
            
        # print(user_message)
            
        self.messages.append({"role": "user", "content": user_message})
        if not essay_analysis:
            self.messages.pop(1)

        print('test 1')

        system_prompt = self.fetch_prompt()
        if not system_prompt:
            raise ValueError("Prompt is empty")

        # print(self.messages)

        prompt = self.tokenizer.apply_chat_template(
            self.messages,
            tokenize=False,
            add_generation_prompt=True
        )

        tokens = self.tokenizer(
            prompt,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt",
        )

        input_tokens = tokens.to(self.device)

        # simple_gen = self.model.generate(**self.tokenizer("Hello", return_tensors="pt").to(self.device), max_new_tokens=256)
        # print('1 - Simple Generative Output: ', simple_gen)

        print('test 2')

        # pad_id = self.tokenizer.pad_token_id or self.tokenizer.eos_token_id
        # eos_id = self.tokenizer.eos_token_id

        streamer = TextIteratorStreamer(
            self.tokenizer, skip_prompt=True, skip_special_tokens=True
        )

        # IMPORTANT: set a generation limit
        generation_kwargs = dict(
            input_ids=input_tokens["input_ids"],
            attention_mask=tokens["attention_mask"],
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
            length_penalty=1.0,
            streamer=streamer,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.pad_token_id or self.tokenizer.eos_token_id
        )

        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()

        return streamer, thread
    
    def save_ai_response(self, bot_reply: str):
        self.messages.append({"role": "assistant", "content": bot_reply})
