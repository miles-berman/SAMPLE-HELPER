import tkinter as tk
from tkinter import filedialog, LabelFrame
from sampler import Sample 
import threading
import time

class SamplerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SMPL-HLPR")
        self.geometry("600x450")

        self.sample = None
        self.last_pitch_value = 0  # To track the last pitch value

        self.left_panel = LabelFrame(self, text="File Info")
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Track Info
        self.track_info_label = tk.Label(self.left_panel, text="No file loaded", justify=tk.LEFT)
        self.track_info_label.pack(pady=10)

        # Load Button
        self.load_button = tk.Button(self.left_panel, text="Load Audio File", command=self.load_audio)
        self.load_button.pack(pady=10)

        # Right Panel for Controls
        self.right_panel = LabelFrame(self, text="Controls")
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bit Depth Slider
        self.bit_depth_slider = tk.Scale(self.right_panel, from_=4, to=16, orient=tk.HORIZONTAL, label="Bit Depth")
        self.bit_depth_slider.set(16)  # Default value
        self.bit_depth_slider.pack(pady=10)

        # Sample Rate Slider
        self.sample_rate_slider = tk.Scale(self.right_panel, from_=8000, to=48000, orient=tk.HORIZONTAL, label="Sample Rate", resolution=1000)
        self.sample_rate_slider.set(44100)  # Default value
        self.sample_rate_slider.pack(pady=10)

        # Pitch Slider
        self.pitch_slider = tk.Scale(self.right_panel, from_=-12, to=12, orient=tk.HORIZONTAL, label="Pitch (Semitones)")
        self.pitch_slider.pack(pady=10)

        # Play and Stop Buttons
        self.play_button = tk.Button(self.right_panel, text="Play", command=self.play_audio)
        self.play_button.pack(pady=5)
        self.stop_button = tk.Button(self.right_panel, text="Stop", command=self.stop_audio)
        self.stop_button.pack(pady=5)

        # Modify sliders to update on release
        self.bit_depth_slider.bind("<ButtonRelease-1>", lambda event: self.apply_changes())
        self.sample_rate_slider.bind("<ButtonRelease-1>", lambda event: self.apply_changes())
        self.pitch_slider.bind("<ButtonRelease-1>", lambda event: self.apply_pitch_change())

    def load_audio(self):
        if self.sample:
            self.sample.stop_audio()
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if file_path:
            self.sample = Sample(file_path)
            # Update track info label
            self.track_info_label.config(text=f"Loaded: {file_path.split('/')[-1]}\nSample Rate: {self.sample.sr} Hz\nLength: {self.sample.length_seconds} seconds\nChannels: {self.sample.channels}")

    def play_audio(self):
        if self.sample:
            threading.Thread(target=self.sample.play_audio, daemon=True).start()

    def stop_audio(self):
        if self.sample:
            self.sample.stop_audio()

    def apply_changes(self):
        if self.sample:
            threading.Thread(target=self.apply_audio_changes, daemon=True).start()

    def apply_pitch_change(self):
        time.sleep(0.1)
        if self.sample:
            new_pitch = self.pitch_slider.get()
            pitch_change = new_pitch - self.last_pitch_value
            self.last_pitch_value = new_pitch
            threading.Thread(target=self.sample.set_pitch, args=(pitch_change,), daemon=True).start()

    def apply_audio_changes(self):
        bit_depth = self.bit_depth_slider.get()
        sample_rate = self.sample_rate_slider.get()
        time.sleep(0.1)
        self.sample.lower_bd(bit_depth)
        time.sleep(0.1)
        self.sample.lower_sr(sample_rate)


app = SamplerApp()
app.mainloop()
