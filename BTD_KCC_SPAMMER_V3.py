import tkinter as tk
from tkinter import messagebox
from time import sleep
from pynput.keyboard import Controller, Listener
import threading
import win32gui
import win32con

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
PER_KEY_DELAY = 0.1

# =====================================================

def list_open_windows():
    """Returns a list of visible windows."""
    windows = []
    def enum_handler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            windows.append(win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(enum_handler, None)
    return windows

def bring_window_to_front(window_title):
    """Bring the target window to the front."""
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return hwnd
    return None

class BTDSpammerApp:
    def __init__(self, root):
        self.root = root
        root.title("BTD Key Spammer")

        self.kb = Controller()
        self.running = False
        self.listener = None
        self.stop_key = None
        self.target_window = None
        self.keep_window_on_top = False
        self.bg_color = DEFAULT_BG_COLOR
        self.fg_color = DEFAULT_FG_COLOR

        root.configure(bg=self.bg_color)

        # --- WINDOW SELECTION ---
        frame_window = tk.LabelFrame(root, text="Target Window", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_window.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_window, text="Select window:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky="w")
        self.window_var = tk.StringVar()
        open_windows = list_open_windows()
        if open_windows:
            self.window_var.set(open_windows[0])
        self.dropdown = tk.OptionMenu(frame_window, self.window_var, *open_windows)
        self.dropdown.config(bg="#2c2c2c", fg="white")
        self.dropdown.grid(row=0, column=1, padx=5, sticky="w")

        # Refresh button (icon)
        self.btn_toggle_top = tk.Button(frame_window, text="Keep Target Always on Top: OFF", command=self.toggle_target_topmost, bg="#9C27B0", fg="white", relief="flat")
        self.btn_refresh.grid(row=0, column=2, padx=5, sticky="w")

        # Toggle keep target on top (below)
        self.btn_toggle_top = tk.Button(frame_window, text="Keep Target Always on Top: OFF", 
                                        command=self.toggle_target_topmost, bg="#FF9800", fg="white", relief="flat")
        self.btn_toggle_top.grid(row=1, column=0, columnspan=3, pady=5, sticky="w")

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

        # --- BUTTONS (LEFT ALIGNED) ---
        frame_buttons = tk.Frame(root, bg=self.bg_color)
        frame_buttons.pack(pady=10, anchor="w")
        self.btn_start = tk.Button(frame_buttons, text="Start", command=self.start_spam, bg="#4CAF50", fg="white", relief="flat")
        self.btn_start.pack(side="left", padx=5)
        self.btn_stop = tk.Button(frame_buttons, text="Stop", command=self.stop_spam, state="disabled", bg="#f44336", fg="white", relief="flat")
        self.btn_stop.pack(side="left", padx=5)

        # --- LED INDICATOR + FOOTER/STATUS ---
        self.led = tk.Canvas(root, width=20, height=20, bg=self.bg_color, highlightthickness=0)
        self.led.pack(anchor="ne", padx=10, pady=5)
        self.led_circle = self.led.create_oval(2,2,18,18, fill="red")

        footer_frame = tk.Frame(root, bg=self.bg_color)
        footer_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        self.status_label = tk.Label(footer_frame, text="Spam stopped", bg=self.bg_color, fg="white", font=DEFAULT_FONT)
        self.status_label.pack(side="left")
        self.footer = tk.Label(footer_frame, text=FOOTER_TEXT, font=FOOTER_FONT, bg=self.bg_color, fg=self.fg_color)
        self.footer.pack(side="right")

    # ----------------- WINDOW REFRESH -----------------
    def refresh_windows(self):
        open_windows = list_open_windows()
        menu = self.dropdown["menu"]
        menu.delete(0, "end")
        for w in open_windows:
            menu.add_command(label=w, command=lambda value=w: self.window_var.set(value))
        if open_windows:
            self.window_var.set(open_windows[0])

    # ----------------- TOGGLE TARGET TOPMOST -----------------
    def toggle_target_topmost(self):
        self.keep_window_on_top = not self.keep_window_on_top
        status = "ON" if self.keep_window_on_top else "OFF"
        self.btn_toggle_top.config(text=f"Keep Target Always on Top: {status}")

    # ----------------- THREADS -----------------
    def spam_keys(self, keys, interval_ms):
        sleep(interval_ms / 1000.0)
        while self.running:
            hwnd = bring_window_to_front(self.target_window)
            if self.keep_window_on_top and hwnd:
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
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
            hwnd = bring_window_to_front(self.target_window)
            if self.keep_window_on_top and hwnd:
                win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0,0,0,0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
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
        if not keys_str:
            messagebox.showerror("Error", "Please enter at least one key to repeat.")
            return
        keys = list(keys_str)

        try:
            interval = int(self.entry_interval.get())
        except:
            messagebox.showerror("Error", "Invalid interval for main keys.")
            return

        stop_key_val = self.entry_stop.get()
        if not stop_key_val or len(stop_key_val) != 1:
            messagebox.showerror("Error", "Please enter exactly one stop key.")
            return
        self.stop_key = stop_key_val

        money_key = self.entry_money.get()
        if not money_key or len(money_key) != 1:
            messagebox.showerror("Error", "Please enter exactly one money key.")
            return
        try:
            money_interval = int(self.entry_money_interval.get())
        except:
            messagebox.showerror("Error", "Invalid interval for money input.")
            return

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
        self.status_label.config(text="Spam stopped")
        messagebox.showinfo("Info", "Stopped via GUI button.")

    # ----------------- LED -----------------
    def update_led(self):
        color = "green" if self.running else "red"
        self.led.itemconfig(self.led_circle, fill=color)
        self.status_label.config(text="Spamming running" if self.running else "Spam stopped")

# --- RUN APP ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BTDSpammerApp(root)
    root.mainloop()
