import tkinter as tk
from tkinter import ttk, messagebox
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

# Configure logging to debug.log
logging.basicConfig(
    filename='debug.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Helper function for uncommon letter combinations
def is_vowel(letter: str) -> bool:
    return letter in 'aeiou'

def bad_letter_combo(new_letter: str, next_letter: str) -> bool:
    if new_letter == "a": return check_a(next_letter)
    elif new_letter == "b": return check_b(next_letter)
    elif new_letter == "c": return check_c(next_letter)
    elif new_letter == "d": return check_d(next_letter)
    elif new_letter == "e": return check_e(next_letter)
    elif new_letter == "f": return check_f(next_letter)
    elif new_letter == "g": return check_g(next_letter)
    elif new_letter == "h": return check_h(next_letter)
    elif new_letter == "i": return check_i(next_letter)
    elif new_letter == "j": return check_j(next_letter)
    elif new_letter == "k": return check_k(next_letter)
    elif new_letter == "l": return check_l(next_letter)
    elif new_letter == "m": return check_m(next_letter)
    elif new_letter == "n": return check_n(next_letter)
    elif new_letter == "o": return True
    elif new_letter == "p": return check_p(next_letter)
    elif new_letter == "q": return check_q(next_letter)
    elif new_letter == "r": return check_r(next_letter)
    elif new_letter == "s": return check_s(next_letter)
    elif new_letter == "t": return check_t(next_letter)
    elif new_letter == "u": return check_u(next_letter)
    elif new_letter == "v": return check_v(next_letter)
    elif new_letter == "w": return check_w(next_letter)
    elif new_letter == "x": return check_x(next_letter)
    elif new_letter == "y": return check_y(next_letter)
    elif new_letter == "z": return check_z(next_letter)
    elif new_letter == "_": return check__(next_letter)
    else:
        logging.error(f"Unknown bad letter combo: new_letter={new_letter}, next_letter={next_letter}")
        return False

def check_a(next_letter: str) -> bool:
    return next_letter != "a"

def check_b(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "ls_"

def check_c(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "hklrt"

def check_d(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "bcglmrw_"

def check_e(next_letter: str) -> bool:
    return next_letter not in "ei"

def check_f(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "lrt_"

def check_g(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "lmnr_"

def check_h(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "lt_"

def check_i(next_letter: str) -> bool:
    return next_letter not in "iy"

def check_j(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter == "_"

def check_k(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "ln_"

def check_l(next_letter: str) -> bool:
    return next_letter not in "jnpqrvwxyz_"

def check_m(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "bp_"

def check_n(next_letter: str) -> bool:
    return next_letter not in "mnqxyz_"

def check_p(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "ghlqrt_"

def check_q(next_letter: str) -> bool:
    return next_letter == "u"

def check_r(next_letter: str) -> bool:
    return next_letter not in "fhjpqrvxyz"

def check_s(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "cdklmnpt_"

def check_t(next_letter: str) -> bool:
    return next_letter not in "djkmnpqsvxyz"

def check_u(next_letter: str) -> bool:
    return next_letter not in "uy"

def check_v(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter == "_"

def check_w(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "hr_"

def check_x(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter in "p_"

def check_y(next_letter: str) -> bool:
    return next_letter not in "dfhjksvxyz"

def check_z(next_letter: str) -> bool:
    return is_vowel(next_letter) or next_letter == "_"

def check__(next_letter: str) -> bool:
    return next_letter != "_"

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height()
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#FFFFE0", foreground="#000000",
                         relief="solid", borderwidth=1, font=("TkDefaultFont", 10))
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def format_algorithms_text(selected_algorithms, all_hash_types):
    if set(selected_algorithms) == set(all_hash_types):
        return "All Selected"
    if not selected_algorithms:
        return "None"
    if len(selected_algorithms) > 3:
        return "\n".join(selected_algorithms)
    return ", ".join(selected_algorithms)

def update_button_states(app):
    app.algo_listbox.config(state="normal" if not app.is_brute_force_running else "disabled")
    if hasattr(app, 'toggle_frame'):
        for child in app.toggle_frame.winfo_children():
            child.configure(state="normal" if not app.is_brute_force_running else "disabled")
    app.select_characters_button.config(state="normal" if not app.is_char_window_open and not app.is_brute_force_running else "disabled")
    app.custom_start_string_entry.configure(state="normal" if not app.is_brute_force_running else "disabled")
    app.disable_uncommon_combinations_check.config(state="normal" if not app.is_brute_force_running else "disabled")
    if app.is_brute_force_running:
        app.brute_force_button.config(text="Stop Brute Force", command=lambda: stop_brute_force(app))
    else:
        app.brute_force_button.config(text="Start Brute Force", command=lambda: start_brute_force(app))
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Updated button states: Algorithms listbox {'enabled' if not app.is_brute_force_running else 'disabled'}, Characters button {'enabled' if not app.is_char_window_open else 'disabled'}, Brute Force button {'Stop' if app.is_brute_force_running else 'Start'}")

def toggle_game_algorithms(app, game, hash_types):
    game_to_algorithms = {
        "Black Ops 3": ["BO3 SCR"],
        "Black Ops 4/Cold War": ["BO4CW SCR", "FNV1A 63"],
        "Modern Warfare III": ["MWIII SCR", "FNV1A 63", "IW Resources", "IW Dvars", "IW Tag FNV32"],
        "Black Ops 6": ["BO6 SCR", "BO6 SP SCR", "FNV1A 64", "IW Resources", "IW Dvars", "BO6 Omnvars", "IW Tag FNV32"]
    }
    selected_indices = app.algo_listbox.curselection()
    selected_algorithms = [hash_types[i] for i in selected_indices]
    game_algorithms = game_to_algorithms[game]
    all_game_selected = all(algo in selected_algorithms for algo in game_algorithms)
    if all_game_selected:
        for algo in game_algorithms:
            try:
                index = hash_types.index(algo)
                app.algo_listbox.selection_clear(index)
            except ValueError:
                pass
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Deselected all algorithms for {game}")
    else:
        for algo in game_algorithms:
            try:
                index = hash_types.index(algo)
                app.algo_listbox.selection_set(index)
            except ValueError:
                pass
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Selected all algorithms for {game}")
    save_algorithm_selection(app, hash_types)

def save_algorithm_selection(app, hash_types):
    selected_indices = app.algo_listbox.curselection()
    app.selected_algorithms = [hash_types[i] for i in selected_indices]
    algorithms_text = format_algorithms_text(app.selected_algorithms, hash_types)
    app.selected_algorithms_label.config(text=f"Selected Algorithms: {algorithms_text}")
    app.config_manager.save_brute_force_config(
        app.selected_algorithms,
        app.excluded_characters,
        last_string=app.last_hashed_string,
        disable_uncommon_combinations=app.disable_uncommon_combinations.get()
    )
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Selected algorithms: {algorithms_text}, last_string: {app.last_hashed_string or 'None'}")

def reset_selections(app):
    app.selected_algorithms = []
    app.excluded_characters = []
    app.disable_uncommon_combinations.set(False)
    app.algo_listbox.selection_clear(0, tk.END)
    app.selected_algorithms_label.config(text="Selected Algorithms: None")
    app.excluded_characters_label.config(text="Excluded Characters: None")
    app.config_manager.save_brute_force_config(
        app.selected_algorithms,
        app.excluded_characters,
        last_string=app.last_hashed_string,
        disable_uncommon_combinations=app.disable_uncommon_combinations.get()
    )
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Reset selections: algorithms, excluded characters, and filters, last_string: {app.last_hashed_string or 'None'}")
    update_button_states(app)

def open_character_selection(app):
    if app.is_char_window_open:
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Character exclusion window already open")
        return

    app.is_char_window_open = True
    update_button_states(app)

    characters = list("abcdefghijklmnopqrstuvwxyz0123456789_/")
    numbers = list("0123456789")
    symbols = list("_/")
    vowels = list("aeiou")
    non_vowels = [c for c in "abcdefghijklmnopqrstuvwxyz" if c not in vowels]

    char_window = tk.Toplevel(app.root)
    char_window.title("Select Characters to Exclude")
    char_window.configure(bg="#222222")
    char_window.protocol("WM_DELETE_WINDOW", lambda: close_char_window(app, char_window))

    screen_width = app.root.winfo_screenwidth()
    screen_height = app.root.winfo_screenheight()
    max_width = int(screen_width * 0.8)
    max_height = int(screen_height * 0.8)
    estimated_width = max(700, min(800, max_width))
    estimated_height = max(500, min(600, max_height))
    char_window.geometry(f"{estimated_width}x{estimated_height}")

    label = ttk.Label(char_window, text="Select Characters to Exclude:", background="#222222", foreground="#E07B00", font=("TkDefaultFont", 14, "bold"))
    label.pack(pady=10, anchor="center")

    keyboard_frame = tk.Frame(char_window, bg="#222222")
    keyboard_frame.pack(pady=10, anchor="center")

    style = ttk.Style()
    style.configure("Large.TCheckbutton", font=("Courier", 12), padding=10, background="#222222", foreground="#E07B00")

    qwerty_rows = [
        list("1234567890"),
        list("qwertyuiop"),
        list("asdfghjkl"),
        list("zxcvbnm"),
        list("_/")
    ]

    char_vars = {char: tk.BooleanVar(value=char in app.excluded_characters) for char in characters}

    for row_idx, row_chars in enumerate(qwerty_rows):
        row_frame = tk.Frame(keyboard_frame, bg="#222222")
        row_frame.pack(pady=8)
        container_frame = tk.Frame(row_frame, bg="#222222")
        container_frame.pack(anchor="center")
        max_row_length = 10
        padding_width = (max_row_length - len(row_chars)) // 2
        if padding_width > 0:
            tk.Label(container_frame, text="", width=padding_width * 2, bg="#222222").pack(side="left")
        for char in row_chars:
            btn = ttk.Checkbutton(container_frame, text=char, variable=char_vars[char], style="Large.TCheckbutton")
            btn.pack(side="left", padx=5)
            Tooltip(btn, f"Exclude '{char}' from brute force")
        if row_idx == 4:
            container_frame.pack(padx=150)

    def toggle_numbers():
        all_numbers_selected = all(char_vars[char].get() for char in numbers)
        for char in numbers:
            char_vars[char].set(not all_numbers_selected)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'Selected' if not all_numbers_selected else 'Deselected'} all numbers (0-9)")

    def toggle_symbols():
        all_symbols_selected = all(char_vars[char].get() for char in symbols)
        for char in symbols:
            char_vars[char].set(not all_symbols_selected)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'Selected' if not all_symbols_selected else 'Deselected'} all symbols (_/)")

    def toggle_vowels():
        all_vowels_selected = all(char_vars[char].get() for char in vowels)
        for char in vowels:
            char_vars[char].set(not all_vowels_selected)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'Selected' if not all_vowels_selected else 'Deselected'} all vowels (aeiou)")

    def toggle_non_vowels():
        all_non_vowels_selected = all(char_vars[char].get() for char in non_vowels)
        for char in non_vowels:
            char_vars[char].set(not all_non_vowels_selected)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'Selected' if not all_non_vowels_selected else 'Deselected'} all non-vowel letters")

    def save_selection():
        selected_chars = [char for char, var in char_vars.items() if var.get()]
        if len(selected_chars) == len(characters):
            app.excluded_characters = []
            app.excluded_characters_label.config(text="Excluded Characters: None")
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] All characters selected for exclusion; reset to none")
        else:
            app.excluded_characters = selected_chars
            app.excluded_characters_label.config(text=f"Excluded Characters: {''.join(app.excluded_characters) if app.excluded_characters else 'None'}")
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Excluded characters: {''.join(app.excluded_characters) if app.excluded_characters else 'None'}")
        app.config_manager.save_brute_force_config(
            app.selected_algorithms,
            app.excluded_characters,
            last_string=app.last_hashed_string,
            disable_uncommon_combinations=app.disable_uncommon_combinations.get()
        )
        close_char_window(app, char_window)

    toggle_frame = tk.Frame(char_window, bg="#222222")
    toggle_frame.pack(pady=10)
    button_numbers = ttk.Button(toggle_frame, text="Toggle Numbers (0-9)", command=toggle_numbers)
    button_numbers.pack(pady=2)
    Tooltip(button_numbers, "Selects or deselects all numbers (0-9)")
    button_symbols = ttk.Button(toggle_frame, text="Toggle Symbols (_/)", command=toggle_symbols)
    button_symbols.pack(pady=2)
    Tooltip(button_symbols, "Selects or deselects all symbols (_/)")
    button_vowels = ttk.Button(toggle_frame, text="Toggle Vowels (aeiou)", command=toggle_vowels)
    button_vowels.pack(pady=2)
    Tooltip(button_vowels, "Selects or deselects all vowels (aeiou)")
    button_non_vowels = ttk.Button(toggle_frame, text="Toggle Non-Vowels", command=toggle_non_vowels)
    button_non_vowels.pack(pady=2)
    Tooltip(button_non_vowels, "Selects or deselects all non-vowel letters")

    button_frame = tk.Frame(char_window, bg="#222222")
    button_frame.pack(pady=10, anchor="center")
    save_button = ttk.Button(button_frame, text="Save", command=save_selection)
    save_button.pack(side="left", padx=10)
    cancel_button = ttk.Button(button_frame, text="Cancel", command=lambda: close_char_window(app, char_window))
    cancel_button.pack(side="left", padx=10)

    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Opened character exclusion window")

def close_char_window(app, window):
    app.is_char_window_open = False
    update_button_states(app)
    window.destroy()
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Closed character exclusion window")

def stop_brute_force(app):
    app.is_brute_force_running = False
    app.brute_force_stop = True
    last_string = getattr(app, 'last_hashed_string', None)
    app.current_string_label.config(text="Current String: None")
    app.custom_start_string_entry.configure(state="normal")
    if last_string:
        app.custom_start_string_entry.delete(0, tk.END)
        app.custom_start_string_entry.insert(0, last_string)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Updated Start String textbox with: {last_string}")
    else:
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No last string available to update Start String textbox")
    app.config_manager.save_brute_force_config(
        app.selected_algorithms,
        app.excluded_characters,
        last_string=last_string,
        disable_uncommon_combinations=app.disable_uncommon_combinations.get()
    )
    update_button_states(app)
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force stopped, last string: {last_string or 'None'}")

def start_brute_force(app):
    if not app.selected_algorithms:
        messagebox.showwarning("No Hashing Algorithms Selected", "Please select at least one hashing algorithm.")
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force start attempt failed: No hashing algorithms selected")
        return

    all_chars = list("abcdefghijklmnopqrstuvwxyz0123456789_/")
    allowed_chars = [char for char in all_chars if char not in app.excluded_characters]
    if not allowed_chars:
        messagebox.showwarning("No Characters Available", "All characters are excluded. Please include at least one character.")
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force start attempt failed: No characters available")
        return

    algo_to_csvs = {
        "BO3 SCR": {
            "games": ["Black Ops 3"],
            "csvs": ["bo3_var.csv", "bo3_function.csv", "bo3_namespace.csv", "bo3_class.csv", "bo3_hash.csv"]
        },
        "BO4CW SCR": {
            "games": ["Black Ops 4", "Black Ops Cold War"],
            "csvs": [
                "bo4_var.csv", "bo4_function.csv", "bo4_namespace.csv", "bo4_class.csv", "bo4_event.csv",
                "bocw_var.csv", "bocw_function.csv", "bocw_namespace.csv", "bocw_class.csv", "bocw_event.csv"
            ]
        },
        "FNV1A 63": {
            "games": ["Black Ops 4", "Black Ops Cold War", "Modern Warfare III"],
            "csvs": [
                "bo4_hash.csv", "bo4_script.csv",
                "bocw_hash.csv", "bocw_script.csv",
                "mwiii_hash.csv"
            ]
        },
        "MWIII SCR": {
            "games": ["Modern Warfare III"],
            "csvs": ["mwiii_var.csv", "mwiii_function.csv", "mwiii_namespace.csv", "mwiii_andhash.csv"]
        },
        "IW Resources": {
            "games": ["Modern Warfare III", "Black Ops 6"],
            "csvs": [
                "mwiii_script.csv", "mwiii_rhash.csv", "mwiii_percenthash.csv",
                "bo6_script.csv", "bo6_rhash.csv", "bo6_percenthash.csv"
            ]
        },
        "IW Tag FNV32": {
            "games": ["Modern Warfare III", "Black Ops 6"],
            "csvs": ["mwiii_thash.csv", "bo6_thash.csv"]
        },
        "IW Dvars": {
            "games": ["Modern Warfare III", "Black Ops 6"],
            "csvs": ["mwiii_dvar.csv", "bo6_dvar.csv"]
        },
        "FNV1A 64": {
            "games": ["Black Ops 6"],
            "csvs": ["bo6_hash.csv"]
        },
        "BO6 SCR": {
            "games": ["Black Ops 6"],
            "csvs": ["bo6_var.csv", "bo6_function.csv", "bo6_namespace.csv", "bo6_andhash.csv"]
        },
        "BO6 SP SCR": {
            "games": ["Black Ops 6"],
            "csvs": ["bo6_andhash.csv"]
        },
        "BO6 Omnvars": {
            "games": ["Black Ops 6"],
            "csvs": ["bo6_omnvar.csv"]
        }
    }

    algo_no_csvs = []
    app.cached_hashes = set()
    root_folder = os.path.dirname(os.path.abspath(__file__)).rsplit('gui', 1)[0]
    for algo in app.selected_algorithms:
        found_csv = False
        if algo in algo_to_csvs:
            for game in algo_to_csvs[algo]['games']:
                game_folder = os.path.join(root_folder, game)
                if os.path.exists(game_folder):
                    for csv_name in algo_to_csvs[algo]['csvs']:
                        csv_path = os.path.join(game_folder, csv_name)
                        if os.path.exists(csv_path):
                            found_csv = True
                            try:
                                with open(csv_path, 'r', encoding='utf-8') as f:
                                    reader = csv.reader(f)
                                    header = next(reader, None)
                                    for row in reader:
                                        if row and row[0]:
                                            hash_value = row[0].lstrip('0') or '0'
                                            app.cached_hashes.add(hash_value)
                                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Cached {csv_name} for {algo} from {game_folder}")
                            except Exception as e:
                                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error reading {csv_name}: {str(e)}")
                        else:
                            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CSV not found: {csv_path}")
                else:
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Game folder not found: {game_folder}")
            if not found_csv:
                algo_no_csvs.append(algo)

    if algo_no_csvs and len(app.selected_algorithms) > 1:
        error_msg = f"No CSV files found for the following algorithms: {', '.join(algo_no_csvs)}."
        messagebox.showerror("Missing CSV Files", error_msg)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force start attempt failed: {error_msg}")
        return

    if not app.cached_hashes:
        error_msg = "No CSV files found for the selected algorithms."
        messagebox.showerror("No Hashes Found", error_msg)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force start attempt failed: {error_msg}")
        return

    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Total cached hashes: {len(app.cached_hashes)}")

    app.is_brute_force_running = True
    update_button_states(app)

    start_string = app.custom_start_string_entry.get().strip()
    app.last_hashed_string = start_string or ""
    if start_string:
        if not all(c in allowed_chars for c in start_string):
            messagebox.showwarning("Invalid Start String", "Start string contains excluded characters.")
            app.is_brute_force_running = False
            update_button_states(app)
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Brute force start attempt failed: Invalid start string")
            return
        start_length = len(start_string)
    else:
        start_length = 1

    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Started brute force with algorithms: {', '.join(app.selected_algorithms)}, allowed_chars: {''.join(allowed_chars)}, start_string: {start_string or 'None'}, uncommon_combinations filter: {'enabled' if app.disable_uncommon_combinations.get() else 'disabled'}")

    app.brute_force_length = start_length
    app.brute_force_iterator = itertools.product(allowed_chars, repeat=app.brute_force_length)
    app.brute_force_stop = False
    app.brute_force_started = True

    if start_string:
        try:
            for combo in app.brute_force_iterator:
                current_string = ''.join(combo)
                if current_string >= start_string:
                    app.brute_force_iterator = itertools.chain([combo], app.brute_force_iterator)
                    break
        except Exception as e:
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error advancing to start_string: {str(e)}")
            messagebox.showwarning("Invalid Start String", f"Start string {start_string} is beyond available combinations for length {start_length}.")
            app.is_brute_force_running = False
            update_button_states(app)
            return

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

    game_to_short = {
        "Black Ops 3": "BO3",
        "Black Ops 4": "BO4",
        "Black Ops Cold War": "BOCW",
        "Modern Warfare III": "MWIII",
        "Black Ops 6": "BO6"
    }

    def has_uncommon_combo(string: str) -> bool:
        for i in range(len(string) - 1):
            if not bad_letter_combo(string[i], string[i + 1]):
                return True
        return False

    def brute_force_step():
        if not app.is_brute_force_running or app.brute_force_stop:
            stop_brute_force(app)
            return

        try:
            current_string = ''.join(next(app.brute_force_iterator))
            app.current_string_label.config(text=f"Current String: {current_string}")
            app.last_hashed_string = current_string
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Set last_hashed_string to: {current_string}")
            app.root.update()

            if app.disable_uncommon_combinations.get() and has_uncommon_combo(current_string):
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Skipped {current_string} due to uncommon letter combinations")
                app.root.after(10, brute_force_step)
                return

            for algo in app.selected_algorithms:
                if algo in algo_to_func:
                    hash_func = algo_to_func[algo]
                    hash_value = hex(hash_func(current_string))[2:]
                    if algo in ["FNV1A 63", "FNV1A 64", "BO6 SCR", "BO6 SP SCR", "IW Resources", "IW Dvars", "BO6 Omnvars"]:
                        hash_value = hash_value
                    else:
                        hash_value = hash_value.zfill(8)
                    hash_value = hash_value.lstrip('0') or '0'
                    if hash_value in app.cached_hashes:
                        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Match found for {algo}: {current_string} -> {hash_value}")
                        datatype = algo_to_datatype.get(algo, "unknown")
                        for game in algo_to_csvs[algo]["games"]:
                            short_name = game_to_short.get(game, game)
                            game_folder = os.path.join(root_folder, game)
                            if os.path.exists(game_folder):
                                found_csv = os.path.join(game_folder, f"{datatype}_found.csv")
                                file_exists = os.path.exists(found_csv)
                                try:
                                    with open(found_csv, 'a', newline='', encoding='utf-8') as f:
                                        writer = csv.writer(f)
                                        if not file_exists:
                                            writer.writerow(["hash", "data"])
                                        writer.writerow([hash_value, current_string])
                                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Saved match to {found_csv}")
                                    logging.info(f"Match found for {algo} in {game}: String='{current_string}', Hash='{hash_value}'")
                                except Exception as e:
                                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error writing to {found_csv}: {str(e)}")

            app.root.after(10, brute_force_step)

        except StopIteration:
            max_length = 20
            if app.brute_force_length >= max_length:
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Reached maximum length {max_length}, stopping brute force")
                logging.info(f"Reached maximum length: {max_length}, stopping brute force")
                stop_brute_force(app)
                return

            app.brute_force_length += 1
            log_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Moving to next length: {app.brute_force_length}"
            app.log_queue.put(log_message)
            logging.info(f"Moving to next length: {app.brute_force_length}")
            app.brute_force_iterator = itertools.product(allowed_chars, repeat=app.brute_force_length)
            app.brute_force_started = True
            app.root.after(10, brute_force_step)
        except Exception as e:
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error in brute force step: {str(e)}")
            stop_brute_force(app)
            return

    app.root.after(10, brute_force_step)

def setup_brute_force_tab(app, tab):
    frame = tk.Frame(tab, bg="#222222")
    frame.pack(pady=10, padx=10, fill="both", expand=True)

    app.is_char_window_open = False
    app.is_brute_force_running = False

    config = app.config_manager.load_config()
    app.selected_algorithms = config.get('selected_algorithms', [])
    app.excluded_characters = config.get('excluded_characters', [])
    app.last_hashed_string = config.get('last_hashed_string', None)
    app.disable_uncommon_combinations = tk.BooleanVar(value=config.get('disable_uncommon_combinations', False))

    left_frame = tk.Frame(frame, bg="#222222")
    left_frame.pack(side="left", padx=10, fill="y")

    app.algo_frame = tk.Frame(left_frame, bg="#222222")
    app.algo_frame.pack(anchor="nw")

    hash_types = [
        "BO3 SCR", "BO4CW SCR", "FNV1A 63", "MWIII SCR", "IW Resources",
        "IW Tag FNV32", "IW Dvars", "FNV1A 64", "BO6 SCR", "BO6 SP SCR", "BO6 Omnvars"
    ]
    game_to_algorithms = {
        "Black Ops 3": ["BO3 SCR"],
        "Black Ops 4/Cold War": ["BO4CW SCR", "FNV1A 63"],
        "Modern Warfare III": ["MWIII SCR", "FNV1A 63", "IW Resources", "IW Dvars", "IW Tag FNV32"],
        "Black Ops 6": ["BO6 SCR", "BO6 SP SCR", "FNV1A 64", "IW Resources", "IW Dvars", "BO6 Omnvars", "IW Tag FNV32"]
    }

    listbox_frame = ttk.Frame(app.algo_frame, relief="groove", borderwidth=2)
    listbox_frame.pack(anchor="nw")
    listbox_width = 35
    app.algo_listbox = tk.Listbox(
        listbox_frame,
        selectmode="multiple",
        height=min(len(hash_types), 11),
        width=listbox_width,
        bg="#333333",
        fg="#E07B00",
        selectbackground="#B0B0B0",
        selectforeground="#E07B00",
        font=("Courier", 10))
    for hash_type in hash_types:
        padding = (listbox_width - len(hash_type)) // 2
        centered_text = " " * padding + hash_type + " " * (listbox_width - len(hash_type) - padding)
        app.algo_listbox.insert(tk.END, centered_text)
    app.algo_listbox.pack(padx=5, pady=5)

    for algo in app.selected_algorithms:
        try:
            index = hash_types.index(algo)
            app.algo_listbox.selection_set(index)
        except ValueError:
            pass

    app.algo_listbox.bind('<<ListboxSelect>>', lambda event: save_algorithm_selection(app, hash_types))

    app.toggle_frame = tk.Frame(app.algo_frame, bg="#222222")
    app.toggle_frame.pack(anchor="nw", pady=5)
    style = ttk.Style()
    style.configure("Small.TButton", font=("TkDefaultFont", 7), padding=1)
    for game in game_to_algorithms:
        button = ttk.Button(app.toggle_frame, text=game, command=lambda g=game: toggle_game_algorithms(app, g, hash_types), style="Small.TButton")
        button.pack(side="left", padx=1)
        Tooltip(button, f"Selects or deselects all algorithms for {game}")

    algorithms_text = format_algorithms_text(app.selected_algorithms, hash_types)
    app.selected_algorithms_label = ttk.Label(left_frame, text=f"Selected Algorithms: {algorithms_text}", background="#222222", foreground="#E07B00")
    app.selected_algorithms_label.pack(pady=5, anchor="w")

    app.select_characters_button = ttk.Button(left_frame, text="Select Characters to Exclude", command=lambda: open_character_selection(app))
    app.select_characters_button.pack(pady=10, anchor="w")

    app.excluded_characters_label = ttk.Label(left_frame, text=f"Excluded Characters: {''.join(app.excluded_characters) if app.excluded_characters else 'None'}", background="#222222", foreground="#E07B00")
    app.excluded_characters_label.pack(pady=5, anchor="w")

    reset_button = ttk.Button(left_frame, text="Reset Selections", command=lambda: reset_selections(app))
    reset_button.pack(anchor="w", pady=10)

    right_frame = tk.Frame(frame, bg="#222222")
    right_frame.pack(side="left", padx=10, fill="y")

    custom_string_frame = tk.Frame(right_frame, bg="#222222")
    custom_string_frame.pack(anchor="w", pady=5)
    ttk.Label(custom_string_frame, text="Start String:", background="#222222", foreground="#E07B00").pack(side="left")
    app.custom_start_string_entry = ttk.Entry(custom_string_frame, width=20)
    app.custom_start_string_entry.pack(side="left", padx=5)
    Tooltip(app.custom_start_string_entry, "Enter a custom string to start brute force from")

    if app.last_hashed_string:
        app.custom_start_string_entry.insert(0, app.last_hashed_string)

    app.current_string_label = ttk.Label(right_frame, text="Current String: None", background="#222222", foreground="#E07B00")
    app.current_string_label.pack(anchor="w", pady=5)

    app.brute_force_button = ttk.Button(right_frame, text="Start Brute Force", command=lambda: start_brute_force(app))
    app.brute_force_button.pack(anchor="w", pady=10)

    app.disable_uncommon_combinations_check = ttk.Checkbutton(
        right_frame,
        text="Disable Uncommon Letter Combinations",
        variable=app.disable_uncommon_combinations,
        command=lambda: app.config_manager.save_brute_force_config(
            app.selected_algorithms,
            app.excluded_characters,
            last_string=app.last_hashed_string,
            disable_uncommon_combinations=app.disable_uncommon_combinations.get()
        )
    )
    app.disable_uncommon_combinations_check.pack(anchor="w", pady=5)
    Tooltip(app.disable_uncommon_combinations_check, "Skips strings with uncommon letter pairs (e.g., 'bb', 'cc') when enabled")

    update_button_states(app)
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Initialized Brute Force tab")