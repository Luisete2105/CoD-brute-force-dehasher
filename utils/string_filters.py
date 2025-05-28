import re
from typing import List, Set

# Precompiled regex patterns for lowercase
CONSECUTIVE_SYMBOLS = re.compile(r'(__|//|_\/|\/_)')
TRIPLE_CHARS = re.compile(r'(.)\1\1')
FOUR_VOWELS = re.compile(r'[aeiou]{4}')
FOUR_NON_CONSONANTS = re.compile(r'[aeiou0123456789_/]{4}')
THREE_UNCOMMON_NON_CONSONANTS = re.compile(r'[0123456789_/]{3}')

# Cache for vowel checks (lowercase only)
VOWEL_SET = frozenset('aeiou')

# Optimized invalid pairs set (lowercase only)
INVALID_PAIRS = frozenset([
    'bz', 'oo', 'be', 'bn', 'bs', 'bb', 'bg', 'bm', 'bn', 'bv', 'bw', 'bx', 'by',
    'cz', 'cb', 'cc', 'cb', 'cg', 'cg',
    'dz', 'de', 'bd', 'be', 'dg', 'dg',
    'fz', 'be', 'bf', 'fb', 'bf', 'fm',
    'bg', 'gn', 'gs', 'gb', 'gm', 'gv',
    'bh', 'gz', 'hn', 'gb', 'hb',
    'bj', 'jm', 'js', 'jb',
    'km',
    'k', 'kn', 'kp',
    'bp', 'oz', 'pn', 'ps',
    'ng', 'pn',
    'rz', 'rn',
    'rn', 'sn', 'sb',
    'rn', 'ts', 'tb',
    'rt',
    'rt',
    'bv', 'bz', 'vn', 'bs',
    'vb', 'vg', 'vm',
    'bw', 'vb', 'wm',
    'wv', 'wx', 'wy',
    'xz', 'xn', 'xs', 'xb', 'xg', 'xm', 'xv', 'xw', 'xy',
    'yz', 'yn', 'ys', 'yb', 'yg', 'ym', 'yv', 'yw', 'yx'
])

def is_vowel(char: str) -> bool:
    return char in VOWEL_SET

def has_vowel(text: str) -> bool:
    return any(c in VOWEL_SET for c in text)

def bad_letter_combo(text: str) -> bool:
    for i in range(len(text) - 1):
        if text[i].isalpha() and text[i + 1].isalpha():
            if text[i:i+2] in INVALID_PAIRS:
                return True
    return False

def has_uncommon_combo(text: str) -> bool:
    return bad_letter_combo(text)

def has_consecutive_symbols(text: str) -> bool:
    return bool(CONSECUTIVE_SYMBOLS.search(text))

def has_triple_chars(text: str) -> bool:
    return bool(TRIPLE_CHARS.search(text))

def has_four_vowels(text: str) -> bool:
    return bool(FOUR_VOWELS.search(text))

def has_four_non_consonants(text: str) -> bool:
    return bool(FOUR_NON_CONSONANTS.search(text))

def has_three_uncommon_non_consonants(text: str) -> bool:
    return bool(THREE_UNCOMMON_NON_CONSONANTS.search(text))

def filter_strings(strings: List[str], require_vowel: bool = False, no_uncommon: bool = False,
                   no_consecutive_symbols: bool = False, no_triple: bool = False,
                   no_four_vowels: bool = False, no_four_non_consonants: bool = False,
                   no_three_uncommon_non_consonants: bool = False) -> List[str]:
    """Batch filter lowercase strings based on multiple criteria."""
    valid = []
    for s in strings:
        if no_uncommon and has_uncommon_combo(s):
            continue
        if require_vowel and not has_vowel(s):
            continue
        if no_consecutive_symbols and has_consecutive_symbols(s):
            continue
        if no_triple and has_triple_chars(s):
            continue
        if no_four_vowels and has_four_vowels(s):
            continue
        if no_four_non_consonants and has_four_non_consonants(s):
            continue
        if no_three_uncommon_non_consonants and has_three_uncommon_non_consonants(s):
            continue
        valid.append(s)
    return valid