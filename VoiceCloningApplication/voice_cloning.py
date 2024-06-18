import tkinter as tk
from tkinter import Label, StringVar, OptionMenu, messagebox, filedialog, scrolledtext
from TTS.api import TTS
import torch
import os
import time
from pydub import AudioSegment
import pygame
import threading
import queue
import nltk

nltk.download('punkt')
from nltk.tokenize import sent_tokenize, word_tokenize


class VoiceCloning:
    def __init__(self, master):
        self.master = master
        self.voice_cloning_window = None
        self.audio_path = None
        self.text_file_path = None
        self.output_dir = os.path.join(os.path.dirname(__file__), "Cloning_Output")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        pygame.mixer.init()
        self.output_filename = None
        self.temp_audio_path = None
        self.queue = queue.Queue()
        self.processing_label = None
        self.animating = False

    def open_voice_cloning(self):
        if not self.voice_cloning_window or not self.voice_cloning_window.winfo_exists():
            self.voice_cloning_window = tk.Toplevel(self.master)
            self.voice_cloning_window.title("Voice Cloning")
            self.center_window(self.voice_cloning_window, 600, 600)

            self.audio_label = Label(self.voice_cloning_window, text="No audio file or folder selected")
            self.audio_label.pack(pady=5)

            options_frame = tk.Frame(self.voice_cloning_window)
            options_frame.pack(pady=5)

            self.model_var = StringVar()
            self.model_var.set("Select a model")
            models = ["tts_models/multilingual/multi-dataset/xtts_v2", "tts_models/multilingual/multi-dataset/your_tts"]
            model_menu = OptionMenu(options_frame, self.model_var, *models, command=self.update_language_options)
            model_menu.pack(side="left", padx=5)

            self.language_var = StringVar()
            self.language_var.set("en")
            self.language_menu = OptionMenu(options_frame, self.language_var, "en")
            self.language_menu.pack(side="left", padx=5)

            tk.Button(self.voice_cloning_window, text="Select Audio File",
                      command=lambda: self.choose_audio_file(self.audio_label)).pack(pady=10)
            tk.Button(self.voice_cloning_window, text="Select Audio Folder",
                      command=lambda: self.choose_audio_folder(self.audio_label)).pack(pady=10)

            self.text_entry = scrolledtext.ScrolledText(self.voice_cloning_window, width=50, height=10, wrap=tk.WORD)
            self.text_entry.pack(pady=5)

            self.file_label = Label(self.voice_cloning_window, text="")
            self.file_label.pack(pady=5)

            file_frame = tk.Frame(self.voice_cloning_window)
            file_frame.pack(pady=5)
            tk.Button(file_frame, text="Select Text File", command=self.choose_text_file).pack(side="left", padx=5)
            tk.Button(file_frame, text="Remove Text File", command=self.remove_text_file).pack(side="left", padx=5)

            tk.Button(self.voice_cloning_window, text="Start Cloning", command=self.start_cloning_thread).pack(pady=10)

            # Adding playback and control buttons
            control_frame = tk.Frame(self.voice_cloning_window)
            control_frame.pack(pady=10)
            self.play_button = tk.Button(control_frame, text="Play", command=self.play_audio, state="disabled")
            self.play_button.pack(side="left", padx=5)
            self.pause_button = tk.Button(control_frame, text="Stop", command=self.pause_audio, state="disabled")
            self.pause_button.pack(side="left", padx=5)

    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def update_language_options(self, selected_model):
        if selected_model == "tts_models/multilingual/multi-dataset/xtts_v2":
            languages = ["en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", "zh-cn", "ja", "hu", "ko", "hi"]
        elif selected_model == "tts_models/multilingual/multi-dataset/your_tts":
            languages = ["en", "pt-br", "fr"]
        else:
            languages = ["en"]

        menu = self.language_menu["menu"]
        menu.delete(0, "end")
        for language in languages:
            menu.add_command(label=language, command=lambda value=language: self.language_var.set(value))
        self.language_var.set(languages[0])

    def animate_processing(self):
        def animate():
            while self.animating and self.processing_label and self.processing_label.winfo_exists():
                for i in range(4):
                    if not self.animating:
                        break
                    self.queue.put(("update_label", f"Processing{'.' * i}"))
                    time.sleep(0.5)

        threading.Thread(target=animate).start()

    def start_cloning_thread(self):
        if self.processing_label:
            self.processing_label.destroy()
        self.processing_label = None

        self.processing_label = Label(self.voice_cloning_window, text="Processing...", font=("Helvetica", 16))
        self.processing_label.pack(pady=10)
        self.animating = True
        self.animate_processing()

        thread = threading.Thread(target=self.start_cloning)
        thread.start()

    def start_cloning(self):
        text = self.text_entry.get("1.0", tk.END).strip()
        model = self.model_var.get()
        language = self.language_var.get()

        if not self.audio_path:
            self.queue.put(("error", "Please select an audio file or folder."))
            return

        if model == "Select a model":
            self.queue.put(("error", "Please select a TTS model."))
            return

        if not text and not self.text_file_path:
            self.queue.put(("error", "Please enter some text or select a text file."))
            return

        if text and self.text_file_path:
            self.queue.put(("error", "Please provide either text input or a text file, not both."))
            return

        if self.text_file_path:
            try:
                if self.text_file_path.endswith(".txt"):
                    with open(self.text_file_path, 'r', encoding='utf-8') as file:
                        text = file.read()
            except Exception as e:
                self.queue.put(("error", f"Cannot read the text file: {str(e)}"))
                return

        self.queue.put(("info", "Cloning in progress..."))
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            tts = TTS(model).to(device)
            audio_base_name = os.path.splitext(os.path.basename(self.audio_path))[0]
            current_time = time.strftime("%Y%m%d_%H%M%S")
            self.output_filename = os.path.join(self.output_dir, f"{audio_base_name}_{current_time}.wav")

            # Check if the selected path is a folder or a file
            if os.path.isdir(self.audio_path):
                combined_audio_path = os.path.join(self.output_dir, f"combined_{current_time}.wav")
                self.audio_path = self.combine_audio_files(self.audio_path, combined_audio_path)
                self.temp_audio_path = self.audio_path  # Save the temp audio path for later deletion
                print(f"Combined audio path: {self.audio_path}")

            # Convert to wav if necessary
            if not self.audio_path.endswith(".wav"):
                wav_audio_path = os.path.join(self.output_dir, f"{audio_base_name}_{current_time}_temp.wav")
                audio = AudioSegment.from_file(self.audio_path)
                audio.export(wav_audio_path, format="wav")
                self.audio_path = wav_audio_path

            # Check the token length and split if necessary
            sentences = self.split_text(text, max_tokens=300)
            combined_audio = AudioSegment.empty()

            for i, sentence in enumerate(sentences):
                temp_output = os.path.join(self.output_dir, f"{audio_base_name}_{current_time}_part_{i}.wav")
                tts.tts_to_file(text=sentence, speaker_wav=self.audio_path, language=language, file_path=temp_output)
                part_audio = AudioSegment.from_file(temp_output)
                combined_audio += part_audio
                os.remove(temp_output)  # Remove the temporary part audio file

            combined_audio.export(self.output_filename, format="wav")

            self.queue.put(("enable_buttons", None))
            self.queue.put(
                ("message", f"Voice cloning has been successfully completed and saved at: {self.output_filename}"))

            # Delete the temporary combined audio file if it exists
            if self.temp_audio_path and os.path.exists(self.temp_audio_path):
                os.remove(self.temp_audio_path)
                self.temp_audio_path = None
        except Exception as e:
            self.queue.put(("error", str(e)))
        finally:
            self.queue.put("done")

    def split_text(self, text, max_tokens):
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_tokens = 0

        for sentence in sentences:
            tokens = word_tokenize(sentence)
            if current_tokens + len(tokens) > max_tokens:
                chunks.append(' '.join(current_chunk))
                current_chunk = tokens
                current_tokens = len(tokens)
            else:
                current_chunk.extend(tokens)
                current_tokens += len(tokens)

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def combine_audio_files(self, folder_path, output_path):
        try:
            audio_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
                           f.endswith(('.mp3', '.wav', '.flac', '.ogg', '.m4a'))]
            combined = AudioSegment.empty()
            for file in audio_files:
                audio = AudioSegment.from_file(file)
                combined += audio
            combined.export(output_path, format="wav")
            return output_path
        except Exception as e:
            self.queue.put(("error", f"Failed to combine audio files: {str(e)}"))
            return None

    def choose_audio_file(self, label):
        self.audio_path = filedialog.askopenfilename(title="Select Audio File",
                                                     filetypes=[("Audio files", "*.wav *.mp3 *.flac *.ogg *.m4a")])
        if self.audio_path:
            label.config(text=f"Audio file selected: {self.audio_path}")
            self.voice_cloning_window.lift()

    def choose_audio_folder(self, label):
        self.audio_path = filedialog.askdirectory(title="Select Audio Folder")
        if self.audio_path:
            label.config(text=f"Audio folder selected: {self.audio_path}")
            self.voice_cloning_window.lift()

    def choose_text_file(self):
        self.text_file_path = filedialog.askopenfilename(title="Select Text File", filetypes=[("Text files", "*.txt")])
        if self.text_file_path:
            self.file_label.config(text=f"Text file selected: {self.text_file_path}")
            self.text_entry.delete("1.0", tk.END)
            self.voice_cloning_window.lift()

    def remove_text_file(self):
        self.text_file_path = None
        self.file_label.config(text="")

    def play_audio(self):
        if self.output_filename and os.path.exists(self.output_filename):
            pygame.mixer.music.load(self.output_filename)
            pygame.mixer.music.play()

    def pause_audio(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def process_queue(self):
        while not self.queue.empty():
            task = self.queue.get()
            if task == "done":
                if self.processing_label:
                    self.processing_label.destroy()
                self.processing_label = None
                self.animating = False
            elif isinstance(task, tuple) and task[0] == "error":
                messagebox.showerror("Error", task[1])
            elif isinstance(task, tuple) and task[0] == "info":
                messagebox.showinfo("Status", task[1])
            elif isinstance(task, tuple) and task[0] == "update_label":
                if self.processing_label:
                    self.processing_label.config(text=task[1])
            elif isinstance(task, tuple) and task[0] == "message":
                messagebox.showinfo("Success", task[1])
            elif isinstance(task, tuple) and task[0] == "enable_buttons":
                self.play_button.config(state="normal")
                self.pause_button.config(state="normal")

        self.master.after(100, self.process_queue)


if __name__ == "__main__":
    root = tk.Tk()
    vc = VoiceCloning(root)
    vc.open_voice_cloning()
    root.after(100, vc.process_queue)
    root.mainloop()
