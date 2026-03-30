import os
from dotenv import load_dotenv
import requests

load_dotenv()
api_key = os.getenv("API_KEY")

dataset_id = "cmflnuzw70j7lpa4qgjzcbuyu"
url = f"https://datacollective.mozillafoundation.org/api/datasets/{dataset_id}"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json"
}

response = requests.get(url, headers=headers)
dataset = response.json()

print("Dataset:", dataset["datasetUrl"])

""" file_info = dataset["files"][0]
download_url = file_info["downloadUrl"]

# Download file
file_response = requests.get(download_url, headers=headers)

with open(file_info["filename"], "wb") as f:
    f.write(file_response.content)

print("Downloaded:", file_info["filename"]) """