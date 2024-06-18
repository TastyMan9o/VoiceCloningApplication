import tkinter as tk
import sounddevice as sd
import wavio
import time
from tkinter import filedialog


class RecordingModule:
    def __init__(self, master):
        self.master = master
        self.recording_window = None
        self.recording = False
        self.start_time = None
        self.timer_label = None

    def open_recording(self):
        if not self.recording_window or not self.recording_window.winfo_exists():
            self.recording_window = tk.Toplevel(self.master)
            self.recording_window.title("Recording Feature")
            self.center_window(self.recording_window, 300, 200)
            self.record_button = tk.Button(self.recording_window, text="Start Recording", command=self.toggle_recording)
            self.record_button.pack(pady=10)
            self.timer_label = tk.Label(self.recording_window, text="Recording time: 00:00")
            self.timer_label.pack(pady=10)

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def toggle_recording(self):
        if not self.recording:
            self.record_button.config(text="Stop Recording")
            self.recording = True
            self.start_recording()
        else:
            self.record_button.config(text="Start Recording")
            self.recording = False
            self.stop_recording()

    def start_recording(self):
        self.frames = []
        self.stream = sd.InputStream(callback=self.audio_callback)
        self.stream.start()
        self.start_time = time.time()
        self.update_timer()

    def stop_recording(self):
        self.stream.stop()
        filename = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")])
        if filename:
            wavio.write(filename, self.frames, self.stream.samplerate, sampwidth=2)
        self.frames = []

    def audio_callback(self, indata, frames, time, status):
        self.frames.extend(indata.copy())

    def update_timer(self):
        if self.recording:
            elapsed_time = int(time.time() - self.start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            self.timer_label.config(text=f"Recording... {minutes:02}:{seconds:02}")
            self.recording_window.after(1000, self.update_timer)
