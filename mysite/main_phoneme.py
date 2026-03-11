# g2p
from llm_aligner.g2p import (
    RUS_MFA_G2P,
    VOWELS,
    g2p_with_alignment,
    apply_stress,
    stressed_positions,
)

# textgrid parsing
from llm_aligner.textgrid_parser import (
    get_words_from_textgrid,
    extract_phonemes,
    create_mapping_dictionary,
)

# stats + plotting
from llm_aligner.stats import (
    organize_phonemes,
    run_phoneme_stats,
    plot_phoneme_durations,
)

# corpus preparation
from llm_aligner.corpus import (
    convert_to_wav,
    clean,
    formulate_data,
)

# dictionary building
from llm_aligner.dictionary import (
    create_stress_dictionary,
    apply_stress_to_dictionary,
    create_phoneme_word_mappings,
    normalize_dictionary,
)

# MFA alignment
from llm_aligner.aligner import align


if __name__ == "__main__":
    # Step 1
    print("STEP 1: Creating stress dictionary")
    create_stress_dictionary()

    # Step 2
    print("STEP 2: Applying stress to dictionary")
    apply_stress_to_dictionary()

    # Step 3
    print("STEP 3: Normalizing stressed dictionary")
    normalize_dictionary()

    # Step 4
    print("STEP 4: Creating phoneme-word mappings")
    create_phoneme_word_mappings()

    # Step 5
    print("STEP 5: Preparing corpus (formulate_data)")
    formulate_data(100000000000000)

    # Step 6
    print("STEP 6: Running MFA alignment")
    align()

    # Step 7
    print("STEP 7: Computing phoneme statistics")
    mapping = create_mapping_dictionary()
    phoneme_df, separated_data = organize_phonemes(mapping)
    stats = run_phoneme_stats(phoneme_df, separated_data)

    # Step 8
    print("STEP 8: Plotting phoneme durations")
    plot_phoneme_durations(stats)