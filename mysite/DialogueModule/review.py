import torch
import os
from Config.config import config
from dotenv import load_dotenv

from transformers import LlamaTokenizer, AutoTokenizer, AutoModelForCausalLM, GenerationConfig, TextIteratorStreamer, BitsAndBytesConfig

class env:
    model_name = config["generate_model"]["model"]
    model_basename = config["generate_model"]["basename"]
    load_quantized_model = config["generate_model"]["load_quantized_model"]
    quantized_model_directory = config["generate_model"]["quantized_model"]
    bits = config["generate_model"]["bits"]
    group_size = config["generate_model"]["group_size"]

class Review:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained(env.model_name, use_fast=True)
        self.model = AutoModelForCausalLM.from_pretrained(
                env.quantized_model_directory,
                device_map={"":"cuda:0"},
                low_cpu_mem_usage=True,
                trust_remote_code=True,
            )

    def format_chat(self, chat_history):
        text = ""
        for msg in chat_history:
            text += f"{msg['role']}: {msg['content']}\n"
        return text


    def analyze_response(self, chat_history):
        prompt = self.format_chat(chat_history)
        prompt += "SAY HI!!!"
        inputs = self.tokenizer(prompt, return_tensors="pt").to("cuda:0")

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=200
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)