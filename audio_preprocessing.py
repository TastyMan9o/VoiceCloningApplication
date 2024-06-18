import subprocess
import os
from tkinter import messagebox

def open_audio_preprocessing():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, "Ultimate Vocal Remover", "UVR_Launcher.exe")

    if os.path.exists(filepath):
        subprocess.Popen(filepath, shell=True)
    else:
        messagebox.showerror("Error", "File not found, please check the path.")
