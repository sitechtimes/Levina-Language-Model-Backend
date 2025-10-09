import torch
from dataclasses import dataclass
from dotenv import load_dotenv
import json
from Config.config import config

@dataclass
class env:
    model_name = config["generate_model"]["model"]
    model_basename = config["generate_model"]["basename"]
    load_quantized_model = config["generate_model"]["load_quantized_model"]
    quantized_model_directory = config["generate_model"]["quantized_model"]
    bits = config["generate_model"]["bits"]
    group_size = config["generate_model"]["group_size"]

def generate_response():
    return torch.cuda.is_available(), env.quantized_model_directory

response = generate_response()
print(response)