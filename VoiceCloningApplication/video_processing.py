import tkinter as tk
from tkinter import Label, messagebox, filedialog, simpledialog, Scrollbar, Frame, Canvas
from PIL import Image, ImageTk
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
import threading
import time
import queue

class VideoProcessing:
    def __init__(self, master):
        self.master = master
        self.video_processing_window = None
        self.images = []
        self.selected_index = None
        self.processing_label = None
        self.queue = queue.Queue()
        self.processing_thread = None
        self.animating = False

    def open_video_processing(self):
        if self.video_processing_window is not None and tk.Toplevel.winfo_exists(self.video_processing_window):
            self.video_processing_window.lift()
            return

        self.video_processing_window = tk.Toplevel(self.master)
        self.video_processing_window.title("Video Processing")
        self.center_window(self.video_processing_window, 600, 400)

        tk.Button(self.video_processing_window, text="Add Image and Audio", command=self.add_image_audio).pack(pady=10)
        tk.Button(self.video_processing_window, text="Delete Selected", command=self.delete_selected).pack(pady=10)
        tk.Button(self.video_processing_window, text="Create Video", command=self.create_video).pack(pady=10)

        self.canvas = Canvas(self.video_processing_window)
        self.scrollbar = Scrollbar(self.video_processing_window, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.configure(yscrollcommand=self.scrollbar.set, scrollregion=self.canvas.bbox("all"))

        self.frame = Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.frame.bind("<Configure>", self.on_frame_configure)

        self.video_processing_window.bind_all("<MouseWheel>", self.on_mouse_wheel)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def add_image_audio(self):
        self.queue.put(None)
        self.master.after(100, self.check_queue)

    def check_queue(self):
        try:
            task = self.queue.get_nowait()
        except queue.Empty:
            self.master.after(100, self.check_queue)
        else:
            self.select_image_audio()

    def select_image_audio(self):
        image_path = filedialog.askopenfilename(title="Select Image File", filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp *.ico")])
        if not image_path:
            return

        audio_path = filedialog.askopenfilename(title="Select Audio File", filetypes=[("Audio files", "*.wav *.mp3 *.aac *.flac *.ogg *.m4a *.wma"), ("All files", "*.*")])
        if not audio_path:
            return

        timestamp = simpledialog.askstring("Input", "Enter timestamp (MM:SS):", initialvalue="00:00")
        if not timestamp:
            return

        try:
            minutes, seconds = map(int, timestamp.split(':'))
            total_seconds = minutes * 60 + seconds
        except ValueError:
            messagebox.showerror("Error", "Invalid timestamp format!")
            return

        audio_duration = AudioFileClip(audio_path).duration
        self.images.append((image_path, audio_path, total_seconds, audio_duration))
        self.images.sort(key=lambda x: x[2])  # Sort by timestamp

        self.refresh_image_audio_blocks()

    def refresh_image_audio_blocks(self):
        for widget in self.frame.winfo_children():
            widget.destroy()  # Clear previous content

        for index, (img, audio, time, duration) in enumerate(self.images):
            self.add_image_audio_block(img, audio, time, duration, index)

        self.update_window_size()

    def add_image_audio_block(self, img, audio, time, duration, index):
        end_time = time + duration
        panel = Frame(self.frame, borderwidth=2, relief="groove")
        panel.pack(fill="x", pady=5, padx=10)
        panel.bind("<Button-1>", lambda event, idx=index: self.select_block(event, idx))

        # Display thumbnail
        thumbnail = Image.open(img)
        thumbnail.thumbnail((100, 100))
        thumb_img = ImageTk.PhotoImage(thumbnail)

        thumbnail_label = Label(panel, image=thumb_img)
        thumbnail_label.image = thumb_img  # Keep a reference to avoid garbage collection
        thumbnail_label.pack(side="left", padx=10)
        thumbnail_label.bind("<Button-1>", lambda event, idx=index: self.select_block(event, idx))

        # Display paths and timestamp
        text_frame = Frame(panel)
        text_frame.pack(side="left", fill="x", expand=True)
        text_frame.bind("<Button-1>", lambda event, idx=index: self.select_block(event, idx))
        wrap_length = self.video_processing_window.winfo_width() - 150  # Adjust wrap length based on window width

        labels = [
            Label(text_frame, text=f"Image: {img}", anchor="w", wraplength=wrap_length, justify="left"),
            Label(text_frame, text=f"Audio: {audio}", anchor="w", wraplength=wrap_length, justify="left"),
            Label(text_frame, text=f"Timestamp: {time // 60:02d}:{time % 60:02d}", anchor="w"),
            Label(text_frame, text=f"Audio Duration: {int(duration // 60):02d}:{int(duration % 60):02d}", anchor="w"),
            Label(text_frame, text=f"End Time: {int(end_time // 60):02d}:{int(end_time % 60):02d}", anchor="w")
        ]

        for label in labels:
            label.pack(fill="x")
            label.bind("<Button-1>", lambda event, idx=index: self.select_block(event, idx))

        panel.configure(bg="white")
        text_frame.configure(bg="white")

    def select_block(self, event, index):
        for panel in self.frame.winfo_children():
            panel.configure(bg="white")
            for widget in panel.winfo_children():
                widget.configure(bg="white")

        selected_panel = self.frame.winfo_children()[index]
        selected_panel.configure(bg="lightblue")
        for widget in selected_panel.winfo_children():
            widget.configure(bg="lightblue")

        self.selected_index = index

    def delete_selected(self):
        if hasattr(self, 'selected_index') and self.selected_index is not None:
            del self.images[self.selected_index]
            self.selected_index = None
            self.refresh_image_audio_blocks()

    def update_window_size(self):
        self.video_processing_window.update_idletasks()
        width = 600
        height = 400
        self.center_window(self.video_processing_window, width, height)

    def create_video(self):
        self.processing_label = Label(self.video_processing_window, text="Video is processing...", font=("Helvetica", 16))
        self.processing_label.pack(pady=20, anchor="n")
        self.animating = True
        threading.Thread(target=self.animate_processing).start()
        threading.Thread(target=self.process_image_audio).start()

    def animate_processing(self):
        def animate():
            while self.animating and self.processing_label.winfo_exists():
                for i in range(4):
                    if not self.animating:
                        break
                    self.master.after(0, self.update_processing_label, f"Video is processing{'.' * i}")
                    time.sleep(0.5)
        threading.Thread(target=animate).start()

    def update_processing_label(self, text):
        if self.processing_label and self.processing_label.winfo_exists():
            self.processing_label.config(text=text)

    def process_image_audio(self):
        clips = []
        fps = 1  # 默认帧率设置为1

        for i, (image_path, audio_path, start_time, duration) in enumerate(self.images):
            audio_clip = AudioFileClip(audio_path)
            image_clip = ImageClip(image_path).set_duration(audio_clip.duration).set_fps(fps)
            image_clip = image_clip.resize(height=720).set_position("center")
            image_clip = image_clip.set_audio(audio_clip)
            image_clip = image_clip.set_start(start_time)
            clips.append(image_clip)

            if i < len(self.images) - 1:
                next_start_time = self.images[i + 1][2]
                if next_start_time > start_time + audio_clip.duration:
                    blank_duration = next_start_time - (start_time + audio_clip.duration)
                    blank_clip = ImageClip(image_path).set_duration(blank_duration).set_start(start_time + audio_clip.duration).set_fps(fps)
                    blank_clip = blank_clip.resize(height=720).set_position("center")
                    clips.append(blank_clip)

        final_clip = concatenate_videoclips(clips, method="compose")
        output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 files", "*.mp4")])
        if output_path:
            final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=fps)
            messagebox.showinfo("Success", f"Video saved to {output_path}")
        self.animating = False
        self.processing_label.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    vp = VideoProcessing(root)
    vp.open_video_processing()
    root.mainloop()
