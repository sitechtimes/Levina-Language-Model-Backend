import subprocess
import os

def align():
    conda_bat = os.getenv("CONDA_BAT")

    audio_path = "data/corpus/audio.wav"

    cmd = f"{conda_bat} run -n aligner mfa align training_data/corpus russian_mfa russian_mfa training_data/aligned_output --clean --verbose"


    subprocess.run(cmd, shell=True, check=True)