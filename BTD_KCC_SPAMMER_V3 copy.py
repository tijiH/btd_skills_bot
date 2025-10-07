import tkinter as tk
from tkinter import messagebox
from time import sleep
from pynput.keyboard import Listener
import threading
import pyautogui
import win32gui
import win32con
import win32process
import ctypes

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
INPUT_WIDTH = 20
BUTTON_WIDTH = 10
PER_KEY_DELAY = 0.1
# ======================================================


def get_active_window_title():
    hwnd = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(hwnd)


def list_open_windows():
    windows = []

    def enum_handler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            windows.append(win32gui.GetWindowText(hwnd))

    win32gui.EnumWindows(enum_handler, None)
    return windows


def force_window_foreground(hwnd):
    """
    Try to reliably bring hwnd to the foreground using AttachThreadInput trick.
    This is more reliable than just SetForegroundWindow.
    """
    try:
        if not hwnd or not win32gui.IsWindow(hwnd):
            return False

        # Restore if minimized
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        fg = win32gui.GetForegroundWindow()
        if fg == hwnd:
            # already foreground
            return True

        # get thread IDs
        try:
            tid_foreground = win32process.GetWindowThreadProcessId(fg)[0]
            tid_target = win32process.GetWindowThreadProcessId(hwnd)[0]
        except Exception:
            tid_foreground = None
            tid_target = None

        # Attach thread input if possible
        if tid_foreground and tid_target and tid_foreground != tid_target:
            ctypes.windll.user32.AttachThreadInput(tid_foreground, tid_target, True)
            win32gui.SetForegroundWindow(hwnd)
            ctypes.windll.user32.AttachThreadInput(tid_foreground, tid_target, False)
        else:
            # fallback
            win32gui.SetForegroundWindow(hwnd)

        # also bring to top
        win32gui.BringWindowToTop(hwnd)
        return True
    except Exception:
        try:
            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False


class BTDSpammerApp:
    def __init__(self, root):
        self.root = root
        root.title("BTD Key Spammer")

        # state
        self.running = False
        self.listener = None
        self.stop_key = DEFAULT_STOP_KEY
        self.target_window = None      # title
        self.target_hwnd = None        # HWND
        self.per_key_delay = PER_KEY_DELAY

        # UI colors
        self.bg_color = DEFAULT_BG_COLOR
        self.fg_color = DEFAULT_FG_COLOR
        root.configure(bg=self.bg_color)

        # --- TARGET WINDOW SELECTION ---
        frame_window = tk.LabelFrame(root, text="Target Window", padx=10, pady=5,
                                    bg=self.bg_color, fg=self.fg_color)
        frame_window.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_window, text="Select window:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0,
                                                                                               sticky="w")
        self.window_var = tk.StringVar()
        open_windows = list_open_windows()
        if open_windows:
            self.window_var.set(open_windows[0])
        self.dropdown = tk.OptionMenu(frame_window, self.window_var, *open_windows)
        self.dropdown.config(width=INPUT_WIDTH, bg="#2c2c2c", fg="white")
        self.dropdown.grid(row=0, column=1, padx=5)

        # Refresh button (small)
        self.btn_refresh = tk.Button(frame_window, text="🔄", command=self.refresh_windows, width=3,
                                     bg=self.bg_color, fg="white", relief="flat")
        self.btn_refresh.grid(row=0, column=2, padx=5)

        # --- MAIN KEYS ---
        frame_main = tk.LabelFrame(root, text="Main Keys", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_main.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_main, text="Keys to repeat:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky="w")
        self.entry_keys = tk.Entry(frame_main, width=INPUT_WIDTH, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_keys.grid(row=0, column=1, padx=5)
        self.entry_keys.insert(0, DEFAULT_KEYS)

        tk.Label(frame_main, text="Interval (ms):", bg=self.bg_color, fg=self.fg_color).grid(row=1, column=0, sticky="w")
        self.entry_interval = tk.Entry(frame_main, width=INPUT_WIDTH, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_interval.grid(row=1, column=1, padx=5)
        self.entry_interval.insert(0, str(DEFAULT_INTERVAL))

        # --- MONEY INPUT ---
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

        # --- STOP KEY ---
        frame_stop = tk.LabelFrame(root, text="Stop Key", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_stop.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_stop, text="Stop key:", bg=self.bg_color, fg=self.fg_color).grid(row=0, column=0, sticky="w")
        self.entry_stop = tk.Entry(frame_stop, width=INPUT_WIDTH, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_stop.grid(row=0, column=1, padx=5)
        self.entry_stop.insert(0, DEFAULT_STOP_KEY)

        # --- Always On Top checkbox (for the app window itself) ---
        self.topmost_var = tk.BooleanVar()
        self.chk_topmost = tk.Checkbutton(root, text="Always On Top", variable=self.topmost_var, command=self.toggle_topmost,
                                         bg=self.bg_color, fg="white", selectcolor=self.bg_color)
        self.chk_topmost.pack(padx=10, pady=(0, 5), anchor="w")

        # --- Bring Window to Front checkbox (for the target window) ---
        self.bring_front_var = tk.BooleanVar()
        self.chk_bring_front = tk.Checkbutton(root, text="Bring target window to front before each cycle",
                                              variable=self.bring_front_var, bg=self.bg_color, fg="white", selectcolor=self.bg_color)
        self.chk_bring_front.pack(padx=10, pady=(0, 10), anchor="w")

        # --- BUTTONS CENTERED ---
        frame_buttons = tk.Frame(root, bg=self.bg_color)
        frame_buttons.pack(pady=10)
        self.btn_start = tk.Button(frame_buttons, text="Start", command=self.start_spam, width=BUTTON_WIDTH, bg="#4CAF50", fg="white", relief="flat")
        self.btn_start.pack(side="left", padx=5)
        self.btn_stop = tk.Button(frame_buttons, text="Stop", command=self.stop_spam, width=BUTTON_WIDTH, state="disabled", bg="#f44336", fg="white", relief="flat")
        self.btn_stop.pack(side="left", padx=5)

        # --- FOOTER & STATUS ---
        footer_frame = tk.Frame(root, bg=self.bg_color)
        footer_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        self.status_label = tk.Label(footer_frame, text="Spam stopped", bg=self.bg_color, fg="white", font=DEFAULT_FONT)
        self.status_label.pack(side="left")

        # LED to the right of status_label
        self.led = tk.Canvas(footer_frame, width=20, height=20, bg=self.bg_color, highlightthickness=0)
        self.led.pack(side="left", padx=5)
        self.led_circle = self.led.create_oval(2, 2, 18, 18, fill="red")

        self.footer = tk.Label(footer_frame, text=FOOTER_TEXT, font=FOOTER_FONT, bg=self.bg_color, fg=self.fg_color)
        self.footer.pack(side="right")

    # ----------------- THREADS -----------------
    def spam_keys(self, keys, interval_ms):
        # initial wait before first cycle
        sleep(interval_ms / 1000.0)
        while self.running:
            # ensure target HWND is valid
            if not self.target_hwnd_valid():
                # if HWND is invalid, try to find it again
                self.find_target_hwnd()
                if not self.target_hwnd_valid():
                    # cannot find the target, stop to avoid uncontrolled behavior
                    self.running = False
                    self.update_led()
                    messagebox.showerror("Error", f"Target window '{self.target_window}' not found. Stopping spam.")
                    return

            # optionally bring the target window to front
            if self.bring_front_var.get():
                force_window_foreground(self.target_hwnd)

            # only send keys if the target is the active window (after bring_front, usually true)
            if get_active_window_title() == self.target_window:
                for k in keys:
                    if not self.running:
                        return
                    try:
                        pyautogui.press(k)
                    except Exception:
                        pass
                    sleep(self.per_key_delay)

            sleep(interval_ms / 1000.0)

    def spam_money(self, key, interval_ms):
        while self.running:
            if not self.target_hwnd_valid():
                self.find_target_hwnd()
                if not self.target_hwnd_valid():
                    self.running = False
                    self.update_led()
                    messagebox.showerror("Error", f"Target window '{self.target_window}' not found. Stopping spam.")
                    return

            if self.bring_front_var.get():
                force_window_foreground(self.target_hwnd)

            if get_active_window_title() == self.target_window:
                try:
                    pyautogui.press(key)
                except Exception:
                    pass

            sleep(interval_ms / 1000.0)

    # ----------------- HELPERS -----------------
    def find_target_hwnd(self):
        """Find and store HWND for the selected target window title."""
        title = self.target_window
        if not title:
            self.target_hwnd = None
            return
        hwnd = win32gui.FindWindow(None, title)
        self.target_hwnd = hwnd if hwnd and win32gui.IsWindow(hwnd) else None

    def target_hwnd_valid(self):
        return getattr(self, "target_hwnd", None) and win32gui.IsWindow(self.target_hwnd)

    # ----------------- KEYBOARD LISTENER -----------------
    def on_press(self, key):
        try:
            if hasattr(key, "char") and key.char == self.stop_key:
                self.stop_spam()
                return False
        except Exception:
            pass

    # ----------------- CONTROL -----------------
    def start_spam(self):
        if self.running:
            messagebox.showwarning("Already Running", "The spam is already running.")
            return

        keys = list(self.entry_keys.get()) if self.entry_keys.get() else []
        try:
            interval = int(self.entry_interval.get())
        except Exception:
            messagebox.showerror("Error", "Invalid interval for main keys.")
            return

        stop_key_val = self.entry_stop.get()
        if stop_key_val:
            self.stop_key = stop_key_val

        money_key = self.entry_money.get() if self.entry_money.get() else DEFAULT_MONEY_KEY
        try:
            money_interval = int(self.entry_money_interval.get())
        except Exception:
            money_interval = DEFAULT_MONEY_INTERVAL

        self.target_window = self.window_var.get()
        self.find_target_hwnd()
        if not self.target_hwnd_valid():
            messagebox.showerror("Error", f"Target window '{self.target_window}' not found.")
            return

        # If bring_front_var is set, bring once now before starting threads
        if self.bring_front_var.get():
            force_window_foreground(self.target_hwnd)

        self.running = True
        self.update_led()
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")

        threading.Thread(target=self.spam_keys, args=(keys, interval), daemon=True).start()
        threading.Thread(target=self.spam_money, args=(money_key, money_interval), daemon=True).start()

        # install global listener for stop key
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

    def stop_spam(self):
        if not self.running:
            return
        self.running = False
        if self.listener:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None
        self.update_led()
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        self.status_label.config(text="Spam stopped")
        messagebox.showinfo("Info", "Stopped via GUI button.")

    # ----------------- TOPMOST (app) -----------------
    def toggle_topmost(self):
        try:
            self.root.attributes("-topmost", self.topmost_var.get())
        except Exception:
            pass

    # ----------------- REFRESH -----------------
    def refresh_windows(self):
        open_windows = list_open_windows()
        menu = self.dropdown["menu"]
        menu.delete(0, "end")
        for w in open_windows:
            menu.add_command(label=w, command=lambda value=w: self.window_var.set(value))
        if open_windows:
            self.window_var.set(open_windows[0])

    # ----------------- LED -----------------
    def update_led(self):
        color = "green" if self.running else "red"
        self.led.itemconfig(self.led_circle, fill=color)
        self.status_label.config(text="Spamming running" if self.running else "Spam stopped", fg=color)


# --- RUN APP ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BTDSpammerApp(root)
    root.mainloop()
