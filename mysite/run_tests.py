import os
import subprocess
import pandas as pd
import re
from llm_aligner.hypothesis_test import load_phoneme_stats, calculate_p_values
import dotenv

dotenv.load_dotenv()


def align_audio(audio_path, output_dir):
    conda_bat = os.getenv("LLM_ALIGNER_CONDA_BAT")
    print(f"Using conda batch file at: {conda_bat}")
    cmd = f"{conda_bat} run -n aligner mfa align {audio_path} russian_mfa russian_mfa {output_dir} --clean --verbose"


    subprocess.run(cmd, shell=True, check=True)

def extract_phoneme_durations(textgrid_file):
    """Extract phoneme durations from TextGrid file using text parsing (no praatio dependency)."""
    with open(textgrid_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Isolate the phoneme tier (item [2])
    _, _, phoneme_block = content.partition("item [2]:")
    if not phoneme_block:
        return []
    
    phoneme_durations = []
    intervals = phoneme_block.split("intervals [")[1:]
    
    for interval in intervals:
        # Extract text (phoneme label)
        text_match = re.search(r'text\s*=\s*"([^"]*)"', interval)
        phoneme = text_match.group(1).strip() if text_match else ""
        
        # Extract xmin (start time)
        xmin_match = re.search(r'xmin\s*=\s*([\d.]+)', interval)
        xmin = float(xmin_match.group(1)) if xmin_match else 0.0
        
        # Extract xmax (end time)
        xmax_match = re.search(r'xmax\s*=\s*([\d.]+)', interval)
        xmax = float(xmax_match.group(1)) if xmax_match else 0.0
        
        duration = xmax - xmin
        
        if phoneme:  # Skip empty labels
            phoneme_durations.append((phoneme, duration))
    
    return phoneme_durations


def run_hypothesis_test(phoneme_durations, stats_file):

    population_stats = load_phoneme_stats(stats_file)
    results = calculate_p_values(phoneme_durations, population_stats)
    return results



if __name__ == '__main__':
    # Configuration
    audio_file = 'run_tests_corpus'
    stats_file = 'phoneme_stats_normalized.csv'
    output_dir = './alignments'
    
    os.makedirs(output_dir, exist_ok=True)
 
    try:
        # Step 1: Align file


        # print("Aligning audio file...")
        # align_audio(audio_file, output_dir)

        textgrid_file = output_dir + "/" + audio_file.replace('.wav', '.TextGrid')
        print(textgrid_file)
        # Step 2: Extract durations from textgrid output
        print("Extracting phoneme durations...")
        phoneme_durations = extract_phoneme_durations(textgrid_file)
        
        # Step 3: Import hypothesis test and run it on the extracted durations
        print("Running hypothesis test...")
        results = run_hypothesis_test(phoneme_durations, stats_file)
        
        # Display results
        print("\nPhoneme P-Value Results:")
        for phoneme, p_value in results.items():
            if pd.isna(p_value):
                print(f"  - {phoneme}: Not available")
            else:
                print(f"  - {phoneme}: {p_value:.6f}")
                
    except Exception as e:
        print(f"Error: {e}")