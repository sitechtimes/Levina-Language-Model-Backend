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

def extract_phoneme_durations(textgrid_file,total_mean):
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
    if total_mean is not None and phoneme_durations:
        clip_mean = sum(d for _, d in phoneme_durations) / len(phoneme_durations)
        if clip_mean != 0:
            normalization_factor = total_mean / clip_mean
            phoneme_durations = [(p, d * normalization_factor) for p, d in phoneme_durations]

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
    alpha = 0.05  # Significance level for hypothesis testing
    
    os.makedirs(output_dir, exist_ok=True)
 
    try:
        # Step 1: Align file


        # print("Aligning audio file...")
        # align_audio(audio_file, output_dir)

        textgrid_folder = output_dir + "/" + audio_file.replace('.wav', '.TextGrid')
        for root, _, files in os.walk(output_dir):
            candidates = sorted(
                os.path.join(root, f)
                for f in files
                if f.lower().endswith(".textgrid")
            )
            if candidates:
                textgrid_file = candidates[0]
                break
            else:
                raise FileNotFoundError(f"No .TextGrid file found under: {output_dir}")
        print(textgrid_file)
        # Step 2: Extract durations from textgrid output
        print("Extracting phoneme durations...")
        total_clip_mean =  0.10474026101545329
        phoneme_durations = extract_phoneme_durations(textgrid_file,total_clip_mean)

        
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
                
        # Step 4: Flag phonemes that fail the hypothesis test at the given alpha
        flagged = []
        for phoneme, p_value in results.items():
            if pd.isna(p_value):
                continue
            if p_value < alpha:
                flagged.append((phoneme, p_value))

        if flagged:
            print(f"\nFlagged phonemes (p < {alpha}):")
            for phoneme, p_value in sorted(flagged, key=lambda x: x[1]):
                print(f"  - {phoneme}: {p_value:.6f}")
        else:
            print(f"\nNo phonemes flagged (all available p-values >= {alpha}).")

    except Exception as e:
        print(f"Error: {e}")