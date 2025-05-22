import tkinter as tk
import os
from tkinter import messagebox

def update_console(app, log_message):
    if hasattr(app, 'console_text'):
        app.console_text.config(state="normal")
        app.console_text.insert(tk.END, log_message)
        app.console_text.config(state="disabled")
        app.console_text.see(tk.END)
        app.root.update_idletasks()

def load_log_contents(app):
    # Move debug.log to root folder
    log_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "debug.log")
    try:
        # Create log file if it doesn't exist
        if os.path.exists(log_file_path):
            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            with open(log_file_path, 'w', encoding='utf-8') as f:
                f.write("Debug Log\n")
        with open(log_file_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        app.console_text.config(state="normal")
        app.console_text.delete(1.0, tk.END)
        app.console_text.insert(tk.END, log_content)
        app.console_text.config(state="disabled")
        app.console_text.see(tk.END)
    except Exception as e:
        update_console(app, f"Error loading log: {str(e)}\n")

def update_game_label(app):
    color = {
        "Black Ops 3": "#FFA500",
        "Black Ops 4": "#FFA500",
        "Black Ops 6": "#FFA500",
        "Black Ops Cold War": "#000000",
        "Modern Warfare III": "#90EE90"
    }.get(app.detected_game, "#FF8C00")
    app.game_label.config(text=f"Game: {app.detected_game}", foreground=color)

def copy_to_clipboard(app, text):
    try:
        app.root.clipboard_clear()
        app.root.clipboard_append(text)
        app.root.update()
        messagebox.showinfo("Success", f"Copied {text} to clipboard!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy to clipboard: {str(e)}")