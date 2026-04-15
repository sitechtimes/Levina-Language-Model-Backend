#I am going to use Whelches T test, thank you Mr. Siozios
import pandas as pd
import os
from scipy.stats import norm

def load_phoneme_stats(file_path):
    """
    Loads phoneme population statistics from a CSV file.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        dict: A dictionary mapping each phoneme to its statistics (avg_duration, std_deviation).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Statistics file not found at: {file_path}")
    
    df = pd.read_csv(file_path)

    # Use normalized average/std if available (matches run_tests normalization).
    mean_col = 'normalized_avg_duration' if 'normalized_avg_duration' in df.columns else 'avg_duration'
    std_col = 'normalized_std_deviation' if 'normalized_std_deviation' in df.columns else 'std_deviation'

    stats_dict = {
        row['phoneme']: {
            'mean': row[mean_col],
            'std_dev': row[std_col],
            'count': row['count']
        }
        for index, row in df.iterrows()
    }
    return stats_dict

def calculate_p_values(speaker_duration_pairs,population_stats):
    p_values = {}
    for phoneme, duration in speaker_duration_pairs:
        phoneme = phoneme.strip()
        if phoneme in population_stats:
            stats = population_stats[phoneme]
            pop_mean = stats['mean']
            pop_count = stats['count']
            pop_std_dev = stats['std_dev']

            # Some phonemes have very low counts, which a t test would be better suited for.
            # Some have large counts and will be fine. As n approaches infinity, the t distribution approaches the normal distribution.
        
            if pop_std_dev > 0:
                # Calculate the Z-score for the speaker's duration
                z_score = (duration - pop_mean) / pop_std_dev
                # Calculate the two-tailed p-value from the Z-score
                p_value = 2 * (1 - norm.cdf(abs(z_score)))
                p_values[phoneme] = p_value
            else:
                # Cannot calculate p-value if standard deviation is zero
                p_values[phoneme] = float('nan')
        else:
            # Phoneme not found in population stats
            p_values[phoneme] = float('nan')
            
    return p_values




# Test Usage:
if __name__ == '__main__':
    stats_file_path = 'phoneme_stats_normalized.csv'

    # Load the population statistics
    try:
        population_data = load_phoneme_stats(stats_file_path)

        # Example data for a speaker to be tested
        speaker_data = [
            ('v', 0.08),
            ('ɐ', 0.05),
            ('s̪', 0.25), # This duration is intentionally high to show a low p-value
            ('non_existent_phoneme', 0.1)
        ]

        results = calculate_p_values(speaker_data, population_data)

        # Print the results
        print("Phoneme P-Value Results:")
        for phoneme, p_value in results.items():
            if pd.isna(p_value):
                print(f"  - {phoneme}: Not available (phoneme not in stats or std_dev is zero)")
            else:
                print(f"  - {phoneme}: {p_value:.6f}")

    except FileNotFoundError as e:
        print(e)