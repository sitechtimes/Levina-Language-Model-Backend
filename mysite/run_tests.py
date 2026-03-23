import os
import subprocess
from praatio import tg
import pandas as pd
from llm_aligner.hypothesis_test import load_phoneme_stats, calculate_p_values

def align_audio(audio_path, output_dir):
    conda_bat = os.getenv("CONDA_BAT")

    cmd = f"{conda_bat} run -n aligner mfa align {audio_path} russian_mfa russian_mfa {output_dir} --clean --verbose"


    subprocess.run(cmd, shell=True, check=True)

def extract_phoneme_durations(textgrid_file):

    tg_obj = tg.TextGrid()
    tg_obj.read(textgrid_file)
    
    phoneme_durations = []
    for entry in tg_obj.tiers[1].entries:
        phoneme = entry.label.strip()
        duration = entry.end - entry.start
        if phoneme:  # Skip empty labels
            phoneme_durations.append((phoneme, duration))
    
    return phoneme_durations


def run_hypothesis_test(phoneme_durations, stats_file):

    population_stats = load_phoneme_stats(stats_file)
    results = calculate_p_values(phoneme_durations, population_stats)
    return results



if __name__ == '__main__':
    # Configuration
    audio_file = 'audio3.wav'
    stats_file = 'phoneme_stats_normalized.csv'
    output_dir = './alignments'
    
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Step 1: Align file
        print("Aligning audio file...")
        textgrid_file = align_audio(audio_file, output_dir)
        
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