import os
import json

cwd = os.getcwd()

config = None

with open(f"{cwd}/config.json", 'r') as f:
    config = json.load(f)

if (not config):
    Exception("NO CONFIG FILE")