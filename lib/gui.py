import sys
import threading
import tkinter as tk
from tkinter import DoubleVar

class GuiVals:
    def __init__(self, framerate, timeframe):
        self.framerate = framerate
        self.timeframe = timeframe

def start():
    global init_complete, shutdown_complete
    init_complete = threading.Event()  # Event to signal initialization completion
    shutdown_complete = threading.Event()  # Event to signal shutdown
    gui_thread = threading.Thread(target=_run_gui)
    gui_thread.daemon = True
    gui_thread.start()

def _run_gui():
    global root, framerate_var, timeframe_var
    root = tk.Tk()
    root.title("Settings")

    framerate_var = DoubleVar(value=60)
    timeframe_var = DoubleVar(value=0.5)

    tk.Scale(root, from_=1, to=120, orient='horizontal', label='Framerate', variable=framerate_var).pack()
    tk.Scale(root, from_=0.1, to=2, resolution=0.1, orient='horizontal', label='Timeframe', variable=timeframe_var).pack()

    init_complete.set()
    root.protocol("WM_DELETE_WINDOW", _on_close)
    root.mainloop()

def get_values():
    if not init_complete.is_set():
        init_complete.wait()  # Block until GUI is ready
    return GuiVals(framerate_var.get(), timeframe_var.get())

def has_stopped():
    return shutdown_complete.is_set()

def _on_close():
    if not shutdown_complete.is_set():
        root.quit()  # Terminates mainloop
        root.destroy()  # Destroys all widgets
        shutdown_complete.set()  # Signal the main application to shut down