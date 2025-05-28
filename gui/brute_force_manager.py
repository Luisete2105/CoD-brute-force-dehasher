import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import itertools
import os
import csv
import logging
from core.cod_hashes import (
    black_ops_3_scr, hash_bo4cw_scr, base_fnv1a_63, mwii_iii_scr, iw_resources,
    base_fnv1a_32, iw_dvars, base_fnv1a_64, black_ops_6_scr, black_ops_6_sp_scr,
    black_ops_6_omnvars
)
from utils.string_filters import (
    is_vowel, bad_letter_combo, has_uncommon_combo, has_vowel,
    has_consecutive_symbols, has_triple_chars, has_four_vowels,
    has_four_non_consonants, has_three_uncommon_non_consonants
)
from gui.character_selector import open_character_selection
from gui.utils import Tooltip
from utils.string_filters import filter_strings

# Configure logging with explicit file handler
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
if not logger.handlers:  # Avoid duplicate handlers
    file_handler = logging.FileHandler('debug.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger.addHandler(file_handler)
logging.debug("Debug logging initialized")

# Define algo_to_csvs at module level for global access
algo_to_csvs = {
    "BO3 SCR": {"games": ["Black Ops 3"], "csvs": ["bo3_var.csv", "bo3_function.csv", "bo3_namespace.csv", "bo3_class.csv", "bo3_hash.csv"]},
    "BO4CW SCR": {"games": ["Black Ops 4", "Black Ops Cold War"], "csvs": ["bo4_var.csv", "bo4_function.csv", "bo4_namespace.csv", "bo4_class.csv", "bo4_event.csv", "bocw_var.csv", "bocw_function.csv", "bocw_namespace.csv", "bocw_class.csv", "bocw_event.csv"]},
    "FNV1A 63": {"games": ["Black Ops 4", "Black Ops Cold War", "Modern Warfare III"], "csvs": ["bo4_hash.csv", "bo4_script.csv", "bocw_hash.csv", "bocw_script.csv", "mwiii_hash.csv"]},
    "MWIII SCR": {"games": ["Modern Warfare III"], "csvs": ["mwiii_var.csv", "mwiii_function.csv", "mwiii_namespace.csv", "mwiii_andhash.csv"]},
    "IW Resources": {"games": ["Modern Warfare III", "Black Ops 6"], "csvs": ["mwiii_script.csv", "mwiii_rhash.csv", "mwiii_percenthash.csv", "bo6_script.csv", "bo6_rhash.csv", "bo6_percenthash.csv"]},
    "IW Tag FNV32": {"games": ["Modern Warfare III", "Black Ops 6"], "csvs": ["mwiii_thash.csv", "bo6_thash.csv"]},
    "IW Dvars": {"games": ["Modern Warfare III", "Black Ops 6"], "csvs": ["mwiii_dvar.csv", "bo6_dvar.csv"]},
    "FNV1A 64": {"games": ["Black Ops 6"], "csvs": ["bo6_hash.csv"]},
    "BO6 SCR": {"games": ["Black Ops 6"], "csvs": ["bo6_var.csv", "bo6_function.csv", "bo6_namespace.csv", "bo6_andhash.csv"]},
    "BO6 SP SCR": {"games": ["Black Ops 6"], "csvs": ["bo6_andhash.csv"]},
    "BO6 Omnvars": {"games": ["Black Ops 6"], "csvs": ["bo6_omnvar.csv"]}
}

def format_algorithms_text(selected_algorithms, all_hash_types):
    if set(selected_algorithms) == set(all_hash_types):
        return "All selected"
    if not selected_algorithms:
        return "None"
    if len(selected_algorithms) > 4:
        return "\n".join(selected_algorithms)
    return ", ".join(selected_algorithms)

def update_button_states(app):
    app.algo_list.config(state="normal" if not app.is_brute_force_running else "disabled")
    if hasattr(app, 'algo_frame'):
        for widget in app.algo_frame.winfo_children():
            for child in widget.winfo_children():
                child.configure(state="normal" if not app.is_brute_force_running else "disabled")
    app.select_characters_button.config(state="normal" if not app.is_char_window_open.get() and not app.is_brute_force_running else "disabled")
    app.custom_start_string_entry.config(state="normal" if not app.is_brute_force_running else "disabled")
    app.prefix_csv_button.config(state="normal" if not app.is_brute_force_running else "disabled")
    app.suffix_csv_button.config(state="normal" if not app.is_brute_force_running else "disabled")
    app.disable_uncommon_combinations_check.config(state="normal" if not app.is_brute_force_running else "disabled")
    app.require_vowel_check.config(state="normal" if not app.is_brute_force_running else "disabled")
    app.no_consecutive_symbols_check.config(state="normal" if not app.is_brute_force_running else "disabled")
    app.no_triple_rule_check.config(state="normal" if not app.is_brute_force_running else "disabled")
    app.no_four_vowels_check.config(state="normal" if not app.is_brute_force_running else "disabled")
    app.no_four_non_consonants_check.config(state="normal" if not app.is_brute_force_running else "disabled")
    app.no_three_uncommon_non_consonants_check.config(state="normal" if not app.is_brute_force_running else "disabled")
    app.brute_force_button.config(
        text="Stop Brute Force" if app.is_brute_force_running else "Start Brute Force",
        command=lambda: stop_brute_force(app) if app.is_brute_force_running else start_brute_force(app)
    )
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Button states updated: Algorithms {'enabled' if not app.is_brute_force_running else 'disabled'}, Characters {'enabled' if not app.is_char_window_open.get() else 'disabled'}, Brute Force {'Stop' if app.is_brute_force_running else 'Start'}")

def toggle_game_algorithms(app, game, hash_types):
    game_to_algorithms = {
        "Black Ops 3": ["BO3 SCR"],
        "Black Ops 4/Cold War": ["BO4CW SCR", "FNV1A 63"],
        "Modern Warfare III": ["MWIII SCR", "FNV1A 63", "IW Resources", "IW Dvars", "IW Tag FNV32"],
        "Black Ops 6": ["BO6 SCR", "BO6 SP SCR", "FNV1A 64", "IW Resources", "IW Dvars", "BO6 Omnvars", "IW Tag FNV32"]
    }
    selected_indices = app.algo_list.curselection()
    selected_algorithms = [hash_types[i] for i in selected_indices]
    game_algorithms = game_to_algorithms[game]
    all_selected = all(algo in selected_algorithms for algo in game_algorithms)
    
    if all_selected:
        for algo in game_algorithms:
            if algo in hash_types:
                app.algo_list.selection_clear(hash_types.index(algo))
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Deselected algorithms for {game}")
    else:
        for algo in game_algorithms:
            if algo in hash_types:
                app.algo_list.selection_set(hash_types.index(algo))
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Selected algorithms for {game}")
    
    save_algorithm_selection(app, hash_types)

def save_algorithm_selection(app, hash_types):
    selected_indices = app.algo_list.curselection()
    app.selected_algorithms = [hash_types[i] for i in selected_indices]
    algorithms_text = format_algorithms_text(app.selected_algorithms, hash_types)
    app.selected_algorithms_label.config(text=f"Selected Algorithms: {algorithms_text}")
    app.config_manager.save_brute_force_config(
        selected_algorithms=app.selected_algorithms,
        excluded_characters=app.excluded_characters,
        last_string=app.last_hashed_string,
        prefix_csv=app.prefix_csv.get(),
        suffix_csv=app.suffix_csv.get(),
        disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
        require_vowel=app.require_vowel.get(),
        no_consecutive_symbols=app.no_consecutive_symbols.get(),
        no_triple_rule=app.no_triple_rule.get(),
        no_four_vowels=app.no_four_vowels.get(),
        no_four_non_consonants=app.no_four_non_consonants.get(),
        no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
    )
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Algorithms: {algorithms_text}, Last string: {app.last_hashed_string or 'None'}, Prefix CSV: {app.prefix_csv.get() or 'None'}, Suffix CSV: {app.suffix_csv.get() or 'None'}")

def reset_selections(app):
    app.selected_algorithms = []
    app.excluded_characters = []
    app.prefix_csv.set("")
    app.suffix_csv.set("")
    app.disable_uncommon_combinations.set(False)
    app.require_vowel.set(False)
    app.no_consecutive_symbols.set(False)
    app.no_triple_rule.set(False)
    app.no_four_vowels.set(False)
    app.no_four_non_consonants.set(False)
    app.no_three_uncommon_non_consonants.set(False)
    app.algo_list.selection_clear(0, tk.END)
    app.selected_algorithms_label.config(text="Selected Algorithms: None")
    app.excluded_characters_label.config(text="Excluded Characters: None")
    app.prefix_csv_label.config(text="Prefix CSV: None")
    app.suffix_csv_label.config(text="Suffix CSV: None")
    app.config_manager.save_brute_force_config(
        selected_algorithms=app.selected_algorithms,
        excluded_characters=app.excluded_characters,
        last_string=app.last_hashed_string,
        prefix_csv=app.prefix_csv.get(),
        suffix_csv=app.suffix_csv.get(),
        disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
        require_vowel=app.require_vowel.get(),
        no_consecutive_symbols=app.no_consecutive_symbols.get(),
        no_triple_rule=app.no_triple_rule.get(),
        no_four_vowels=app.no_four_vowels.get(),
        no_four_non_consonants=app.no_four_non_consonants.get(),
        no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
    )
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Reset selections, Last string: {app.last_hashed_string or 'None'}, Prefix CSV: None, Suffix CSV: None")
    update_button_states(app)

def stop_brute_force(app):
    app.is_brute_force_running = False
    app.brute_force_stop = True
    app.current_string_label.config(text="Current String: None")
    app.custom_start_string_entry.config(state="normal")
    if app.last_hashed_string:
        app.custom_start_string_entry.delete(0, tk.END)
        app.custom_start_string_entry.insert(0, app.last_hashed_string)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Updated start string: {app.last_hashed_string}")
    app.config_manager.save_brute_force_config(
        selected_algorithms=app.selected_algorithms,
        excluded_characters=app.excluded_characters,
        last_string=app.last_hashed_string,
        prefix_csv=app.prefix_csv.get(),
        suffix_csv=app.suffix_csv.get(),
        disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
        require_vowel=app.require_vowel.get(),
        no_consecutive_symbols=app.no_consecutive_symbols.get(),
        no_triple_rule=app.no_triple_rule.get(),
        no_four_vowels=app.no_four_vowels.get(),
        no_four_non_consonants=app.no_four_non_consonants.get(),
        no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
    )
    update_button_states(app)
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force stopped, Last string: {app.last_hashed_string or 'None'}, Prefix CSV: {app.prefix_csv.get() or 'None'}, Suffix CSV: {app.suffix_csv.get() or 'None'}")

def select_prefix_csv(app):
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")],
        initialdir=os.path.dirname(app.prefix_csv.get()) if app.prefix_csv.get() else app.config_manager.get_folder()
    )
    if file_path:
        app.prefix_csv.set(file_path)
        app.prefix_csv_label.config(text=f"Prefix CSV: {os.path.basename(file_path)}")
        app.config_manager.save_brute_force_config(
            selected_algorithms=app.selected_algorithms,
            excluded_characters=app.excluded_characters,
            last_string=app.last_hashed_string,
            prefix_csv=app.prefix_csv.get(),
            suffix_csv=app.suffix_csv.get(),
            disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
            require_vowel=app.require_vowel.get(),
            no_consecutive_symbols=app.no_consecutive_symbols.get(),
            no_triple_rule=app.no_triple_rule.get(),
            no_four_vowels=app.no_four_vowels.get(),
            no_four_non_consonants=app.no_four_non_consonants.get(),
            no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
        )
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Selected prefix CSV: {file_path}")

def select_suffix_csv(app):
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")],
        initialdir=os.path.dirname(app.suffix_csv.get()) if app.suffix_csv.get() else app.config_manager.get_folder()
    )
    if file_path:
        app.suffix_csv.set(file_path)
        app.suffix_csv_label.config(text=f"Suffix CSV: {os.path.basename(file_path)}")
        app.config_manager.save_brute_force_config(
            selected_algorithms=app.selected_algorithms,
            excluded_characters=app.excluded_characters,
            last_string=app.last_hashed_string,
            prefix_csv=app.prefix_csv.get(),
            suffix_csv=app.suffix_csv.get(),
            disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
            require_vowel=app.require_vowel.get(),
            no_consecutive_symbols=app.no_consecutive_symbols.get(),
            no_triple_rule=app.no_triple_rule.get(),
            no_four_vowels=app.no_four_vowels.get(),
            no_four_non_consonants=app.no_four_non_consonants.get(),
            no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
        )
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Selected suffix CSV: {file_path}")

def start_brute_force(app):
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Attempting to start brute force")
    
    if not app.selected_algorithms:
        messagebox.showwarning("Warning", "Select at least one hashing algorithm.")
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force failed: No algorithms selected")
        return

    all_chars = list("abcdefghijklmnopqrstuvwxyz0123456789_/")
    app.allowed_chars = [char for char in all_chars if char not in app.excluded_characters]
    if not app.allowed_chars:
        messagebox.showwarning("Warning", "No characters available. Include at least one character.")
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force failed: No characters available")
        return

    algo_no_csvs = []
    app.cached_hashes = set()
    app.prefixes = []
    app.suffixes = []
    app.prefix_hashes = {}  # Store precomputed prefix hashes
    root_folder = os.path.dirname(os.path.abspath(__file__)).rsplit('gui', 1)[0]
    
    # Load prefixes and suffixes from selected CSVs
    prefix_csv = app.prefix_csv.get()
    if prefix_csv:
        if os.path.exists(prefix_csv):
            try:
                with open(prefix_csv, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader, None)  # Skip header
                    for row in reader:
                        if row and row[0]:
                            app.prefixes.append(row[0].lower())  # Ensure lowercase
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loaded {len(app.prefixes)} prefixes from {prefix_csv}")
            except Exception as e:
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error loading prefix CSV {prefix_csv}: {str(e)}")
        else:
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Prefix CSV not found: {prefix_csv}")
    
    suffix_csv = app.suffix_csv.get()
    if suffix_csv:
        if os.path.exists(suffix_csv):
            try:
                with open(suffix_csv, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    next(reader, None)  # Skip header
                    for row in reader:
                        if row and row[0]:
                            app.suffixes.append(row[0].lower())  # Ensure lowercase
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loaded {len(app.suffixes)} suffixes from {suffix_csv}")
            except Exception as e:
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error loading suffix CSV {suffix_csv}: {str(e)}")
        else:
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Suffix CSV not found: {suffix_csv}")

    # Precompute prefix hashes for each algorithm
    algo_to_func = {
        "BO3 SCR": black_ops_3_scr,
        "BO4CW SCR": hash_bo4cw_scr,
        "FNV1A 63": base_fnv1a_63,
        "MWIII SCR": mwii_iii_scr,
        "IW Resources": iw_resources,
        "IW Tag FNV32": base_fnv1a_32,
        "IW Dvars": iw_dvars,
        "FNV1A 64": base_fnv1a_64,
        "BO6 SCR": black_ops_6_scr,
        "BO6 SP SCR": black_ops_6_sp_scr,
        "BO6 Omnvars": black_ops_6_omnvars
    }
    for algo in app.selected_algorithms:
        app.prefix_hashes[algo] = {}
        hash_func = algo_to_func.get(algo)
        if not hash_func:
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No hash function for {algo}")
            continue
        for prefix in app.prefixes or ['']:
            if prefix:
                # Compute partial hash for prefix
                if algo in ["IW Dvars", "BO6 SCR", "BO6 Omnvars"]:
                    # For secure hashes, include first character and SEC_STRING
                    if len(prefix) >= 1:
                        sec_string = {
                            "IW Dvars": "q6n-+7=tyytg94_*",
                            "BO6 SCR": "zt@f3yp(d[kkd=_@",
                            "BO6 Omnvars": "gvbs9*vpm@mh@krh"
                        }.get(algo, "")
                        modified_prefix = prefix[0] + sec_string + prefix[1:]
                    else:
                        modified_prefix = prefix
                    hash_val = hash_func(modified_prefix)
                elif algo == "BO6 SP SCR":
                    # For BO6 SP SCR, append SEC_STRING
                    sec_string = "zt@f3yp(d[kkd=_@"
                    modified_prefix = prefix + sec_string
                    hash_val = hash_func(modified_prefix)
                else:
                    hash_val = hash_func(prefix)
                app.prefix_hashes[algo][prefix] = hash_val
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Precomputed hash for {algo}, prefix={prefix}, hash={hex(hash_val)[2:]}")
            else:
                app.prefix_hashes[algo][''] = None  # No prefix case

    # Load cached hashes from CSVs
    for algo in app.selected_algorithms:
        found_csv = False
        if algo in algo_to_csvs:
            for game in algo_to_csvs[algo]["games"]:
                game_folder = os.path.join(root_folder, game)
                if not os.path.exists(game_folder):
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Game folder not found: {game_folder}")
                    continue
                for csv_name in algo_to_csvs[algo]["csvs"]:
                    csv_path = os.path.join(game_folder, csv_name)
                    if os.path.exists(csv_path):
                        found_csv = True
                        try:
                            with open(csv_path, 'r', encoding='utf-8') as f:
                                reader = csv.reader(f)
                                next(reader, None)
                                for row in reader:
                                    if row and row[0]:
                                        hash_value = row[0].lstrip('0') or '0'
                                        app.cached_hashes.add(hash_value)
                            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Cached {csv_name} for {algo}")
                        except Exception as e:
                            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error reading {csv_name}: {str(e)}")
                    else:
                        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CSV not found: {csv_path}")
            if not found_csv:
                algo_no_csvs.append(algo)

    if algo_no_csvs:
        error_msg = f"No CSV files found for: {', '.join(algo_no_csvs)}."
        messagebox.showerror("Error", error_msg)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force failed: {error_msg}")
        return

    if not app.cached_hashes:
        messagebox.showerror("Error", "No hashes found for selected algorithms.")
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force failed: No hashes found")
        return

    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Cached {len(app.cached_hashes)} hashes")

    app.is_brute_force_running = True
    update_button_states(app)

    start_string = app.custom_start_string_entry.get().strip().lower()  # Ensure lowercase
    app.last_hashed_string = start_string or ""
    start_length = max(1, len(start_string))

    if start_string and not all(c in app.allowed_chars for c in start_string):
        messagebox.showwarning("Warning", "Start string contains excluded characters.")
        app.is_brute_force_running = False
        update_button_states(app)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force failed: Invalid start string")
        return

    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting brute force: Algorithms={', '.join(app.selected_algorithms)}, Chars={''.join(app.allowed_chars)}, Start={start_string or 'None'}, Length={start_length}, Prefix CSV={prefix_csv or 'None'}, Suffix CSV={suffix_csv or 'None'}, Filters=[Uncommon={'on' if app.disable_uncommon_combinations.get() else 'off'}, Vowel={'on' if app.require_vowel.get() else 'off'}, Symbols={'on' if app.no_consecutive_symbols.get() else 'off'}, Triple={'on' if app.no_triple_rule.get() else 'off'}, FourVowels={'on' if app.no_four_vowels.get() else 'off'}, FourNonCon QQConsonants={'on' if app.no_four_non_consonants.get() else 'off'}, ThreeUncommonNonConsonants={'on' if app.no_three_uncommon_non_consonants.get() else 'off'}]")

    app.brute_force_length = start_length
    app.brute_force_iterator = itertools.product(app.allowed_chars, repeat=start_length)
    app.brute_force_stop = False
    app.brute_force_started = True

    if start_string:
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Advancing to start string: {start_string}")
        try:
            while True:
                combo = next(app.brute_force_iterator)
                current_string = ''.join(combo)
                if current_string >= start_string:
                    app.brute_force_iterator = itertools.chain([combo], itertools.product(app.allowed_chars, repeat=start_length))
                    break
        except StopIteration:
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Start string {start_string} is beyond available combinations")
            messagebox.showwarning("Warning", f"Invalid start string: {start_string}")
            app.is_brute_force_running = False
            update_button_states(app)
            return
        except Exception as e:
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error advancing to start string: {str(e)}")
            messagebox.showwarning("Warning", f"Error with start string: {str(e)}")
            app.is_brute_force_running = False
            update_button_states(app)
            return

    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iterator initialized, scheduling brute_force_step")
    app.root.after(1, brute_force_step, app)

def brute_force_step(app):
    if not app.is_brute_force_running or app.brute_force_stop:
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force step stopped: Running={app.is_brute_force_running}, Stop={app.brute_force_stop}")
        logging.debug(f"Brute force step stopped: Running={app.is_brute_force_running}, Stop={app.brute_force_stop}")
        stop_brute_force(app)
        return

    try:
        # Process strings in batches, ensuring lowercase
        batch_size = 1000
        batch = []
        for _ in range(batch_size):
            try:
                combo = next(app.brute_force_iterator)
                batch.append(''.join(combo).lower())  # Force lowercase
            except StopIteration:
                break

        if not batch:
            max_length = 10
            if app.brute_force_length >= max_length:
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Reached max length {max_length}, stopping")
                logging.debug(f"Reached max length: {max_length}")
                stop_brute_force(app)
                return
            app.brute_force_length += 1
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Advancing to length: {app.brute_force_length}")
            logging.debug(f"Advancing to length: {app.brute_force_length}")
            app.brute_force_iterator = itertools.product(app.allowed_chars, repeat=app.brute_force_length)
            app.brute_force_started = True
            app.root.after(1, brute_force_step, app)
            return

        # Filter batch
        valid_strings = filter_strings(
            batch,
            require_vowel=app.require_vowel.get(),
            no_uncommon=app.disable_uncommon_combinations.get(),
            no_consecutive_symbols=app.no_consecutive_symbols.get(),
            no_triple=app.no_triple_rule.get(),
            no_four_vowels=app.no_four_vowels.get(),
            no_four_non_consonants=app.no_four_non_consonants.get(),
            no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
        )

        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processed batch: {len(batch)} strings, {len(valid_strings)} valid")
        logging.debug(f"Processed batch: {len(batch)} strings, {len(valid_strings)} valid")

        algo_to_func = {
            "BO3 SCR": black_ops_3_scr,
            "BO4CW SCR": hash_bo4cw_scr,
            "FNV1A 63": base_fnv1a_63,
            "MWIII SCR": mwii_iii_scr,
            "IW Resources": iw_resources,
            "IW Tag FNV32": base_fnv1a_32,
            "IW Dvars": iw_dvars,
            "FNV1A 64": base_fnv1a_64,
            "BO6 SCR": black_ops_6_scr,
            "BO6 SP SCR": black_ops_6_sp_scr,
            "BO6 Omnvars": black_ops_6_omnvars
        }

        algo_to_datatype = {
            "BO3 SCR": "scr",
            "BO4CW SCR": "scr",
            "FNV1A 63": "hash",
            "MWIII SCR": "scr",
            "IW Resources": "resources",
            "IW Tag FNV32": "tag",
            "IW Dvars": "dvars",
            "FNV1A 64": "hash",
            "BO6 SCR": "scr",
            "BO6 SP SCR": "sp_scr",
            "BO6 Omnvars": "omnvars"
        }

        root_folder = os.path.dirname(os.path.abspath(__file__)).rsplit('gui', 1)[0]

        def compute_hash(algo, prefix, string, suffix):
            """Compute hash for a prefix + string + suffix combination."""
            hash_func = algo_to_func[algo]
            if algo in ["IW Dvars", "BO6 SCR", "BO6 Omnvars"]:
                # Secure hash: insert SEC_STRING after first character
                sec_string = {
                    "IW Dvars": "q6n-+7=tyytg94_*",
                    "BO6 SCR": "zt@f3yp(d[kkd=_@",
                    "BO6 Omnvars": "gvbs9*vpm@mh@krh"
                }.get(algo, "")
                combo = (prefix or '') + string
                if len(combo) >= 1:
                    modified_combo = combo[0] + sec_string + combo[1:] + (suffix or '')
                else:
                    modified_combo = combo + (suffix or '')
                hash_val = hash_func(modified_combo)
            elif algo == "BO6 SP SCR":
                # Secure hash with suffix: append SEC_STRING
                sec_string = "zt@f3yp(d[kkd=_@"
                modified_combo = (prefix or '') + string + sec_string + (suffix or '')
                hash_val = hash_func(modified_combo)
            else:
                # Standard hash
                combo = (prefix or '') + string + (suffix or '')
                hash_val = hash_func(combo)
            return hash_val

        def save_hash_match(algo, combo, hash_value):
            """Save a hash match to the appropriate CSV file."""
            datatype = algo_to_datatype.get(algo, "unknown")
            for game in algo_to_csvs[algo]["games"]:
                game_folder = os.path.join(root_folder, game)
                if not os.path.exists(game_folder):
                    continue
                found_csv = os.path.join(game_folder, f"{datatype}_found.csv")
                is_duplicate = False
                if os.path.exists(found_csv):
                    try:
                        with open(found_csv, 'r', encoding='utf-8') as f:
                            reader = csv.reader(f)
                            header = next(reader, None)
                            if header and header[0] == "hash":
                                for row in reader:
                                    if row and row[0] == hash_value:
                                        is_duplicate = True
                                        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Duplicate match in {found_csv}: {hash_value}")
                                        logging.debug(f"Duplicate match in {found_csv}: {hash_value}")
                                        break
                    except Exception as e:
                        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error reading {found_csv}: {str(e)}")
                        logging.debug(f"Error reading {found_csv}: {str(e)}")

                if not is_duplicate:
                    try:
                        file_exists = os.path.exists(found_csv)
                        with open(found_csv, 'a', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            if not file_exists:
                                writer.writerow(["hash", "data"])
                            writer.writerow([hash_value, combo])
                        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Saved match to {found_csv}")
                        logging.debug(f"Saved match to {found_csv}")
                    except Exception as e:
                        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error writing to {found_csv}: {str(e)}")
                        logging.debug(f"Error writing to {found_csv}: {str(e)}")

        for current_string in valid_strings:
            # Update GUI with current string
            app.current_string_label.config(text=f"Current String: {current_string}")
            app.last_hashed_string = current_string
            app.root.update()

            # Generate all combinations: string, prefix+string, string+suffix, prefix+string+suffix
            for algo in app.selected_algorithms:
                hash_func = algo_to_func.get(algo)
                if not hash_func:
                    continue

                # 1. Check string alone
                hash_val = compute_hash(algo, '', current_string, '')
                hash_value = hex(hash_val)[2:].lstrip('0') or '0'
                if algo not in ["FNV1A 63", "FNV1A 64", "BO6 SCR", "BO6 SP SCR", "IW Resources", "IW Dvars", "BO6 Omnvars"]:
                    hash_value = hash_value.zfill(8)
                if hash_value in app.cached_hashes:
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Match: {algo}, String={current_string}, Hash={hash_value}")
                    logging.debug(f"Match: {algo}, String={current_string}, Hash={hash_value}")
                    save_hash_match(algo, current_string, hash_value)

                # 2. Check prefix + string
                for prefix in app.prefixes or ['']:
                    if prefix:
                        hash_val = compute_hash(algo, prefix, current_string, '')
                        hash_value = hex(hash_val)[2:].lstrip('0') or '0'
                        if algo not in ["FNV1A 63", "FNV1A 64", "BO6 SCR", "BO6 SP SCR", "IW Resources", "IW Dvars", "BO6 Omnvars"]:
                            hash_value = hash_value.zfill(8)
                        if hash_value in app.cached_hashes:
                            combo = prefix + current_string
                            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Match: {algo}, String={combo}, Hash={hash_value}")
                            logging.debug(f"Match: {algo}, String={combo}, Hash={hash_value}")
                            save_hash_match(algo, combo, hash_value)

                # 3. Check string + suffix
                for suffix in app.suffixes or ['']:
                    if suffix:
                        hash_val = compute_hash(algo, '', current_string, suffix)
                        hash_value = hex(hash_val)[2:].lstrip('0') or '0'
                        if algo not in ["FNV1A 63", "FNV1A 64", "BO6 SCR", "BO6 SP SCR", "IW Resources", "IW Dvars", "BO6 Omnvars"]:
                            hash_value = hash_value.zfill(8)
                        if hash_value in app.cached_hashes:
                            combo = current_string + suffix
                            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Match: {algo}, String={combo}, Hash={hash_value}")
                            logging.debug(f"Match: {algo}, String={combo}, Hash={hash_value}")
                            save_hash_match(algo, combo, hash_value)

                # 4. Check prefix + string + suffix
                for prefix in app.prefixes or ['']:
                    for suffix in app.suffixes or ['']:
                        if prefix and suffix:
                            hash_val = compute_hash(algo, prefix, current_string, suffix)
                            hash_value = hex(hash_val)[2:].lstrip('0') or '0'
                            if algo not in ["FNV1A 63", "FNV1A 64", "BO6 SCR", "BO6 SP SCR", "IW Resources", "IW Dvars", "BO6 Omnvars"]:
                                hash_value = hash_value.zfill(8)
                            if hash_value in app.cached_hashes:
                                combo = prefix + current_string + suffix
                                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Match: {algo}, String={combo}, Hash={hash_value}")
                                logging.debug(f"Match: {algo}, String={combo}, Hash={hash_value}")
                                save_hash_match(algo, combo, hash_value)

        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Scheduling next brute_force_step")
        logging.debug("Scheduling next brute_force_step")
        app.root.after(1, brute_force_step, app)

    except Exception as e:
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error in brute force: {str(e)}")
        logging.debug(f"Error in brute force: {str(e)}")
        stop_brute_force(app)
        
def setup_brute_force_tab(app, tab):
    frame = tk.Frame(tab, bg="#222222")
    frame.pack(pady=10, padx=10, fill="both", expand=True)

    app.is_char_window_open = tk.BooleanVar(value=False)
    app.is_brute_force_running = False
    app.prefix_csv = tk.StringVar(value="")
    app.suffix_csv = tk.StringVar(value="")

    config = app.config_manager.load_config()
    app.selected_algorithms = config.get('selected_algorithms', [])
    app.excluded_characters = config.get('excluded_characters', [])
    app.last_hashed_string = config.get('last_hashed_string', None)
    app.prefix_csv.set(config.get('prefix_csv', ""))
    app.suffix_csv.set(config.get('suffix_csv', ""))
    app.disable_uncommon_combinations = tk.BooleanVar(value=config.get('disable_uncommon_combinations', False))
    app.require_vowel = tk.BooleanVar(value=config.get('require_vowel', False))
    app.no_consecutive_symbols = tk.BooleanVar(value=config.get('no_consecutive_symbols', False))
    app.no_triple_rule = tk.BooleanVar(value=config.get('no_triple_rule', False))
    app.no_four_vowels = tk.BooleanVar(value=config.get('no_four_vowels', False))
    app.no_four_non_consonants = tk.BooleanVar(value=config.get('no_four_non_consonants', False))
    app.no_three_uncommon_non_consonants = tk.BooleanVar(value=config.get('no_three_uncommon_non_consonants', False))

    left_frame = tk.Frame(frame, bg="#222222")
    left_frame.pack(side="left", padx=10, pady=5, fill="y")

    app.algo_frame = tk.Frame(left_frame, bg="#222222")
    app.algo_frame.pack(fill="both", pady=5)

    hash_types = [
        "BO3 SCR", "BO4CW SCR", "FNV1A 63", "MWIII SCR", "IW Resources",
        "IW Tag FNV32", "IW Dvars", "FNV1A 64", "BO6 SCR", "BO6 SP SCR", "BO6 Omnvars"
    ]
    game_to_keys = {
        "Black Ops 3": ["BO3 SCR"],
        "Black Ops 4/Cold War": ["BO4CW SCR", "FNV1A 63"],
        "Modern Warfare III": ["MWIII SCR", "FNV1A 63", "IW Resources", "IW Dvars", "IW Tag FNV32"],
        "Black Ops 6": ["BO6 SCR", "BO6 SP SCR", "FNV1A 64", "IW Resources", "IW Dvars", "BO6 Omnvars", "IW Tag FNV32"]
    }

    listbox_frame = ttk.Frame(app.algo_frame)
    listbox_frame.pack(fill="both", pady=5)
    app.algo_list = tk.Listbox(
        listbox_frame,
        selectmode="multiple",
        height=len(hash_types),
        width=30,
        bg="#333333",
        fg="#E07B00",
        selectbackground="#555555",
        selectforeground="white",
        font=("Courier", 12)
    )
    for hash_type in hash_types:
        app.algo_list.insert(tk.END, hash_type)
    for algo in app.selected_algorithms:
        if algo in hash_types:
            app.algo_list.selection_set(hash_types.index(algo))
    app.algo_list.pack(padx=5, pady=5)
    app.algo_list.bind('<<ListboxSelect>>', lambda e: save_algorithm_selection(app, hash_types))

    toggle_frame = tk.Frame(app.algo_frame, bg="#222222")
    toggle_frame.pack(fill="x", pady=5)
    for game in game_to_keys:
        btn = ttk.Button(toggle_frame, text=game, command=lambda g=game: toggle_game_algorithms(app, g, hash_types))
        btn.pack(side="left", padx=2)
        Tooltip(btn, f"Toggle algorithms for {game}")

    app.selected_algorithms_label = ttk.Label(left_frame, text=f"Selected Algorithms: {format_algorithms_text(app.selected_algorithms, hash_types)}", background="#222222", foreground="white")
    app.selected_algorithms_label.pack(fill="x", pady=10)

    app.select_characters_button = ttk.Button(left_frame, text="Select Characters to Exclude", command=lambda: open_character_selection(app))
    app.select_characters_button.pack(pady=10)

    app.excluded_characters_label = ttk.Label(left_frame, text=f"Excluded Characters: {''.join(app.excluded_characters) or 'None'}", background="#222222", foreground="#E07B00")
    app.excluded_characters_label.pack(fill="x", pady=5)

    ttk.Button(left_frame, text="Reset Selections", command=lambda: reset_selections(app)).pack(pady=5)

    right_frame = tk.Frame(frame, bg="#222222")
    right_frame.pack(side="left", padx=10, pady=5, fill="y")

    # Prefix and Suffix CSV selection
    prefix_frame = tk.Frame(right_frame, bg="#222222")
    prefix_frame.pack(fill="x", pady=5)
    ttk.Label(prefix_frame, text="Prefix CSV:", background="#222222", foreground="white").pack(side="left")
    app.prefix_csv_button = ttk.Button(prefix_frame, text="Select File", command=lambda: select_prefix_csv(app))
    app.prefix_csv_button.pack(side="left", padx=5)
    app.prefix_csv_label = ttk.Label(prefix_frame, text=f"Prefix CSV: {os.path.basename(app.prefix_csv.get()) if app.prefix_csv.get() else 'None'}", background="#222222", foreground="white")
    app.prefix_csv_label.pack(side="left")
    Tooltip(app.prefix_csv_button, "Select CSV file for prefix strings")

    suffix_frame = tk.Frame(right_frame, bg="#222222")
    suffix_frame.pack(fill="x", pady=5)
    ttk.Label(suffix_frame, text="Suffix CSV:", background="#222222", foreground="white").pack(side="left")
    app.suffix_csv_button = ttk.Button(suffix_frame, text="Select File", command=lambda: select_suffix_csv(app))
    app.suffix_csv_button.pack(side="left", padx=5)
    app.suffix_csv_label = ttk.Label(suffix_frame, text=f"Suffix CSV: {os.path.basename(app.suffix_csv.get()) if app.suffix_csv.get() else 'None'}", background="#222222", foreground="white")
    app.suffix_csv_label.pack(side="left")
    Tooltip(app.suffix_csv_button, "Select CSV file for suffix strings")

    custom_string_frame = tk.Frame(right_frame, bg="#222222")
    custom_string_frame.pack(fill="x", pady=5)
    ttk.Label(custom_string_frame, text="Start String:", background="#222222", foreground="white").pack(side="left")
    app.custom_start_string_entry = ttk.Entry(custom_string_frame, width=30)
    app.custom_start_string_entry.pack(side="left", padx=5)
    if app.last_hashed_string:
        app.custom_start_string_entry.insert(0, app.last_hashed_string)
    Tooltip(app.custom_start_string_entry, "Starting string for brute force")

    app.current_string_label = ttk.Label(right_frame, text="Current String: None", background="#222222", foreground="white")
    app.current_string_label.pack(anchor="w", pady=5)

    app.brute_force_button = ttk.Button(right_frame, text="Start Brute Force", command=lambda: start_brute_force(app))
    app.brute_force_button.pack(anchor="w", pady=10)

    app.disable_uncommon_combinations_check = ttk.Checkbutton(
        right_frame,
        text="Disable Uncommon Letter Combinations",
        variable=app.disable_uncommon_combinations,
        command=lambda: app.config_manager.save_brute_force_config(
            selected_algorithms=app.selected_algorithms,
            excluded_characters=app.excluded_characters,
            last_string=app.last_hashed_string,
            prefix_csv=app.prefix_csv.get(),
            suffix_csv=app.suffix_csv.get(),
            disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
            require_vowel=app.require_vowel.get(),
            no_consecutive_symbols=app.no_consecutive_symbols.get(),
            no_triple_rule=app.no_triple_rule.get(),
            no_four_vowels=app.no_four_vowels.get(),
            no_four_non_consonants=app.no_four_non_consonants.get(),
            no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
        )
    )
    app.disable_uncommon_combinations_check.pack(anchor="w", pady=5)
    Tooltip(app.disable_uncommon_combinations_check, "Skip strings with uncommon letter pairs")

    app.require_vowel_check = ttk.Checkbutton(
        right_frame,
        text="Require At Least One Vowel",
        variable=app.require_vowel,
        command=lambda: app.config_manager.save_brute_force_config(
            selected_algorithms=app.selected_algorithms,
            excluded_characters=app.excluded_characters,
            last_string=app.last_hashed_string,
            prefix_csv=app.prefix_csv.get(),
            suffix_csv=app.suffix_csv.get(),
            disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
            require_vowel=app.require_vowel.get(),
            no_consecutive_symbols=app.no_consecutive_symbols.get(),
            no_triple_rule=app.no_triple_rule.get(),
            no_four_vowels=app.no_four_vowels.get(),
            no_four_non_consonants=app.no_four_non_consonants.get(),
            no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
        )
    )
    app.require_vowel_check.pack(anchor="w", pady=5)
    Tooltip(app.require_vowel_check, "Skip strings without a vowel (aeiou)")

    app.no_consecutive_symbols_check = ttk.Checkbutton(
        right_frame,
        text="No Consecutive Symbols",
        variable=app.no_consecutive_symbols,
        command=lambda: app.config_manager.save_brute_force_config(
            selected_algorithms=app.selected_algorithms,
            excluded_characters=app.excluded_characters,
            last_string=app.last_hashed_string,
            prefix_csv=app.prefix_csv.get(),
            suffix_csv=app.suffix_csv.get(),
            disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
            require_vowel=app.require_vowel.get(),
            no_consecutive_symbols=app.no_consecutive_symbols.get(),
            no_triple_rule=app.no_triple_rule.get(),
            no_four_vowels=app.no_four_vowels.get(),
            no_four_non_consonants=app.no_four_non_consonants.get(),
            no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
        )
    )
    app.no_consecutive_symbols_check.pack(anchor="w", pady=5)
    Tooltip(app.no_consecutive_symbols_check, "Skip strings with __, //, _/, or /_")

    app.no_triple_rule_check = ttk.Checkbutton(
        right_frame,
        text="No Triple Characters",
        variable=app.no_triple_rule,
        command=lambda: app.config_manager.save_brute_force_config(
            selected_algorithms=app.selected_algorithms,
            excluded_characters=app.excluded_characters,
            last_string=app.last_hashed_string,
            prefix_csv=app.prefix_csv.get(),
            suffix_csv=app.suffix_csv.get(),
            disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
            require_vowel=app.require_vowel.get(),
            no_consecutive_symbols=app.no_consecutive_symbols.get(),
            no_triple_rule=app.no_triple_rule.get(),
            no_four_vowels=app.no_four_vowels.get(),
            no_four_non_consonants=app.no_four_non_consonants.get(),
            no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
        )
    )
    app.no_triple_rule_check.pack(anchor="w", pady=5)
    Tooltip(app.no_triple_rule_check, "Skip strings with any character repeated three times")

    app.no_four_vowels_check = ttk.Checkbutton(
        right_frame,
        text="No Four Vowels in a Row",
        variable=app.no_four_vowels,
        command=lambda: app.config_manager.save_brute_force_config(
            selected_algorithms=app.selected_algorithms,
            excluded_characters=app.excluded_characters,
            last_string=app.last_hashed_string,
            prefix_csv=app.prefix_csv.get(),
            suffix_csv=app.suffix_csv.get(),
            disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
            require_vowel=app.require_vowel.get(),
            no_consecutive_symbols=app.no_consecutive_symbols.get(),
            no_triple_rule=app.no_triple_rule.get(),
            no_four_vowels=app.no_four_vowels.get(),
            no_four_non_consonants=app.no_four_non_consonants.get(),
            no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
        )
    )
    app.no_four_vowels_check.pack(anchor="w", pady=5)
    Tooltip(app.no_four_vowels_check, "Skip strings with four consecutive vowels")

    app.no_four_non_consonants_check = ttk.Checkbutton(
        right_frame,
        text="No Four Non-Consonants in a Row",
        variable=app.no_four_non_consonants,
        command=lambda: app.config_manager.save_brute_force_config(
            selected_algorithms=app.selected_algorithms,
            excluded_characters=app.excluded_characters,
            last_string=app.last_hashed_string,
            prefix_csv=app.prefix_csv.get(),
            suffix_csv=app.suffix_csv.get(),
            disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
            require_vowel=app.require_vowel.get(),
            no_consecutive_symbols=app.no_consecutive_symbols.get(),
            no_triple_rule=app.no_triple_rule.get(),
            no_four_vowels=app.no_four_vowels.get(),
            no_four_non_consonants=app.no_four_non_consonants.get(),
            no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
        )
    )
    app.no_four_non_consonants_check.pack(anchor="w", pady=5)
    Tooltip(app.no_four_non_consonants_check, "Skip strings with four consecutive non-consonants (vowels, digits, or symbols)")

    app.no_three_uncommon_non_consonants_check = ttk.Checkbutton(
        right_frame,
        text="No Three Uncommon Non-Consonants",
        variable=app.no_three_uncommon_non_consonants,
        command=lambda: app.config_manager.save_brute_force_config(
            selected_algorithms=app.selected_algorithms,
            excluded_characters=app.excluded_characters,
            last_string=app.last_hashed_string,
            prefix_csv=app.prefix_csv.get(),
            suffix_csv=app.suffix_csv.get(),
            disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
            require_vowel=app.require_vowel.get(),
            no_consecutive_symbols=app.no_consecutive_symbols.get(),
            no_triple_rule=app.no_triple_rule.get(),
            no_four_vowels=app.no_four_vowels.get(),
            no_four_non_consonants=app.no_four_non_consonants.get(),
            no_three_uncommon_non_consonants=app.no_three_uncommon_non_consonants.get()
        )
    )
    app.no_three_uncommon_non_consonants_check.pack(anchor="w", pady=5)
    Tooltip(app.no_three_uncommon_non_consonants_check, "Skip strings with three consecutive digits or symbols")

    update_button_states(app)
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute Force tab initialized with prefix CSV: {app.prefix_csv.get() or 'None'}, suffix CSV: {app.suffix_csv.get() or 'None'}")