import tkinter as tk
from tkinter import messagebox
from time import sleep
import threading
import pyautogui
import win32gui

# ================= CONFIG VARIABLES =================
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
INPUT_WIDTH = 20
BUTTON_HEIGHT = 2
PER_KEY_DELAY = 0.1

# ===================================================

def list_open_windows():
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
        self.kb = pyautogui
        self.running = False
        self.listener = None
        self.stop_key = None
        self.target_window = None
        self.keep_top = False

        # Theme
        self.bg_color = DEFAULT_BG_COLOR
        self.fg_color = DEFAULT_FG_COLOR
        root.configure(bg=self.bg_color)

        # ---------------- Target Window ----------------
        frame_window = tk.LabelFrame(root, text="Target Window", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_window.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_window, text="Select Window:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky="w")

        self.window_var = tk.StringVar()
        self.open_windows = list_open_windows()
        if self.open_windows:
            self.window_var.set(self.open_windows[0])
        self.dropdown = tk.OptionMenu(frame_window, self.window_var, *self.open_windows)
        self.dropdown.config(width=INPUT_WIDTH, bg="#2c2c2c", fg="white")
        self.dropdown.grid(row=0, column=1, padx=5)

        # Refresh button
        self.btn_refresh = tk.Button(frame_window, text="⟳", command=self.refresh_windows, width=3, height=BUTTON_HEIGHT, bg=self.bg_color, fg="white", relief="flat")
        self.btn_refresh.grid(row=0, column=2, padx=5)

        # Toggle top window button
        self.btn_toggle_top = tk.Button(frame_window, text="Toggle Window Background", command=self.toggle_top_window, width=INPUT_WIDTH+2, height=BUTTON_HEIGHT, bg="red", fg="white", relief="flat")
        self.btn_toggle_top.grid(row=1, column=0, columnspan=3, pady=5)

        # ---------------- Main Keys ----------------
        frame_main = tk.LabelFrame(root, text="Main Keys", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_main.pack(padx=10, pady=5, fill="x")
        tk.Label(frame_main, text="Keys to repeat:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky="w")
        self.entry_keys = tk.Entry(frame_main, width=INPUT_WIDTH, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_keys.grid(row=0, column=1, padx=5)
        self.entry_keys.insert(0, DEFAULT_KEYS)

        # Interval
        tk.Label(frame_main, text="Interval (ms):", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, sticky="w")
        self.entry_interval = tk.Entry(frame_main, width=INPUT_WIDTH, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_interval.grid(row=1, column=1, padx=5)
        self.entry_interval.insert(0, str(DEFAULT_INTERVAL))

        # ---------------- Money Input ----------------
        frame_money = tk.LabelFrame(root, text="Money Input", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_money.pack(padx=10, pady=5, fill="x")
        tk.Label(frame_money, text="Money key:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky="w")
        self.entry_money = tk.Entry(frame_money, width=INPUT_WIDTH, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_money.grid(row=0, column=1, padx=5)
        self.entry_money.insert(0, DEFAULT_MONEY_KEY)

        tk.Label(frame_money, text="Interval (ms):", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, sticky="w")
        self.entry_money_interval = tk.Entry(frame_money, width=INPUT_WIDTH, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_money_interval.grid(row=1, column=1, padx=5)
        self.entry_money_interval.insert(0, str(DEFAULT_MONEY_INTERVAL))

        # ---------------- Stop Key ----------------
        frame_stop = tk.LabelFrame(root, text="Stop Key", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_stop.pack(padx=10, pady=5, fill="x")
        tk.Label(frame_stop, text="Stop key:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky="w")
        self.entry_stop = tk.Entry(frame_stop, width=INPUT_WIDTH, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_stop.grid(row=0, column=1, padx=5)
        self.entry_stop.insert(0, DEFAULT_STOP_KEY)

        # ---------------- Buttons Centered ----------------
        frame_buttons = tk.Frame(root, bg=self.bg_color)
        frame_buttons.pack(pady=10)
        self.btn_start = tk.Button(frame_buttons, text="Start", command=self.start_spam, width=15, height=BUTTON_HEIGHT, bg="#4CAF50", fg="white", relief="flat")
        self.btn_start.pack(side="left", padx=10)
        self.btn_stop = tk.Button(frame_buttons, text="Stop", command=self.stop_spam, width=15, height=BUTTON_HEIGHT, state="disabled", bg="#f44336", fg="white", relief="flat")
        self.btn_stop.pack(side="left", padx=10)

        # ---------------- Status + Footer ----------------
        footer_frame = tk.Frame(root, bg=self.bg_color)
        footer_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        self.status_label = tk.Label(footer_frame, text="Spam stopped", bg=self.bg_color, fg="white", font=DEFAULT_FONT)
        self.status_label.pack(side="left")
        self.footer = tk.Label(footer_frame, text=FOOTER_TEXT, font=FOOTER_FONT, bg=self.bg_color, fg=self.fg_color)
        self.footer.pack(side="right")

    # ----------------- THREADS -----------------
    def spam_keys(self, keys, interval_ms):
        sleep(interval_ms / 1000.0)
        while self.running:
            if self.target_window:
                hwnd = win32gui.FindWindow(None, self.target_window)
                if hwnd:
                    win32gui.SetForegroundWindow(hwnd)
                    for k in keys:
                        if not self.running:
                            return
                        try:
                            self.kb.press(k)
                            self.kb.release(k)
                        except:
                            pass
                        sleep(PER_KEY_DELAY)
            sleep(interval_ms / 1000.0)

    def spam_money(self, key, interval_ms):
        while self.running:
            if self.target_window:
                hwnd = win32gui.FindWindow(None, self.target_window)
                if hwnd:
                    win32gui.SetForegroundWindow(hwnd)
                    try:
                        self.kb.press(key)
                        self.kb.release(key)
                    except:
                        pass
            sleep(interval_ms / 1000.0)

    # ----------------- CONTROL -----------------
    def start_spam(self):
        if self.running:
            messagebox.showwarning("Already Running", "The spam is already running.")
            return
        self.target_window = self.window_var.get()
        keys = list(self.entry_keys.get())
        money_key = self.entry_money.get()
        self.stop_key = self.entry_stop.get()
        try:
            interval = int(self.entry_interval.get())
            money_interval = int(self.entry_money_interval.get())
        except:
            messagebox.showerror("Error", "Invalid intervals.")
            return
        self.running = True
        self.update_status()
        threading.Thread(target=self.spam_keys, args=(keys, interval), daemon=True).start()
        threading.Thread(target=self.spam_money, args=(money_key, money_interval), daemon=True).start()

    def stop_spam(self):
        self.running = False
        self.update_status()

    # ----------------- WINDOW TOOLS -----------------
    def refresh_windows(self):
        self.open_windows = list_open_windows()
        menu = self.dropdown["menu"]
        menu.delete(0, "end")
        for w in self.open_windows:
            menu.add_command(label=w, command=lambda value=w: self.window_var.set(value))
        if self.open_windows:
            self.window_var.set(self.open_windows[0])

    def toggle_top_window(self):
        self.keep_top = not self.keep_top
        if self.keep_top:
            self.btn_toggle_top.config(bg="green")
        else:
            self.btn_toggle_top.config(bg="red")
        if self.target_window:
            hwnd = win32gui.FindWindow(None, self.target_window)
            if hwnd:
                win32gui.SetWindowPos(hwnd, -1 if self.keep_top else 0,0,0,0,0,3)

    # ----------------- STATUS -----------------
    def update_status(self):
        self.status_label.config(text="Spamming running" if self.running else "Spam stopped")

# ----------------- RUN APP -----------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BTDSpammerApp(root)
    root.mainloop()
