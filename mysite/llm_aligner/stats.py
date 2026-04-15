from pathlib import Path
import os
import pandas as pd
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
import matplotlib.cm as cm


from .loading_bar import loading_bar
from .textgrid_parser import extract_phonemes


def organize_phonemes(mapping):
    full_data = []
    full_data_separated = []
    file_count_path = Path("training_data/aligned_output/")
    files_count = len([p for p in file_count_path.rglob('*') if p.is_file()])
    print(files_count)
    count = 0
    loading_bar(count, files_count)
    for path in os.listdir("training_data/aligned_output/"):
        count += 1
        if count % 10 == 0:
            loading_bar(count, files_count)
        if path.endswith(".TextGrid"):
            with open(os.path.join("training_data/aligned_output/", path), "r", encoding="utf-8") as f:
                content = f.read()
            single_file_data = extract_phonemes(content,mapping)
            full_data = full_data + single_file_data
            full_data_separated.append(single_file_data)
    full_data_no_whitespace = [(p, d) for p, d in full_data if p != '']

    phoneme_df = pd.DataFrame(full_data_no_whitespace, columns=["phoneme", "duration"])
    return phoneme_df,full_data_separated



def run_phoneme_stats(phoneme_df,separated_data):
    phoneme_counts = phoneme_df['phoneme'].value_counts().reset_index()
    phoneme_counts.columns = ['phoneme', 'count']
    phoneme_avg_durations = phoneme_df.groupby('phoneme')['duration'].mean().reset_index()
    phoneme_avg_durations.columns = ['phoneme', 'avg_duration']
    phoneme_std_deviations = phoneme_df.groupby('phoneme')['duration'].std().reset_index()
    phoneme_std_deviations.columns = ['phoneme', 'std_deviation']
    phoneme_std_deviations = phoneme_std_deviations.round(6)
    phoneme_stats = pd.merge(phoneme_counts, phoneme_avg_durations, on='phoneme').merge(phoneme_std_deviations, on='phoneme')

    clip_means = []
    for clip in separated_data:
        clip_df = pd.DataFrame(clip, columns=["phoneme", "duration"])
        # Keep this consistent with downstream usage: ignore empty labels in per-clip mean.
        clip_df = clip_df[clip_df["phoneme"] != ""]
        clip_mean = clip_df["duration"].mean()
        clip_means.append(clip_mean)
    total_mean = sum(clip_means) / len(clip_means)
    print("TOTAL MEAN")
    print(total_mean)
    separated_data_normalized = []

    for i, clip_phonemes in enumerate(separated_data):
        clip_mean = clip_means[i]
        normalization_factor = total_mean / clip_mean
        normalized_clip = []
        
        for phoneme, duration in clip_phonemes:
            if phoneme == "":
                continue
            normalized_duration = duration * normalization_factor
            normalized_clip.append((phoneme, normalized_duration))
        
        separated_data_normalized.append(normalized_clip)

    normalized_phonemes_dict = {}
    for clip in separated_data_normalized:
        for phoneme, duration in clip:
            if phoneme not in normalized_phonemes_dict:
                normalized_phonemes_dict[phoneme] = []
            normalized_phonemes_dict[phoneme].append(duration)
    normalized_averages = {}
    normalized_stddevs = {}
    for phoneme,durations in normalized_phonemes_dict.items():
        normalized_averages[phoneme] = sum(durations) / len(durations)
        mean = normalized_averages[phoneme]
        variance = sum((x - mean) ** 2 for x in durations) / len(durations)
        normalized_stddevs[phoneme] = variance ** 0.5
    print(normalized_averages)
    print(normalized_stddevs)
    normalized_averages = pd.DataFrame(list(normalized_averages.items()), columns=['phoneme', 'normalized_avg_duration'])
    normalized_stddevs = pd.DataFrame(list(normalized_stddevs.items()), columns=['phoneme', 'normalized_std_deviation'])
    # counts = pd.DataFrame(list(counts.items()), columns=['phoneme', 'normalized_count'])
    normalized_phoneme_stats = pd.merge(normalized_averages, normalized_stddevs, on='phoneme')
    normalized_phoneme_stats = normalized_phoneme_stats.merge(phoneme_stats, on='phoneme')
    # Persist the reference used for normalization so inference/tests can stay consistent.
    normalized_phoneme_stats["total_mean"] = total_mean
    normalized_phoneme_stats.to_csv("phoneme_stats_normalized.csv", index=False)
    print(normalized_phoneme_stats)




def plot_phoneme_durations(phoneme_stats):
    plt.figure(figsize=(12, 6))
    mean_counts = phoneme_stats['count'].mean()
    for i, row in phoneme_stats.sort_values('count').iterrows():
        count = row['count']
        color_intensity = count/mean_counts
        plt.bar(row['phoneme'], row['avg_duration'], color=cm.Reds(color_intensity), edgecolor = "black", linewidth = 0.8, yerr=row['std_deviation'], capsize=2)

    # plt.bar(phoneme_stats['phoneme'], phoneme_stats['avg_duration'], yerr=phoneme_stats['std_deviation'], capsize=5)
    plt.xlabel('Phoneme')
    plt.ylabel('Average Duration (s)')
    plt.title('Average Phoneme Durations with Standard Deviation')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

