import tkinter as tk
from recording_module import RecordingModule
from audio_preprocessing import open_audio_preprocessing
from voice_cloning import VoiceCloning
from video_processing import VideoProcessing
from PIL import Image, ImageTk
import os
import threading
import time

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Cloning Application")
        self.center_window(400, 300)

        self.load_icons()

        tk.Button(root, text="Recording Feature", image=self.mic_icon, compound="left", command=self.open_recording).pack(pady=15)
        tk.Button(root, text="Audio Preprocessing (UVR5)", image=self.uvr5_icon, compound="left", command=open_audio_preprocessing).pack(pady=15)
        tk.Button(root, text="Voice Cloning", image=self.voice_icon, compound="left", command=self.open_voice_cloning).pack(pady=15)
        tk.Button(root, text="Video Processing", image=self.video_icon, compound="left", command=self.open_video_processing).pack(pady=15)

        self.recording_module = RecordingModule(self.root)
        self.voice_cloning = VoiceCloning(self.root)
        self.video_processing = VideoProcessing(self.root)

        self.queue_thread = threading.Thread(target=self.process_queue)
        self.queue_thread.daemon = True
        self.queue_thread.start()

    def load_icons(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.mic_icon = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, "icon", "microphone.png")).resize((20, 20)))
        self.uvr5_icon = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, "icon", "UVR.jpg")).resize((20, 20)))
        self.voice_icon = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, "icon", "VoiceCloning.jpg")).resize((20, 20)))
        self.video_icon = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, "icon", "VideoProcessing.png")).resize((20, 20)))

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def open_recording(self):
        self.recording_module.open_recording()

    def open_voice_cloning(self):
        self.voice_cloning.open_voice_cloning()

    def open_video_processing(self):
        self.video_processing.open_video_processing()

    def process_queue(self):
        while True:
            try:
                self.root.after(0, self.voice_cloning.process_queue)  
            except Exception as e:
                print(f"Error in process_queue: {e}")
            time.sleep(0.5)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
