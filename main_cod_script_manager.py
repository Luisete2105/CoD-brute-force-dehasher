import tkinter as tk
from tkinter import filedialog, messagebox
import os
from datetime import datetime
from config_manager import ConfigManager
from script_processor import ScriptProcessor
from game_detector import detect_game, get_default_hash_function, get_game_specific_hashes, get_all_hashes

class WordExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Call of Duty Script Manager")
        self.root.geometry("800x600")

        self.root.configure(bg="#333333")

        self.folder_path = tk.StringVar()
        self.path_label = None
        self.detected_game = "Unknown"
        self.last_execution = 0
        self.cooldown_period = 2

        # Pass a callback to ScriptProcessor for real-time log updates
        self.processor = ScriptProcessor(log_callback=self.update_console)
        self.config_manager = ConfigManager()

        self.button_style = {
            "bg": "#333333", "fg": "white",
            "activebackground": "#444444", "activeforeground": "white",
            "bd": 0
        }

        self.frame_style = {
            "bg": "#333333",
            "highlightbackground": "#FF8C00",
            "highlightthickness": 2,
            "bd": 0
        }

        self.label_style = {
            "bg": "#333333",
            "fg": "white",
            "bd": 2,
            "relief": "solid",
            "highlightbackground": "#FF8C00",
            "highlightthickness": 2
        }

        self.no_border_label_style = {
            "bg": "#333333",
            "fg": "#FF8C00",
            "font": ("TkDefaultFont", 20)
        }

        # Main frame to hold left, right, and bottom sections
        self.main_frame = tk.Frame(self.root, bg="#333333")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left side: Existing UI elements
        self.left_frame = tk.Frame(self.main_frame, bg="#333333")
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.label = tk.Label(self.left_frame, text=f"Game: {self.detected_game}", **self.no_border_label_style)
        self.label.pack(pady=10)

        self.folder_frame = tk.Frame(self.left_frame, **self.frame_style)
        self.folder_frame.pack(pady=10)
        self.folder_button = tk.Button(self.folder_frame, text="Select Folder", command=self.select_folder, **self.button_style)
        self.folder_button.pack(padx=2, pady=2)

        self.extract_frame = tk.Frame(self.left_frame, **self.frame_style)
        self.extract_frame.pack(pady=10)
        self.extract_button = tk.Button(self.extract_frame, text="Extract Scripts Data", command=self.extract_words_wrapper, **self.button_style)
        self.extract_button.pack(padx=2, pady=2)

        self.path_label = None

        self.result_label = tk.Label(self.left_frame, text="", **self.label_style)
        self.result_label.pack(pady=10)

        self.status_label = tk.Label(self.left_frame, text="", bg="#333333", fg="white")
        self.status_label.pack(pady=5)

        # Right side: Hash input and results
        self.right_frame = tk.Frame(self.main_frame, bg="#333333")
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

        self.hash_input_frame = tk.Frame(self.right_frame, **self.frame_style)
        self.hash_input_frame.pack(pady=10)

        self.hash_input_label = tk.Label(self.hash_input_frame, text="Hash Input:", bg="#333333", fg="white")
        self.hash_input_label.pack(pady=2)

        self.hash_input = tk.Entry(self.hash_input_frame, width=30)
        self.hash_input.pack(padx=2, pady=2)
        self.hash_input.bind("<KeyRelease>", self.update_hash_results)

        # Hash results frame (no scrollbar)
        self.hash_results_frame = tk.Frame(self.right_frame, bg="#333333")
        self.hash_results_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.hash_labels = []  # To store hash labels and copy buttons

        # Bottom: Console display for logs
        self.console_frame = tk.Frame(self.main_frame, bg="#333333")
        self.console_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.console_label = tk.Label(self.console_frame, text="Log Console:", bg="#333333", fg="white")
        self.console_label.pack(anchor="w")

        self.console_inner_frame = tk.Frame(self.console_frame, bg="#333333")
        self.console_inner_frame.pack(fill=tk.BOTH, expand=True)

        self.console_text = tk.Text(
            self.console_inner_frame, height=6, bg="#222222", fg="white", 
            wrap=tk.WORD, state="disabled"
        )
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.console_scrollbar = tk.Scrollbar(
            self.console_inner_frame, orient=tk.VERTICAL, command=self.console_text.yview
        )
        self.console_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.console_text.config(yscrollcommand=self.console_scrollbar.set)

        # Configure grid weights for responsiveness
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=0)

        # Load the last folder and apply it
        last_folder = self.config_manager.get_folder()
        if last_folder and os.path.exists(last_folder):
            self.folder_path.set(last_folder)
            self.path_label = tk.Label(self.left_frame, textvariable=self.folder_path, wraplength=350, **self.label_style)
            self.path_label.pack(pady=10, before=self.extract_frame)
            self.detected_game = detect_game(last_folder)
            self.processor.log_action(f"Initial folder loaded: {last_folder}, Detected game: {self.detected_game}")
            self.update_game_label()

        # Load initial log contents
        self.load_log_contents()

        # Display hash labels even with no input
        self.update_hash_results()

    def update_console(self, log_message):
        """Callback to update the console Text widget with a new log message."""
        self.console_text.config(state="normal")
        self.console_text.insert(tk.END, log_message)
        self.console_text.config(state="disabled")
        self.console_text.see(tk.END)  # Scroll to the bottom
        self.root.update_idletasks()  # Ensure the UI updates immediately

    def load_log_contents(self):
        """Load and display the contents of script_manager.log in the console."""
        log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script_manager.log")
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                log_content = f.read()
            self.console_text.config(state="normal")
            self.console_text.delete(1.0, tk.END)
            self.console_text.insert(tk.END, log_content)
            self.console_text.config(state="disabled")
            self.console_text.see(tk.END)
        except Exception as e:
            self.console_text.config(state="normal")
            self.console_text.delete(1.0, tk.END)
            self.console_text.insert(tk.END, f"Error loading log: {str(e)}")
            self.console_text.config(state="disabled")

    def update_game_label(self):
        color = {
            "Black Ops 3": "#FFA500",
            "Black Ops 4": "#FFA500",
            "Black Ops 6": "#FFA500",
            "Black Ops Cold War": "white",
            "Modern Warfare III": "#90EE90"
        }.get(self.detected_game, "#FF8C00")
        self.label.config(text=f"Game: {self.detected_game}", fg=color)

    def update_hash_results(self, event=None):
        for widget in self.hash_results_frame.winfo_children():
            widget.destroy()
        self.hash_labels.clear()

        input_text = self.hash_input.get().strip()
        hash_results = get_all_hashes(input_text) if input_text else [(label, "N/A") for label, _ in get_all_hashes("dummy")]

        for label, hash_value in hash_results:
            hash_frame = tk.Frame(self.hash_results_frame, bg="#333333")
            hash_frame.pack(fill=tk.X, pady=2)

            hash_label = tk.Label(
                hash_frame,
                text=f"{label}: {hash_value}",
                bg="#333333",
                fg="white",
                anchor="w"
            )
            hash_label.pack(side=tk.LEFT, padx=5)

            copy_button = tk.Button(
                hash_frame,
                text="Copy",
                command=lambda hv=hash_value: self.copy_to_clipboard(hv),
                bg="#555555",
                fg="white",
                activebackground="#666666",
                activeforeground="white",
                bd=0,
                state="normal" if hash_value != "N/A" else "disabled"
            )
            copy_button.pack(side=tk.RIGHT, padx=5)

            self.hash_labels.append((hash_label, copy_button))

    def copy_to_clipboard(self, text):
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            messagebox.showinfo("Success", f"Copied {text} to clipboard!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.config_manager.save_config(folder)
            self.result_label.config(text="")
            if self.path_label is None:
                self.path_label = tk.Label(self.left_frame, textvariable=self.folder_path, wraplength=350, **self.label_style)
                self.path_label.pack(pady=10, before=self.extract_frame)
            self.detected_game = detect_game(folder)
            self.processor.log_action(f"New folder selected: {folder}, Detected game: {self.detected_game}")
            self.update_game_label()
            self.update_hash_results()
            self.load_log_contents()
        else:
            if self.path_label is not None:
                self.path_label.pack_forget()
                self.path_label.destroy()
                self.path_label = None
            self.detected_game = "Unknown"
            self.processor.log_action(f"Folder selection cancelled, Detected game: {self.detected_game}")
            self.update_game_label()
            self.update_hash_results()
            self.load_log_contents()

    def extract_words_wrapper(self):
        current_time = datetime.now().timestamp()
        time_since_last = current_time - self.last_execution

        if time_since_last < self.cooldown_period:
            remaining = self.cooldown_period - time_since_last
            self.status_label.config(text=f"Please wait {remaining:.1f} seconds...")
            self.extract_button.config(state="disabled")
            self.root.after(int(remaining * 1000), self.reset_cooldown)
            return

        self.last_execution = current_time
        self.extract_button.config(state="disabled")
        self.status_label.config(text="Processing...")
        self.root.after(100, self.extract_words)

    def reset_cooldown(self):
        self.extract_button.config(state="normal")
        self.status_label.config(text="Ready")
        self.load_log_contents()

    def extract_words(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first!")
            self.reset_cooldown()
            return

        try:
            total_words, unhashed_count, hashed_count = self.processor.process_scripts(folder, self.detected_game)
            self.result_label.config(text=f"Found {total_words} unique words ({unhashed_count} unhashed, {hashed_count} hashed)")
            messagebox.showinfo("Success", f"Words classified and saved in {self.processor.get_game_dir(self.detected_game)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.processor.log_action(f"Extraction failed: {str(e)}")
        finally:
            self.reset_cooldown()

if __name__ == "__main__":
    root = tk.Tk()
    app = WordExtractorApp(root)
    root.mainloop()