import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime
from config_manager import ConfigManager
from script_processor import ScriptProcessor
from game_detector import detect_game, get_default_hash_function, get_game_specific_hashes, get_all_hashes
from gui_tabs import setup_game_extract_tab, setup_hash_tab
from gui_utils import update_console, load_log_contents, update_game_label, copy_to_clipboard
import threading
import queue

class WordExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Call of Duty Script Manager (UI Beta)")
        self.root.geometry("800x600")
        self.root.configure(bg="#FF8C00")

        self.folder_path = tk.StringVar()
        self.detected_game = "Unknown"
        self.last_execution = 0
        self.cooldown_period = 2
        self.progress = tk.DoubleVar(value=0)
        self.is_processing = False
        self.result_queue = queue.Queue()

        self.processor = ScriptProcessor(log_callback=lambda msg: update_console(self, msg), progress_var=self.progress)
        self.config_manager = ConfigManager()

        self.button_style = {
            "bg": "#D3D3D3", "fg": "#000000",
            "activebackground": "#B0B0B0", "activeforeground": "#000000",
            "bd": 0
        }
        self.frame_style = {
            "bg": "#222222",
            "highlightbackground": "#FF8C00",
            "highlightthickness": 2,
            "bd": 0
        }
        self.label_style = {
            "bg": "#222222",
            "fg": "#000000",
            "bd": 2,
            "relief": "solid",
            "highlightbackground": "#FF8C00",
            "highlightthickness": 2
        }
        self.no_border_label_style = {
            "bg": "#222222",
            "fg": "#FF8C00",
            "font": ("TkDefaultFont", 20)
        }

        self.create_gui()

    def create_gui(self):
        content_frame = tk.Frame(self.root, bg="#222222")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        style = ttk.Style()
        style.configure("TNotebook", background="#222222")
        style.configure("TNotebook.Tab", background="#D3D3D3", foreground="#000000", padding=[10, 5], borderwidth=2)
        style.map("TNotebook.Tab",
                  background=[("selected", "#B0B0B0"), ("active", "#C0C0C0")],
                  foreground=[("selected", "#FF8C00"), ("active", "#000000")],
                  relief=[("selected", "solid")])
        style.configure("Treeview", background="#D3D3D3", fieldbackground="#D3D3D3", foreground="#000000")
        style.configure("Treeview.Heading", background="#D3D3D3", foreground="#000000")
        style.map("Treeview", background=[("selected", "#B0B0B0"), ("!selected", "#D3D3D3")])

        notebook = ttk.Notebook(content_frame, style="TNotebook")
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        game_extract_tab = tk.Frame(notebook, bg="#222222", highlightbackground="#FF8C00", highlightthickness=2)
        notebook.add(game_extract_tab, text="Game & Extraction")
        setup_game_extract_tab(self, game_extract_tab)

        hash_tab = tk.Frame(notebook, bg="#222222", highlightbackground="#FF8C00", highlightthickness=2)
        notebook.add(hash_tab, text="Hash Display")
        setup_hash_tab(self, hash_tab)

        console_frame = ttk.Frame(content_frame, style="TFrame")
        console_frame.pack(fill="both", padx=10, pady=5)
        ttk.Label(console_frame, text="Log Console:", background="#3C3C3C", foreground="#000000").pack(anchor="w")
        console_inner_frame = ttk.Frame(console_frame, style="TFrame")
        console_inner_frame.pack(fill="both", expand=True)
        self.console_text = tk.Text(
            console_inner_frame, height=6, bg="#3C3C3C", fg="#FFFFFF",
            wrap=tk.WORD, state="disabled"
        )
        self.console_text.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar = ttk.Scrollbar(
            console_inner_frame, orient=tk.VERTICAL, command=self.console_text.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_text.config(yscrollcommand=scrollbar.set)

        load_log_contents(self)

        last_folder = self.config_manager.get_folder()
        if last_folder and os.path.exists(last_folder):
            self.folder_path.set(last_folder)
            self.detected_game = detect_game(last_folder)
            self.processor.log_action(f"Initial folder loaded: {last_folder}, Detected game: {self.detected_game}")
            update_game_label(self)

    def update_hash_results(self, event=None):
        for item in self.hash_tree.get_children():
            self.hash_tree.delete(item)
        input_text = self.hash_input.get().strip()
        if input_text:
            hash_results = get_all_hashes(input_text)
            for label, hash_value in hash_results:
                self.hash_tree.insert("", "end", values=(label, hash_value, input_text))
        else:
            dummy_results = get_all_hashes("dummy")
            hash_types = [label for label, _ in dummy_results]
            for label in hash_types:
                self.hash_tree.insert("", "end", values=(label, "", ""))

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:  # Only update if a folder was selected
            self.folder_path.set(folder)
            self.config_manager.save_config(folder)
            self.detected_game = detect_game(folder)
            self.processor.log_action(f"New folder selected: {folder}, Detected game: {self.detected_game}")
            update_game_label(self)
            self.update_hash_results()
            load_log_contents(self)

    def extract_words_wrapper(self):
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_execution

        if time_since_last < self.cooldown_period:
            remaining = self.cooldown_period - time_since_last
            self.status_label.config(text=f"Please wait {remaining:.1f} seconds...", foreground="#FF0000")
            self.extract_button.config(state="disabled")
            self.browse_button.config(state="disabled")
            self.root.after(int(remaining * 1000), self.reset_cooldown)
            return

        self.last_execution = current_time
        self.extract_button.config(state="disabled")
        self.browse_button.config(state="disabled")
        self.status_label.config(text="Processing...", foreground="#FF0000")
        self.is_processing = True
        self.progress.set(0)
        self.root.after(100, self.extract_words)

    def reset_cooldown(self):
        self.extract_button.config(state="normal")
        self.browse_button.config(state="normal")
        self.status_label.config(text="Ready", foreground="#00FF00")
        load_log_contents(self)
        self.is_processing = False

    def extract_words(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first!")
            self.reset_cooldown()
            return

        thread = threading.Thread(
            target=self.processor.process_scripts,
            args=(folder, self.detected_game, self.result_queue)
        )
        thread.daemon = True
        thread.start()

        self.root.after(100, self.check_queue)

    def check_queue(self):
        try:
            total_words, unhashed_count, hashed_count = self.result_queue.get_nowait()
            self.result_label.config(
                text=f"Found {total_words} unique words ({unhashed_count} unhashed, {hashed_count} hashed)"
            )
            messagebox.showinfo(
                "Success", f"Words classified and saved in {self.processor.get_game_dir(self.detected_game)}"
            )
            self.reset_cooldown()
        except queue.Empty:
            if self.is_processing:
                self.root.after(100, self.check_queue)
            else:
                self.reset_cooldown()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.processor.log_action(f"Extraction failed: {str(e)}")
            self.reset_cooldown()

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.configure("TButton", background="#D3D3D3", foreground="#000000", padding=5)
    style.configure("TLabel", background="#222222", foreground="#000000", padding=5)
    style.configure("TFrame", background="#222222")
    app = WordExtractorApp(root)
    root.mainloop()