import tkinter as tk
from tkinter import messagebox
from time import sleep
from pynput.keyboard import Controller, Listener
import threading
import win32gui

# ================== CONFIG VARIABLES ==================
DEFAULT_KEYS = "&é\"'(-è_çà"
DEFAULT_INTERVAL = 5000
DEFAULT_MONEY_KEY = "="
DEFAULT_MONEY_INTERVAL = 2000
DEFAULT_STOP_KEY = "q"
DEFAULT_BG_COLOR = "#1e1e1e"
DEFAULT_FG_COLOR = "white"
DEFAULT_FONT = ("Arial", 9)
FOOTER_TEXT = "Made by Kush Crew corporation"
FOOTER_FONT = ("Old English Text MT", 10)
# =====================================================

def list_open_windows():
    """Return a list of visible windows."""
    windows = []
    def enum_handler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            windows.append(win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(enum_handler, None)
    return windows

class BTDSpammerApp:
    def __init__(self, root):
        self.root = root
        root.title("BTD Key Spammer")

        self.kb = Controller()
        self.running = False
        self.listener = None
        self.stop_key = None
        self.per_key_delay = 0.1
        self.target_window = None
        self.topmost_enabled = False

        # --- THEME ---
        self.bg_color = DEFAULT_BG_COLOR
        self.fg_color = DEFAULT_FG_COLOR
        root.configure(bg=self.bg_color)

        # --- WINDOW SELECTION ---
        frame_window = tk.LabelFrame(root, text="Target Window", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_window.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_window, text="Select window:", bg=self.bg_color, fg=self.fg_color).pack(side="left")
        self.window_var = tk.StringVar()
        self.dropdown = tk.OptionMenu(frame_window, self.window_var, *list_open_windows())
        self.dropdown.config(bg="#2c2c2c", fg="white")
        self.dropdown.pack(side="left", padx=5)

        # Small refresh button
        self.btn_refresh = tk.Button(frame_window, text="⟳", command=self.refresh_windows, bg=self.bg_color, fg="white", width=2)
        self.btn_refresh.pack(side="left", padx=2)

        # Toggle top-most button
        self.btn_topmost = tk.Button(frame_window, text="Toggle Always On Top", command=self.toggle_topmost_ui, bg="red", fg="white")
        self.btn_topmost.pack(side="left", padx=5)

        # --- MAIN KEYS ---
        frame_main = tk.LabelFrame(root, text="Main Keys", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_main.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_main, text="Keys to repeat:", bg=self.bg_color, fg=self.fg_color).pack(side="left", anchor="w")
        self.entry_keys = tk.Entry(frame_main, width=30, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_keys.pack(side="left", padx=5)
        self.entry_keys.insert(0, DEFAULT_KEYS)

        # Interval
        frame_main_interval = tk.Frame(root, bg=self.bg_color)
        frame_main_interval.pack(padx=10, pady=2, fill="x")
        tk.Label(frame_main_interval, text="Interval (ms) between cycles:", bg=self.bg_color, fg=self.fg_color).pack(side="left", anchor="w")
        self.entry_interval = tk.Entry(frame_main_interval, width=10, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_interval.pack(side="left", padx=5)
        self.entry_interval.insert(0, str(DEFAULT_INTERVAL))

        # --- MONEY INPUT ---
        frame_money = tk.LabelFrame(root, text="Money Input", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_money.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_money, text="Money key:", bg=self.bg_color, fg=self.fg_color).pack(side="left", anchor="w")
        self.entry_money = tk.Entry(frame_money, width=5, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_money.pack(side="left", padx=5)
        self.entry_money.insert(0, DEFAULT_MONEY_KEY)

        frame_money_interval = tk.Frame(root, bg=self.bg_color)
        frame_money_interval.pack(padx=10, pady=2, fill="x")
        tk.Label(frame_money_interval, text="Interval (ms):", bg=self.bg_color, fg=self.fg_color).pack(side="left", anchor="w")
        self.entry_money_interval = tk.Entry(frame_money_interval, width=10, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_money_interval.pack(side="left", padx=5)
        self.entry_money_interval.insert(0, str(DEFAULT_MONEY_INTERVAL))

        # --- STOP KEY ---
        frame_stop = tk.LabelFrame(root, text="Stop Key", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_stop.pack(padx=10, pady=5, fill="x")
        tk.Label(frame_stop, text="Stop key:", bg=self.bg_color, fg=self.fg_color).pack(side="left", anchor="w")
        self.entry_stop = tk.Entry(frame_stop, width=5, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_stop.pack(side="left", padx=5)
        self.entry_stop.insert(0, DEFAULT_STOP_KEY)

        # --- BUTTONS (CENTERED) ---
        frame_buttons = tk.Frame(root, bg=self.bg_color)
        frame_buttons.pack(pady=10)
        self.btn_start = tk.Button(frame_buttons, text="Start", command=self.start_spam, bg="#4CAF50", fg="white", relief="flat", width=10)
        self.btn_start.pack(side="left", padx=10)
        self.btn_stop = tk.Button(frame_buttons, text="Stop", command=self.stop_spam, state="disabled", bg="#f44336", fg="white", relief="flat", width=10)
        self.btn_stop.pack(side="left", padx=10)

        # --- LED & FOOTER ---
        footer_frame = tk.Frame(root, bg=self.bg_color)
        footer_frame.pack(side="bottom", fill="x", padx=10, pady=5)

        self.status_label = tk.Label(footer_frame, text="Spam stopped", bg=self.bg_color, fg="red", font=DEFAULT_FONT)
        self.status_label.pack(side="left")
        self.footer = tk.Label(footer_frame, text=FOOTER_TEXT, font=FOOTER_FONT, bg=self.bg_color, fg=self.fg_color)
        self.footer.pack(side="right")

    # ----------------- THREADS -----------------
    def spam_keys(self, keys, interval_ms):
        sleep(interval_ms / 1000.0)
        while self.running:
            for k in keys:
                if not self.running:
                    return
                try:
                    self.kb.press(k)
                    self.kb.release(k)
                except:
                    pass
                sleep(self.per_key_delay)
            sleep(interval_ms / 1000.0)

    def spam_money(self, key, interval_ms):
        while self.running:
            try:
                self.kb.press(key)
                self.kb.release(key)
            except:
                pass
            sleep(interval_ms / 1000.0)

    # ----------------- KEYBOARD LISTENER -----------------
    def on_press(self, key):
        try:
            if hasattr(key, "char") and key.char == self.stop_key:
                self.stop_spam()
                return False
        except:
            pass

    # ----------------- CONTROL -----------------
    def start_spam(self):
        if self.running:
            messagebox.showwarning("Already Running", "The spam is already running.")
            return
        keys_str = self.entry_keys.get()
        keys = list(keys_str) if keys_str else []
        try:
            interval = int(self.entry_interval.get())
        except:
            interval = DEFAULT_INTERVAL
        stop_key_val = self.entry_stop.get()
        self.stop_key = stop_key_val if stop_key_val else DEFAULT_STOP_KEY
        money_key = self.entry_money.get()
        money_interval = int(self.entry_money_interval.get()) if self.entry_money_interval.get() else DEFAULT_MONEY_INTERVAL

        self.target_window = self.window_var.get()

        self.running = True
        self.update_led()
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        threading.Thread(target=self.spam_keys, args=(keys, interval), daemon=True).start()
        threading.Thread(target=self.spam_money, args=(money_key, money_interval), daemon=True).start()
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

    def stop_spam(self):
        if not self.running:
            return
        self.running = False
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass
            self.listener = None
        self.update_led()
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        messagebox.showinfo("Info", "Stopped via GUI button.")

    # ----------------- TOPMOST -----------------
    def toggle_topmost_ui(self):
        # Inverse la valeur
        current = self.root.attributes("-topmost")
        new_value = not current
        self.root.attributes("-topmost", new_value)
        # Change la couleur du bouton selon l'état
        self.btn_topmost.config(bg="green" if new_value else "red")


    # ----------------- REFRESH WINDOWS -----------------
    def refresh_windows(self):
        menu = self.dropdown["menu"]
        menu.delete(0, "end")
        for w in list_open_windows():
            menu.add_command(label=w, command=lambda value=w: self.window_var.set(value))
        if list_open_windows():
            self.window_var.set(list_open_windows()[0])

    # ----------------- LED / STATUS -----------------
    def update_led(self):
        color = "green" if self.running else "red"
        self.status_label.config(text="Spamming running" if self.running else "Spam stopped", fg=color)

# --- RUN APP ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BTDSpammerApp(root)
    root.mainloop()
