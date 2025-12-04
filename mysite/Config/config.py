import os
import json

config = None

with open(f"config.json", 'r') as f:
    config = json.load(f)

if (not config):
    Exception("Config file not detected")