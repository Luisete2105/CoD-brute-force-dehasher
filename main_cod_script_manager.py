import tkinter as tk
from tkinter import ttk, filedialog
import os
import multiprocessing as mp
import queue
from datetime import datetime
from utils.config_manager import ConfigManager
from core.script_processor import ScriptProcessor
from core.game_detector import detect_game, get_all_hashes
from gui.gui_tabs import setup_game_extract_tab, setup_hash_tab, setup_csv_selection_ui
from gui.brute_force_manager import setup_brute_force_tab
from utils.gui_utils import update_console, load_log_contents, update_game_label, copy_to_clipboard
from gui.extraction_manager import ExtractionManager


class CodScriptManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Call of Duty Script Manager (UI Beta)")
        self.root.geometry("800x600")
        self.root.configure(bg="#E07B00")

        self.root_folder = os.path.dirname(os.path.abspath(__file__))
        self.folder_path = tk.StringVar()
        self.detected_game = "Unknown"
        self.progress = tk.DoubleVar(value=0)
        self.is_processing = False
        manager = mp.Manager()
        self.result_queue = manager.Queue()
        self.progress_queue = manager.Queue()
        self.log_queue = manager.Queue()

        self.processor = ScriptProcessor(
            log_file_path=os.path.join(self.root_folder, "debug.log"),
            progress_queue=self.progress_queue
        )
        self.config_manager = ConfigManager()
        self.extraction_manager = ExtractionManager(self.log_queue, self.progress_queue)

        # Load last folder and brute force settings
        last_folder = self.config_manager.get_folder()
        if last_folder and os.path.exists(last_folder):
            self.folder_path.set(last_folder)
            self.detected_game = detect_game(last_folder)
            self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loaded last folder from config.json: {last_folder}\nDetected game: {self.detected_game}")

        # Initialize brute force settings
        self.selected_algorithms, self.excluded_characters = self.config_manager.get_brute_force_config()
        self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Loaded brute force settings: Algorithms={self.selected_algorithms}, Excluded Characters={''.join(self.excluded_characters)}")

        self.button_style = {
            "bg": "#D3D3D3", "fg": "#000000",
            "activebackground": "#B0B0B0", "activeforeground": "#000000",
            "bd": 0
        }
        self.frame_style = {
            "bg": "#222222",
            "highlightbackground": "#E07B00",
            "highlightcolor": "#E07B00",
            "highlightthickness": 2,
            "bd": 0,
            "relief": "solid"
        }
        self.label_style = {
            "bg": "#222222",
            "fg": "#000000",
            "bd": 2,
            "relief": "solid",
            "highlightbackground": "#E07B00",
            "highlightthickness": 2
        }
        self.no_border_label_style = {
            "bg": "#222222",
            "fg": "#E07B00",
            "font": ("TkDefaultFont", 20)
        }

        self.create_gui()
        self.update_button_states()
        self._check_queues()

    def create_gui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(pady=5, padx=10, expand=True, fill="both")

        self.game_frame = ttk.Frame(notebook, style="TFrame")
        hash_frame = ttk.Frame(notebook, style="TFrame")
        brute_force_frame = ttk.Frame(notebook, style="TFrame")

        notebook.add(self.game_frame, text="Game & Extraction")
        notebook.add(hash_frame, text="Hash Display")
        notebook.add(brute_force_frame, text="Brute Force")

        setup_game_extract_tab(self, self.game_frame)
        setup_hash_tab(self, hash_frame)
        setup_brute_force_tab(self, brute_force_frame)

        self.console_frame = tk.Frame(self.root, bg="#222222")
        self.console_frame.pack(fill="both", padx=10, pady=(5, 10), expand=True)
        self.console_text = tk.Text(self.console_frame, height=6, bg="#333333", fg="#FFFFFF", state="disabled")
        self.console_text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self.console_frame, orient="vertical", command=self.console_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.console_text.config(yscrollcommand=scrollbar.set)
        load_log_contents(self)

        style = ttk.Style()
        style.configure("TFrame", background="#222222", bordercolor="#E07B00", borderwidth=2, relief="solid")
        style.configure("TButton", background="#D3D3D3", foreground="#000000")
        style.configure("TLabel", background="#222222", foreground="#E07B00")
        style.configure("Custom.TEntry", 
                        fieldbackground="#333333", 
                        foreground="#E07B00", 
                        selectforeground="#E07B00", 
                        selectbackground="#FFD700")
        style.map("Custom.TEntry", 
                  foreground=[('active', '#E07B00'), ('focus', '#E07B00'), ('!focus', '#E07B00'), ('selected', '#E07B00'), ('disabled', '#E07B00')],
                  fieldbackground=[('active', '#333333'), ('focus', '#333333'), ('!focus', '#333333'), ('selected', '#333333'), ('disabled', '#333333')],
                  selectforeground=[('active', '#E07B00'), ('focus', '#E07B00'), ('!focus', '#E07B00'), ('selected', '#E07B00'), ('disabled', '#E07B00')],
                  selectbackground=[('active', '#FFD700'), ('focus', '#FFD700'), ('!focus', '#FFD700'), ('selected', '#FFD700'), ('disabled', '#FFD700')])
        style.configure("TProgressbar", troughcolor="#333333", background="#E07B00")
        style.configure("Treeview", background="#D3D3D3", fieldbackground="#D3D3D3")
        style.configure("Treeview.Heading", background="#B0B0B0", foreground="#000000")
        self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Configured Custom.TEntry with foreground=#E07B00, selectforeground=#E07B00, selectbackground=#FFD700 for all states")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.config_manager.save_folder(folder)
            self.detected_game = detect_game(folder)
            update_game_label(self)
            self.update_button_states()
            if hasattr(self, 'csv_frame'):
                setup_csv_selection_ui(self, self.game_frame)
            self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Folder selected: {folder}, Detected game: {self.detected_game}, CSV UI refreshed")

    def update_button_states(self):
        if self.is_processing:
            self.browse_button.config(state="disabled")
            self.extract_button.config(state="disabled")
        else:
            self.browse_button.config(state="normal")
            self.extract_button.config(state="normal" if self.detected_game != "Unknown" else "disabled")

    def refresh_csv_buttons(self):
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        setup_game_extract_tab(self, self.game_frame)
        self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Refreshed entire Game & Extraction tab after extraction")

    def _check_queues(self):
        try:
            while True:
                log_message = self.log_queue.get_nowait()
                update_console(self, log_message + "\n")
        except queue.Empty:
            pass

        try:
            while True:
                progress = self.progress_queue.get_nowait()
                self.progress.set(progress)
                self.progress_bar.update()
        except queue.Empty:
            pass

        was_processing = self.is_processing
        if self.extraction_manager.is_processing():
            self.is_processing = True
        else:
            self.is_processing = False
            if was_processing and not self.is_processing:
                self.refresh_csv_buttons()

        self.update_button_states()
        self.root.after(100, self._check_queues)

    def run_extraction(self):
        if self.is_processing:
            self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extraction already in progress")
            return

        folder = self.folder_path.get()
        if not folder:
            self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No folder selected")
            return

        self.progress.set(0)
        self.is_processing = True
        self.update_button_states()
        self.extraction_manager.start_extraction(folder, self.detected_game)

    def on_treeview_click(self, event):
        region = self.hash_tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        column = self.hash_tree.identify_column(event.x)
        if column != "#4":
            return
        item_id = self.hash_tree.identify_row(event.y)
        if item_id and item_id in self.hash_values:
            copy_to_clipboard(self, self.hash_values[item_id])
            self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Copied hash: {self.hash_values[item_id]}")

    def update_hash_results(self, event=None):
        input_text = self.hash_input.get().strip()
        processed_text = input_text.replace('\\', '/').replace(' ', '_')
        self.hash_tree.delete(*self.hash_tree.get_children())
        self.hash_values = {}
        hash_types = [
            "BO3 SCR", "BO4CW SCR", "FNV1A 63", "MWIII SCR", "IW Resources",
            "IW Tag FNV32", "IW Dvars", "FNV1A 64", "BO6 SCR", "BO6 SP SCR", "BO6 Omnvars"
        ]
        if processed_text:
            results = get_all_hashes(processed_text)
            self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Hash results count: {len(results)}, Results: {results}")
            result_dict = {label.strip(): hash_value for label, hash_value in results}
            for hash_type in hash_types:
                hash_value = result_dict.get(hash_type, f"mock_{hash_type}_{processed_text}")
                item_id = self.hash_tree.insert("", "end", values=(hash_type, hash_value, processed_text, "Copy"),
                                               tags=('row',))
                self.hash_values[item_id] = hash_value
        else:
            for hash_type in hash_types:
                self.hash_tree.insert("", "end", values=(hash_type, "", "", ""), tags=('row',))
        self.hash_tree.tag_configure('row', background="#D3D3D3")
        self.log_queue.put(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Updated hash results for: {processed_text or 'empty input'}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CodScriptManager(root)
    root.mainloop()