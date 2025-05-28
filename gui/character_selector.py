import tkinter as tk
from tkinter import ttk
from datetime import datetime
from .utils import Tooltip

def open_character_selection(app):
    if app.is_char_window_open.get():
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Character exclusion window already open")
        return

    app.is_char_window_open.set(True)
    app.update_button_states()

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
    window_width = min(800, max_width)
    window_height = min(600, max_height)
    char_window.geometry(f"{window_width}x{window_height}")

    label = ttk.Label(char_window, text="Select Characters to Exclude:", background="#222222", foreground="#E07B00", font=("Arial", 14, "bold"))
    label.pack(pady=10)

    keyboard_frame = tk.Frame(char_window, bg="#222222")
    keyboard_frame.pack(pady=10)

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
        container_frame.pack()
        max_row_length = 10
        padding_width = (max_row_length - len(row_chars)) // 2
        if padding_width > 0:
            tk.Label(container_frame, text="", width=padding_width * 2, bg="#222222").pack(side="left")
        for char in row_chars:
            btn = ttk.Checkbutton(container_frame, text=char, variable=char_vars[char], style="Large.TCheckbutton")
            btn.pack(side="left", padx=5)
            Tooltip(btn, f"Exclude '{char}'")
        if row_idx == 4:
            container_frame.pack(padx=150)

    def toggle_numbers():
        state = not all(char_vars[char].get() for char in numbers)
        for char in numbers:
            char_vars[char].set(state)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'Selected' if state else 'Deselected'} numbers (0-9)")

    def toggle_symbols():
        state = not all(char_vars[char].get() for char in symbols)
        for char in symbols:
            char_vars[char].set(state)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'Selected' if state else 'Deselected'} symbols (_/)")

    def toggle_vowels():
        state = not all(char_vars[char].get() for char in vowels)
        for char in vowels:
            char_vars[char].set(state)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'Selected' if state else 'Deselected'} vowels (aeiou)")

    def toggle_non_vowels():
        state = not all(char_vars[char].get() for char in non_vowels)
        for char in non_vowels:
            char_vars[char].set(state)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {'Selected' if state else 'Deselected'} non-vowel letters")

    def save_selection():
        selected_chars = [char for char, var in char_vars.items() if var.get()]
        app.excluded_characters = [] if len(selected_chars) == len(characters) else selected_chars
        app.excluded_characters_label.config(text=f"Excluded Characters: {''.join(app.excluded_characters) or 'None'}")
        app.config_manager.save_brute_force_config(
            selected_algorithms=app.selected_algorithms,
            excluded_characters=app.excluded_characters,
            last_string=app.last_hashed_string,
            disable_uncommon_combinations=app.disable_uncommon_combinations.get(),
            require_vowel=app.require_vowel.get(),
            no_consecutive_symbols=app.no_consecutive_symbols.get(),
            no_triple_rule=app.no_triple_rule.get(),
            no_four_vowels=app.no_four_vowels.get()
        )
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Excluded characters: {''.join(app.excluded_characters) or 'None'}")
        close_char_window(app, char_window)

    toggle_frame = tk.Frame(char_window, bg="#222222")
    toggle_frame.pack(pady=10)
    ttk.Button(toggle_frame, text="Toggle Numbers (0-9)", command=toggle_numbers).pack(pady=2)
    ttk.Button(toggle_frame, text="Toggle Symbols (_/)", command=toggle_symbols).pack(pady=2)
    ttk.Button(toggle_frame, text="Toggle Vowels (aeiou)", command=toggle_vowels).pack(pady=2)
    ttk.Button(toggle_frame, text="Toggle Non-Vowels", command=toggle_non_vowels).pack(pady=2)

    button_frame = tk.Frame(char_window, bg="#222222")
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="Save", command=save_selection).pack(side="left", padx=10)
    ttk.Button(button_frame, text="Cancel", command=lambda: close_char_window(app, char_window)).pack(side="left", padx=10)

    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Opened character exclusion window")

def close_char_window(app, window):
    app.is_char_window_open.set(False)
    app.update_button_states()
    window.destroy()
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Closed character exclusion window")