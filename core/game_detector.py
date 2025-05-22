import re
import os
from core.cod_hashes import (
    base_fnv1a_63, base_fnv1a_64, base_fnv1a_32,
    iw_resources, mwii_iii_scr, black_ops_3_scr, hash_bo4cw_scr,
    iw_dvars, black_ops_6_scr, black_ops_6_omnvars, black_ops_6_sp_scr
)

def log_to_file(message, log_file="debug.log"):
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")

def detect_game(folder):
    # Game identifiers
    game_identifiers = {
        'Black Ops 3': ['t7', 'bo3', 'blackops3', 'blackops-3', 'black-ops-3'],
        'Black Ops 4': ['t8', 'bo4', 'blackops4', 'blackops-4', 'black-ops-4'],
        'Black Ops Cold War': ['t9', 'cw', 'coldwar', 'bocw', 'blackopscoldwar', 'cold-war', 'black-ops-cold-war'],
        'Modern Warfare III': ['jup', 'mwiii', 'modernwarfareiii', 'modern-warfare-iii'],
        'Black Ops 6': ['t10', 'bo6', 'blackops6', 'black-ops-6']
    }

    # Check the last folder name first
    last_folder = os.path.basename(os.path.normpath(folder)).lower()
    log_to_file(f"Checking last folder name: {last_folder} in {folder}")
    for game, identifiers in game_identifiers.items():
        if last_folder in identifiers:
            log_to_file(f"Detected game '{game}' based on last folder: {last_folder}")
            return game

    # Fallback to word-based detection
    found_words = set(re.findall(r'\w+', folder.lower()))
    try:
        for root_dir, _, files in os.walk(folder):
            found_words.update(re.findall(r'\w+', root_dir.lower()))
            for file in files:
                found_words.update(re.findall(r'\w+', file.lower()))
            break
    except Exception as e:
        log_to_file(f"Error walking folder {folder}: {str(e)}")
        return "Unknown"

    log_to_file(f"Found words in folder {folder}: {found_words}")
    def matches(words, patterns): return any(name in words for name in patterns)

    for game, identifiers in game_identifiers.items():
        if matches(found_words, identifiers):
            log_to_file(f"Detected game '{game}' based on word match")
            return game

    log_to_file(f"No game detected for folder {folder}")
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
        return "Word\tBase FNV1A 64\tIW Resources\tBlack Ops 6 Scr\tBlack Ops 6 SP Scr\tIW Dvars\n"
    if game == "Unknown":
        return "Word\n"
    return "Word\n"

def get_game_specific_hashes(word, game, is_sp_folder=False):
    word = word.strip()
    if not word:
        return ""
    h = lambda fn: hex(fn(word))[2:] if fn.__name__.endswith("_63") or fn.__name__.endswith("_64") else hex(fn(word))[2:].zfill(8)

    if game == "Black Ops 3":
        return f"{word}\t{h(black_ops_3_scr)}\n"
    if game == "Black Ops 4":
        return f"{word}\t{h(base_fnv1a_63)}\t{h(hash_bo4cw_scr)}\n"
    if game == "Black Ops Cold War":
        return f"{word}\t{h(base_fnv1a_63)}\t{h(hash_bo4cw_scr)}\n"
    if game == "Modern Warfare III":
        return f"{word}\t{h(base_fnv1a_63)}\t{h(iw_resources)}\t{h(mwii_iii_scr)}\t{h(iw_dvars)}\n"
    if game == "Black Ops 6":
        scr_hash = black_ops_6_sp_scr if is_sp_folder else black_ops_6_scr
        return f"{word}\t{h(base_fnv1a_64)}\t{h(iw_resources)}\t{h(scr_hash)}\t{h(black_ops_6_sp_scr)}\t{h(iw_dvars)}\n"
    if game == "Unknown":
        return f"{word}\n"
    return ""

def get_all_hashes(word):
    word = word.strip()
    if not word:
        return []

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

    results = []
    for label, func in hash_functions:
        hash_value = hex(func(word))[2:] if func.__name__.endswith("_63") or func.__name__.endswith("_64") else hex(func(word))[2:].zfill(8)
        results.append((label, hash_value.lstrip('0') or '0'))

    return results