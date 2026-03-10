"""Simple grapheme-to-phoneme helpers for Russian text.

This module is intentionally small and import-safe. It provides a tiny,
easily-testable mapping and helper functions for converting words (strings)
into sequences of phonemes and an aligned representation that maps phonemes
to source letter indices.

This is not a production-grade G2P. It's a focused refactor target: later
you can replace the mapping with a richer resource or a lookup loader.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Sequence, Tuple

# Minimal example mapping: Cyrillic letter -> list of phonemes (strings).
# Extend or replace this mapping from data files as needed.

RUS_MFA_G2P = {
    # vowels
    "а": ["a"],
    "о": ["o"],
    "у": ["u"],
    "ы": ["ɨ"],
    "э": ["e"],
    "и": ["i"],
    "е": ["e"],
    "ё": ["ɐ", "o"],
    "ю": ["j", "u"],
    "я": ["j", "a"],

    "б": ["b"],
    "в": ["v"],
    "г": ["ɡ"],
    "д": ["d̪"],
    "ж": ["ʐ"],
    "з": ["z̪"],
    "й": ["j"],
    "к": ["k"],
    "л": ["l"],
    "м": ["m"],
    "н": ["n̪"],
    "п": ["p"],
    "р": ["r"],
    "с": ["s̪"],
    "т": ["t̪"],
    "ф": ["f"],
    "х": ["x"],
    "ц": ["t̪s̪"],
    "ч": ["tɕ"],
    "ш": ["ʂ"],
    "щ": ["ɕ"],
    "ь": [],
    "ъ": [],

    #old letters

    "ѣ": ["e"],
    "ѵ": ["i"],
    "ѳ": ["f"],
    "ѝ": ["i"],
}



def g2p_with_alignment(word: str):
    aligned = []
    unknown_characters = set()
    for i, ch in enumerate(word):
        phones = RUS_MFA_G2P.get(ch.lower())
        if phones is None:
            # raise ValueError(f"Unknown character: {ch}")
            unknown_characters.add(ch)
            continue
        for p in phones:
            aligned.append((p, [i]))
    return aligned,unknown_characters

VOWELS = set(["a","o","u","ɨ","e","i","ɐ"])

def apply_stress(aligned, stress_positions):
    stressed = []
    for p, idxs in aligned:
        if p in VOWELS and any(i in stress_positions for i in idxs):
            stressed.append(p + "ˈ")  # new stressed phoneme
        else:
            stressed.append(p)
    return stressed


def stressed_positions(word: str):
    positions = []
    base_index = -1

    for char in word:
        if not unicodedata.combining(char):
            base_index += 1  
        if char == "\u0301":
            positions.append(base_index)
    return positions