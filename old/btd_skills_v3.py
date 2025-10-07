import tkinter as tk
from tkinter import messagebox
from time import sleep
from pynput.keyboard import Controller, Listener
import threading

class BTDSpammerApp:
    def __init__(self, root):
        self.root = root
        root.title("BTD Key Spammer")

        self.kb = Controller()
        self.running = False
        self.listener = None
        self.stop_key = None
        self.per_key_delay = 0.1

        # --- THEME ---
        self.bg_color = "#1e1e1e"
        self.fg_color = "white"
        root.configure(bg=self.bg_color)

        # --- MAIN KEYS ---
        frame_main = tk.LabelFrame(root, text="Main Keys", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_main.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_main, text="Keys to repeat:", bg=self.bg_color, fg=self.fg_color).pack(side="left", anchor="w")
        self.entry_keys = tk.Entry(frame_main, width=30, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_keys.pack(side="left", padx=5)
        self.entry_keys.insert(0, "&é\"'(-è_çà")

        # Interval
        frame_main_interval = tk.Frame(root, bg=self.bg_color)
        frame_main_interval.pack(padx=10, pady=2, fill="x")
        tk.Label(frame_main_interval, text="Interval (ms) between cycles:", bg=self.bg_color, fg=self.fg_color).pack(side="left", anchor="w")
        self.entry_interval = tk.Entry(frame_main_interval, width=10, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_interval.pack(side="left", padx=5)
        self.entry_interval.insert(0, "5000")

        # --- MONEY INPUT ---
        frame_money = tk.LabelFrame(root, text="Money Input", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_money.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_money, text="Money key:", bg=self.bg_color, fg=self.fg_color).pack(side="left", anchor="w")
        self.entry_money = tk.Entry(frame_money, width=5, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_money.pack(side="left", padx=5)
        self.entry_money.insert(0, "=")

        frame_money_interval = tk.Frame(root, bg=self.bg_color)
        frame_money_interval.pack(padx=10, pady=2, fill="x")
        tk.Label(frame_money_interval, text="Interval (ms):", bg=self.bg_color, fg=self.fg_color).pack(side="left", anchor="w")
        self.entry_money_interval = tk.Entry(frame_money_interval, width=10, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_money_interval.pack(side="left", padx=5)
        self.entry_money_interval.insert(0, "2000")

        # --- STOP KEY ---
        frame_stop = tk.LabelFrame(root, text="Stop Key", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_stop.pack(padx=10, pady=5, fill="x")
        tk.Label(frame_stop, text="Stop key:", bg=self.bg_color, fg=self.fg_color).pack(side="left", anchor="w")
        self.entry_stop = tk.Entry(frame_stop, width=5, bg="#2c2c2c", fg="white", insertbackground="white")
        self.entry_stop.pack(side="left", padx=5)
        self.entry_stop.insert(0, "q")

        # --- WINDOW OPTIONS ---
        frame_options = tk.LabelFrame(root, text="Window Options", padx=10, pady=5, bg=self.bg_color, fg=self.fg_color)
        frame_options.pack(padx=10, pady=5, fill="x")
        self.var_topmost = tk.BooleanVar(value=False)
        chk_topmost = tk.Checkbutton(
            frame_options,
            text="Keep app always on top",
            variable=self.var_topmost,
            command=self.toggle_topmost,
            bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color
        )
        chk_topmost.pack(anchor="w")

        # --- BUTTONS (LEFT ALIGNED) ---
        frame_buttons = tk.Frame(root, bg=self.bg_color)
        frame_buttons.pack(pady=10, anchor="w")  # align à gauche
        self.btn_start = tk.Button(frame_buttons, text="Start", command=self.start_spam, bg="#4CAF50", fg="white", relief="flat")
        self.btn_start.pack(side="left", padx=5)
        self.btn_stop = tk.Button(frame_buttons, text="Stop", command=self.stop_spam, state="disabled", bg="#f44336", fg="white", relief="flat")
        self.btn_stop.pack(side="left", padx=5)

        # --- LED INDICATOR ---
        self.led = tk.Canvas(root, width=20, height=20, bg=self.bg_color, highlightthickness=0)
        self.led.pack(anchor="ne", padx=10, pady=5)
        self.led_circle = self.led.create_oval(2,2,18,18, fill="red")  # rouge par défaut

        # --- STATUS LABEL ---
        self.status_label = tk.Label(root, text="Spam stopped", bg=self.bg_color, fg="white", font=("Arial", 9))
        self.status_label.pack(side="bottom", anchor="w", padx=10, pady=5)

        # --- FOOTER ---
        self.footer = tk.Label(root, text="Made by Kush Crew corporation", font=("Old English Text MT", 10), bg=self.bg_color, fg=self.fg_color)
        self.footer.pack(side="bottom", anchor="e", padx=10, pady=5)

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

    # ----------------- TOPMOST -----------------
    def toggle_topmost(self):
        self.root.attributes("-topmost", self.var_topmost.get())

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
