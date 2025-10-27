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
        self.model = None
        self.tokenizer = AutoTokenizer.from_pretrained(env.model_name, use_fast=True)
        self.device = None
        self.max_length = 512

    def fetch_prompt(self):
        with open("dynamic-prompt.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
        return prompt

    def generate_response(self):
        torch.cuda.empty_cache()

        prompt = self.fetch_prompt()

        self.model = AutoModelForCausalLM.from_pretrained(
            env.quantized_model_directory,
            device_map={"":"cuda:0"},
            load_in_4bit=True,
            trust_remote_code=True
        )

        print('test 1')

        if torch.cuda.is_available():
            self.device = torch.device('cuda:0')
        else:
            self.device = torch.device('cpu')

        # self.model.to(self.device)

        input_tokens = self.tokenizer(
                prompt,
                max_length=self.max_length,
                truncation=True,
                add_special_tokens=False,
                return_tensors="pt",
        ).to(self.device)
        
        print('test 2')

        output_tokens = self.model.generate(
            input_ids=input_tokens['input_ids'],
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1,
        )

        print('test 3')
        
        response = self.tokenizer.decode(output_tokens[0], skip_special_tokens=True)

        return torch.cuda.is_available(), env.quantized_model_directory, output_tokens, response
    
if __name__ == "__main__":
    model_instance = model_gen()
    response = model_instance.generate_response()
    dynamic_prompt = model_instance.fetch_prompt()
    print(response)