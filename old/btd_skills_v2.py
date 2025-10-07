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

        # --- MAIN KEYS SECTION ---
        frame_main = tk.LabelFrame(root, text="Main Keys", padx=10, pady=5)
        frame_main.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_main, text="Keys to repeat:").pack(side="left", anchor="w")
        self.entry_keys = tk.Entry(frame_main, width=30)
        self.entry_keys.pack(side="left", padx=5)
        self.entry_keys.insert(0, "&é\"'(-è_çà")

        frame_main_interval = tk.Frame(root)
        frame_main_interval.pack(padx=10, pady=2, fill="x")
        tk.Label(frame_main_interval, text="Interval (ms) between cycles:").pack(side="left", anchor="w")
        self.entry_interval = tk.Entry(frame_main_interval, width=10)
        self.entry_interval.pack(side="left", padx=5)
        self.entry_interval.insert(0, "5000")

        # --- MONEY INPUT SECTION ---
        frame_money = tk.LabelFrame(root, text="Money Input", padx=10, pady=5)
        frame_money.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_money, text="Money key:").pack(side="left", anchor="w")
        self.entry_money = tk.Entry(frame_money, width=5)
        self.entry_money.pack(side="left", padx=5)
        self.entry_money.insert(0, "=")

        frame_money_interval = tk.Frame(root)
        frame_money_interval.pack(padx=10, pady=2, fill="x")
        tk.Label(frame_money_interval, text="Interval (ms):").pack(side="left", anchor="w")
        self.entry_money_interval = tk.Entry(frame_money_interval, width=10)
        self.entry_money_interval.pack(side="left", padx=5)
        self.entry_money_interval.insert(0, "2000")

        # --- STOP KEY SECTION ---
        frame_stop = tk.LabelFrame(root, text="Stop Key", padx=10, pady=5)
        frame_stop.pack(padx=10, pady=5, fill="x")

        tk.Label(frame_stop, text="Stop key:").pack(side="left", anchor="w")
        self.entry_stop = tk.Entry(frame_stop, width=5)
        self.entry_stop.pack(side="left", padx=5)
        self.entry_stop.insert(0, "q")

        # --- WINDOW OPTIONS ---
        frame_options = tk.LabelFrame(root, text="Window Options", padx=10, pady=5)
        frame_options.pack(padx=10, pady=5, fill="x")

        self.var_topmost = tk.BooleanVar(value=False)
        chk_topmost = tk.Checkbutton(
            frame_options,
            text="Keep app always on top",
            variable=self.var_topmost,
            command=self.toggle_topmost
        )
        chk_topmost.pack(anchor="w")

        # --- BUTTONS ---
        frame_buttons = tk.Frame(root)
        frame_buttons.pack(pady=10)
        self.btn_start = tk.Button(frame_buttons, text="Start", command=self.start_spam)
        self.btn_start.pack(side="left", padx=5)
        self.btn_stop = tk.Button(frame_buttons, text="Stop", command=self.stop_spam, state="disabled")
        self.btn_stop.pack(side="left", padx=5)

        # --- FOOTER ---
        try:
            footer_font = ("Old English Text MT", 10)  # Try gothic-style font
        except:
            footer_font = ("Arial", 10, "italic")  # Fallback if not available

        self.footer = tk.Label(root, text="Made by Kush Crew corporation", font=footer_font)
        self.footer.pack(side="bottom", anchor="e", padx=10, pady=5)  # Align right

    # --- TOGGLE WINDOW TOPMOST ---
    def toggle_topmost(self):
        """Enable or disable 'always on top' depending on checkbox state."""
        self.root.attributes("-topmost", self.var_topmost.get())

    # --- THREADS ---
    def spam_keys(self, keys, interval_ms):
        while self.running:
            for k in keys:
                if not self.running:
                    return
                try:
                    self.kb.press(k)
                    self.kb.release(k)
                except Exception as e:
                    print(f"Warning pressing {k!r}: {e}")
                sleep(self.per_key_delay)
            sleep(interval_ms / 1000.0)

    def spam_money(self, key, interval_ms):
        while self.running:
            try:
                self.kb.press(key)
                self.kb.release(key)
            except Exception as e:
                print(f"Warning pressing money key {key!r}: {e}")
            sleep(interval_ms / 1000.0)

    # --- KEYBOARD LISTENER ---
    def on_press(self, key):
        try:
            if hasattr(key, "char") and key.char == self.stop_key:
                self.running = False
                messagebox.showinfo("Info", f"Stopped by pressing '{self.stop_key}'")
                return False
        except Exception:
            pass

    # --- CONTROL ---
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
            if interval < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Invalid interval for main keys.")
            return

        stop_key_val = self.entry_stop.get()
        if not stop_key_val or len(stop_key_val) != 1:
            messagebox.showerror("Error", "Please enter exactly one stop key.")
            return
        self.stop_key = stop_key_val

        money_key = self.entry_money.get()
        if not money_key or len(money_key) != 1:
            messagebox.showerror("Error", "Please enter exactly one 'money input' key.")
            return
        try:
            money_interval = int(self.entry_money_interval.get())
            if money_interval < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Invalid interval for 'money input'.")
            return

        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")

        self.running = True
        threading.Thread(target=self.spam_keys, args=(keys, interval), daemon=True).start()
        threading.Thread(target=self.spam_money, args=(money_key, money_interval), daemon=True).start()

        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

    def stop_spam(self):
        if not self.running:
            return
        self.running = False
        if self.listener is not None:
            try:
                self.listener.stop()
            except Exception:
                pass
            self.listener = None
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        messagebox.showinfo("Info", "Stopped via GUI button.")

# --- RUN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BTDSpammerApp(root)
    root.mainloop()
