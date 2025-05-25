import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import glob
import fnmatch
import csv
import re

def setup_game_extract_tab(app, tab):
    frame = tk.Frame(tab, **app.frame_style)
    frame.pack(pady=10, padx=10, fill="both", expand=True)
    ttk.Label(frame, text="Select Scripts Folder:", background="#222222", foreground="#E07B00", font=("TkDefaultFont", 14, "bold")).pack(pady=5)
    app.folder_entry = tk.Entry(frame, textvariable=app.folder_path, width=50,
                                fg="#E07B00", bg="#333333",
                                selectbackground="#FFD700", selectforeground="#E07B00")
    app.folder_entry.pack(pady=5)
    app.browse_button = ttk.Button(frame, text="Browse", command=app.select_folder, style="TButton")
    app.browse_button.pack(pady=5)
    app.game_label = ttk.Label(frame, text=f"Game: {app.detected_game}", style="TLabel", font=("TkDefaultFont", 16, "bold"))
    app.game_label.pack(pady=10)
    app.extract_button = ttk.Button(frame, text="Extract Scripts Data", command=app.run_extraction, style="TButton")
    app.extract_button.pack(pady=5)
    app.progress_bar = ttk.Progressbar(frame, variable=app.progress, maximum=100)
    app.progress_bar.pack(fill="x", pady=5)
    app.result_label = ttk.Label(frame, text="", style="TLabel", foreground="#FFFFFF")
    app.result_label.pack(pady=10)
    app.status_label = ttk.Label(frame, text="", background="#222222", foreground="#00FF00")
    app.status_label.pack(pady=5)

    # Initialize CSV selection UI
    setup_csv_selection_ui(app, frame)

def setup_csv_selection_ui(app, parent, csv_list=None, game_short_name=None, output_dir=None):
    # Destroy existing csv_frame if it exists
    if hasattr(app, 'csv_frame'):
        app.csv_frame.destroy()

    # Create new csv_frame
    app.csv_frame = tk.Frame(parent, bg="#222222")
    app.csv_frame.pack(fill="both", expand=True, pady=5)
    if not hasattr(app, 'selected_csvs'):
        app.selected_csvs = []  # Initialize if not exists

    # Define styles for CSV buttons
    style = ttk.Style()
    style.configure("Selected.TButton", bordercolor="#E07B00", highlightcolor="#E07B00", highlightthickness=4, 
                    background="#FFD700", font=("TkDefaultFont", 9, "bold"))
    style.map("Selected.TButton", 
              bordercolor=[('pressed', '#E07B00'), ('active', '#E07B00')],
              highlightcolor=[('pressed', '#E07B00'), ('active', '#E07B00')])
    style.configure("Unavailable.TButton", background="#555555", foreground="#FFFFFF")
    style.configure("NoGame.TButton", background="#888888", foreground="#FFFFFF")
    style.configure("Sort.TButton", font=("TkDefaultFont", 10, "bold"))
    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Configured Selected.TButton with bordercolor=#E07B00")

    # Initialize with detected game
    if csv_list is None or game_short_name is None or output_dir is None:
        game_info = {
            'Black Ops 3': 'bo3',
            'Black Ops 4': 'bo4',
            'Black Ops Cold War': 'bocw',
            'Modern Warfare III': 'mwiii',
            'Black Ops 6': 'bo6'
        }
        if app.detected_game != "Unknown":
            game_short_name = game_info.get(app.detected_game, 'unknown')
            patterns = ['var', 'function', 'namespace', 'class', 'event', 'script', 'hash', 'rhash', 'percenthash', 'andhash', 'thash', 'dvar', 'omnvar']
            possible_csvs = [f"{game_short_name}_{pattern}.csv" for pattern in patterns]
            possible_csvs.extend([f"{game_short_name}.csv", f"{game_short_name}_dictionary.csv"])

            # Check for existing CSVs in root_folder/game_full_name
            output_dir = os.path.normpath(os.path.join(app.root_folder, app.detected_game))
            existing_csvs = []
            if os.path.exists(output_dir):
                csv_pattern = os.path.join(output_dir, f"{game_short_name}*.csv")
                existing_csvs = [os.path.basename(f) for f in glob.glob(csv_pattern, recursive=False)]
                if existing_csvs:
                    possible_csvs = existing_csvs
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Found existing CSVs: {', '.join(existing_csvs)}")
                else:
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No existing CSVs found in {output_dir}")
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Folder contents: {os.listdir(output_dir)}")
            else:
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Game folder does not exist: {output_dir}")
            csv_list = possible_csvs
        else:
            csv_list = ["placeholder.csv"]
            output_dir = ""
            game_short_name = "unknown"
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No game detected, using placeholder CSV buttons")

    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Initializing CSV buttons for game: {app.detected_game}, CSV count: {len(csv_list)}")

    # Sort and Check buttons
    def sort_selected_csvs():
        if not app.selected_csvs:
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No CSVs selected to sort")
            return
        game_info = {
            'Black Ops 3': 'bo3',
            'Black Ops 4': 'bo4',
            'Black Ops Cold War': 'bocw',
            'Modern Warfare III': 'mwiii',
            'Black Ops 6': 'bo6'
        }
        game_short_name = game_info.get(app.detected_game, 'unknown')
        output_dir = os.path.normpath(os.path.join(app.root_folder, app.detected_game))
        
        for csv_name in app.selected_csvs:
            csv_path = os.path.join(output_dir, csv_name)
            if not os.path.exists(csv_path):
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CSV not found: {csv_path}")
                continue
            try:
                # Read CSV
                with open(csv_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    rows = [row for row in reader if row]
                if not rows:
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] CSV is empty: {csv_name}")
                    continue
                # Remove duplicates and sort
                unique_rows = list(dict.fromkeys([tuple(row) for row in rows]))
                is_dictionary = '_dictionary' in csv_name.lower() or header == ['Word']
                if is_dictionary:
                    sorted_rows = sorted(unique_rows, key=lambda x: x[0].lower())
                    sort_method = "lexicographical"
                else:
                    sorted_rows = sorted(unique_rows, key=lambda x: int(x[0].zfill(16), 16))
                    sort_method = "numerical"
                duplicates_removed = len(rows) - len(unique_rows)
                # Log first few sorted rows
                sample_rows = sorted_rows[:3]
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sorted {csv_name} ({sort_method}): Sample rows: {sample_rows}")
                # Write back to CSV
                with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    if header:
                        writer.writerow(header)
                    writer.writerows(sorted_rows)
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Sorted CSV: {csv_name}, removed {duplicates_removed} duplicates")
            except Exception as e:
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error sorting CSV {csv_name}: {str(e)}")
        
        # Refresh UI
        setup_csv_selection_ui(app, parent, csv_list, game_short_name, output_dir)
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Refreshed CSV UI after sorting")

    def check_manual_csvs():
        if not app.folder_path.get():
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No folder selected for CSV check")
            return
        output_dir = os.path.normpath(os.path.join(app.root_folder, app.detected_game))
        if not os.path.exists(output_dir):
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Game folder not found: {output_dir}")
            return
        csv_pattern = os.path.join(output_dir, f"{game_short_name}*.csv")
        found_csvs = []
        for f in glob.glob(csv_pattern, recursive=False):
            if fnmatch.fnmatch(os.path.basename(f).lower(), f"{game_short_name}*.csv"):
                found_csvs.append(os.path.basename(f))
        if found_csvs:
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Manually found CSVs: {', '.join(found_csvs)}")
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Folder contents: {os.listdir(output_dir)}")
            setup_csv_selection_ui(app, parent, found_csvs, game_short_name, output_dir)
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Recreated CSV selection UI with Sort and Check buttons")
        else:
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No CSVs found in {output_dir}")
        app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Root folder subfolders: {os.listdir(app.root_folder)}")

    # Create sort_frame and buttons
    sort_frame = tk.Frame(app.csv_frame, bg="#222222")
    sort_frame.pack(anchor="center", pady=10)
    button_container = tk.Frame(sort_frame, bg="#222222")
    button_container.pack()
    sort_button = ttk.Button(button_container, text="Sort Selected CSVs", command=sort_selected_csvs, style="Sort.TButton", width=20)
    sort_button.pack(side="left", padx=5)
    check_button = ttk.Button(button_container, text="Check CSVs", command=check_manual_csvs, style="TButton", width=15)
    check_button.pack(side="left", padx=5)

    # CSV buttons in grid layout
    def setup_csv_buttons(app, parent, csv_list, game_short_name, output_dir):
        button_frame = tk.Frame(parent, bg="#222222")
        button_frame.pack(fill="both", expand=True)
        def toggle_csv_selection(csv_name, button):
            csv_path = os.path.normpath(os.path.join(output_dir, csv_name)) if output_dir else ""
            is_available = False
            if output_dir and os.path.exists(output_dir):
                for f in glob.glob(os.path.join(output_dir, f"{game_short_name}*.csv")):
                    if fnmatch.fnmatch(os.path.basename(f).lower(), csv_name.lower()):
                        is_available = True
                        csv_path = f
                        break
                if not is_available:
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Folder contents: {os.listdir(output_dir)}")
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Root folder subfolders: {os.listdir(app.root_folder)}")
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking CSV: {csv_name}, Path: {csv_path}, Exists: {is_available}")
            if csv_name in app.selected_csvs:
                app.selected_csvs.remove(csv_name)
                button.configure(style="TButton" if is_available else "Unavailable.TButton")
                app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Deselected CSV: {csv_name}, style: {'TButton' if is_available else 'Unavailable.TButton'}")
            else:
                if is_available:
                    if csv_name not in app.selected_csvs:
                        app.selected_csvs.append(csv_name)
                    button.configure(style="Selected.TButton")
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Selected CSV: {csv_name}, style: Selected.TButton")
                else:
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Cannot select unavailable CSV: {csv_name}")
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Current selected CSVs: {', '.join(app.selected_csvs) if app.selected_csvs else 'None'}")

        max_per_column = 3
        use_nogame_style = app.detected_game == "Unknown"
        for i, csv_name in enumerate(csv_list):
            column = i // max_per_column
            row = i % max_per_column
            csv_path = os.path.normpath(os.path.join(output_dir, csv_name)) if output_dir else ""
            is_available = False
            if output_dir and os.path.exists(output_dir):
                for f in glob.glob(os.path.join(output_dir, f"{game_short_name}*.csv")):
                    if fnmatch.fnmatch(os.path.basename(f).lower(), csv_name.lower()):
                        is_available = True
                        break
                if not is_available:
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Folder contents: {os.listdir(output_dir)}")
                    app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Root folder subfolders: {os.listdir(app.root_folder)}")
            initial_style = "NoGame.TButton" if use_nogame_style else ("Selected.TButton" if csv_name in app.selected_csvs else ("TButton" if is_available else "Unavailable.TButton"))
            button = ttk.Button(button_frame, text=csv_name, style=initial_style)
            button.configure(command=lambda b=button, name=csv_name: toggle_csv_selection(name, b))
            button.grid(row=row, column=column, sticky="ew", pady=5, padx=5)
            app.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Created button for {csv_name}, initial style: {initial_style}")
        for col in range((len(csv_list) + max_per_column - 1) // max_per_column):
            button_frame.grid_columnconfigure(col, weight=1)

    setup_csv_buttons(app, app.csv_frame, csv_list, game_short_name, output_dir)

def setup_hash_tab(app, tab):
    frame = tk.Frame(tab, **app.frame_style)
    frame.pack(pady=10, padx=10, fill="both", expand=True)
    ttk.Label(frame, text="Enter String to Hash:", background="#222222", foreground="#E07B00").pack(pady=5)
    app.hash_input = tk.Entry(frame, width=30,
                              fg="#E07B00", bg="#333333",
                              selectbackground="#FFD700", selectforeground="#E07B00")
    app.hash_input.pack(pady=5)
    app.hash_input.bind("<KeyRelease>", lambda event: app.update_hash_results(event))
    tree_frame = tk.Frame(frame, **app.frame_style)
    tree_frame.pack(fill="both", expand=True, pady=5)
    app.hash_tree = ttk.Treeview(tree_frame, columns=("Type", "Hash", "String", "CopyButton"), show="headings", height=10)
    app.hash_tree.heading("Type", text="Hash Type")
    app.hash_tree.heading("Hash", text="Hash Value")
    app.hash_tree.heading("String", text="Unhashed String")
    app.hash_tree.heading("CopyButton", text="")
    app.hash_tree.column("Type", width=120, anchor=tk.CENTER, stretch=tk.NO)
    app.hash_tree.column("Hash", width=200, anchor=tk.CENTER)
    app.hash_tree.column("String", width=200, anchor=tk.CENTER)
    app.hash_tree.column("CopyButton", width=60, anchor=tk.CENTER, stretch=tk.NO)
    app.hash_tree.pack(fill="both", expand=True)
    app.hash_tree.bind("<Button-1>", app.on_treeview_click)
    app.hash_values = {}
    app.update_hash_results()