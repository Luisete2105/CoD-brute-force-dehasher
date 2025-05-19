import re
import os
from cod_hashes import (
    base_fnv1a_63, base_fnv1a_64, base_fnv1a_32,
    iw_resources, mwii_iii_scr, black_ops_3_scr, hash_bo4cw_scr,
    iw_dvars, black_ops_6_scr, black_ops_6_omnvars, black_ops_6_sp_scr
)

def detect_game(folder):
    bo3_names = ['t7', 'bo3', 'blackops3', 'blackops-3', 'black-ops-3']
    bo4_names = ['t8', 'bo4', 'blackops4', 'blackops-4', 'black-ops-4']
    bocw_names = ['t9', 'cw', 'coldwar', 'bocw', 'blackopscoldwar', 'cold-war', 'black-ops-cold-war']
    mwiii_names = ['jup', 'mwiii', 'modernwarfareiii', 'modern-warfare-iii']
    bo6_names = ['t10', 'bo6', 'blackops6', 'black-ops-6']

    found_words = set(re.findall(r'\w+', folder.lower()))
    try:
        for root_dir, _, files in os.walk(folder):
            found_words.update(re.findall(r'\w+', root_dir.lower()))
            for file in files:
                found_words.update(re.findall(r'\w+', file.lower()))
            break
    except Exception as e:
        return "Unknown"

    def matches(words, patterns): return any(name in words for name in patterns)

    if matches(found_words, bo3_names): return "Black Ops 3"
    if matches(found_words, bo4_names): return "Black Ops 4"
    if matches(found_words, bocw_names): return "Black Ops Cold War"
    if matches(found_words, mwiii_names): return "Modern Warfare III"
    if matches(found_words, bo6_names): return "Black Ops 6"
    return "Unknown"

def get_default_hash_function(game):
    if game == "Black Ops 3":
        return black_ops_3_scr
    if game == "Black Ops 4":
        return hash_bo4cw_scr
    if game == "Black Ops Cold War":
        return hash_bo4cw_scr
    if game == "Modern Warfare III":
        return mwii_iii_scr
    if game == "Black Ops 6":
        return black_ops_6_scr
    return None

def get_game_specific_header(game):
    if game == "Black Ops 3":
        return "Word\tBlack Ops 3 Scr\n"
    if game == "Black Ops 4":
        return "Word\tBase FNV1A 63\tBlack Ops 4 Scr\n"
    if game == "Black Ops Cold War":
        return "Word\tBase FNV1A 63\tBlack Ops Cold War Scr\n"
    if game == "Modern Warfare III":
        return "Word\tBase FNV1A 63\tIW Resources\tMWIII Scr\tIW Dvars\n"
    if game == "Black Ops 6":
        return "Word\tBase FNV1A 64\tIW Resources\tBlack Ops 6 Scr\tBlack Ops 6 SP Scr\tBlack Ops 6 Omnvars\tIW Dvars\n"
    if game == "Unknown":
        return "Word\n"
    return "Word\n"

def get_game_specific_hashes(word, game):
    word = word.strip()
    if not word:
        return ""
    h = lambda fn: f"{fn(word):016x}" if fn.__name__.endswith("_63") or fn.__name__.endswith("_64") else f"{fn(word):08x}"

    if game == "Black Ops 3":
        return f"{word}\t{h(black_ops_3_scr)}\n"
    if game == "Black Ops 4":
        return f"{word}\t{h(base_fnv1a_63)}\t{h(hash_bo4cw_scr)}\n"
    if game == "Black Ops Cold War":
        return f"{word}\t{h(base_fnv1a_63)}\t{h(hash_bo4cw_scr)}\n"
    if game == "Modern Warfare III":
        return f"{word}\t{h(base_fnv1a_63)}\t{h(iw_resources)}\t{h(mwii_iii_scr)}\t{h(iw_dvars)}\n"
    if game == "Black Ops 6":
        return f"{word}\t{h(base_fnv1a_64)}\t{h(iw_resources)}\t{h(black_ops_6_scr)}\t{h(black_ops_6_sp_scr)}\t{h(black_ops_6_omnvars)}\t{h(iw_dvars)}\n"
    if game == "Unknown":
        return f"{word}\n"
    return ""

def get_all_hashes(word):
    word = word.strip()
    if not word:
        return []

    # Define all hash functions in the specified order with standardized labels (12 characters each)
    hash_functions = [
        ("BO3 SCR     ", black_ops_3_scr),
        ("BO4CW SCR   ", hash_bo4cw_scr),
        ("FNV1A 63    ", base_fnv1a_63),
        ("MWIII SCR   ", mwii_iii_scr),
        ("IW Resources", iw_resources),
        ("IW Tag FNV32 ", base_fnv1a_32),
        ("IW Dvars    ", iw_dvars),
        ("FNV1A 64    ", base_fnv1a_64),
        ("BO6 SCR     ", black_ops_6_scr),
        ("BO6 SP SCR  ", black_ops_6_sp_scr),
        ("BO6 Omnvars ", black_ops_6_omnvars),
    ]

    # Compute hashes using all functions
    results = []
    for label, func in hash_functions:
        if func.__name__.endswith("_63") or func.__name__.endswith("_64"):
            hash_value = f"{func(word):016x}"  # 16 characters for 63/64-bit hashes
        else:
            hash_value = f"{func(word):08x}"   # 8 characters for 32-bit hashes
        results.append((label, hash_value))

    return results