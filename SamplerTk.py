# 1/9/2024

import tkinter as tk
from tkinter import filedialog, LabelFrame
from SamplerClass import Sample 
import threading
import time

class SamplerApp(tk.Tk):
    
#----------------
# UI
#----------------
    
    def __init__(self):
        super().__init__()
        self.title("SMPL-HLPR")
        self.geometry("600x500")
        self.resizable(False, False)  # prevent window from being resizable

        self.sample = None
        self.last_pitch_value = 0  # track the last pitch, volume, & pan
        self.last_volume_value = 0
        self.last_pan_value = 0


        # LEFT
        self.left_panel = LabelFrame(self, text="File Info", width=220, height=430)
        self.left_panel.pack_propagate(False)  # prevent resizing of left_panel
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)


        # RIGHT
        self.right_panel = LabelFrame(self, text="Controls", width=380, height=430)
        self.right_panel.pack_propagate(False)  # prevent resizing of right_panel
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Screen
        self.track_info_label = tk.Label(self.left_panel, text="No file loaded", justify=tk.LEFT)
        self.track_info_label.pack(pady=10)

        self.load_button = tk.Button(self.left_panel, text="Load Audio File", command=self.load_audio)
        self.load_button.pack(pady=10)

        # Play & Stop
        self.play_button = tk.Button(self.left_panel, text="Play", command=self.play_audio)
        self.play_button.pack(pady=5)
        self.stop_button = tk.Button(self.left_panel, text="Stop", command=self.stop_audio)
        self.stop_button.pack(pady=5)

        # Bit Depth
        self.bit_depth_slider = tk.Scale(self.right_panel, from_=4, to=16, orient=tk.HORIZONTAL, label="Bit Depth")
        self.bit_depth_slider.set(16)  # default value
        self.bit_depth_slider.pack(pady=10)

        # Sample Rate
        self.sample_rate_slider = tk.Scale(self.right_panel, from_=8000, to=48000, orient=tk.HORIZONTAL, label="Sample Rate", resolution=1000)
        self.sample_rate_slider.set(44100)  # default value
        self.sample_rate_slider.pack(pady=10)

        # Pitch 
        self.pitch_slider = tk.Scale(self.right_panel, from_=-12, to=12, orient=tk.HORIZONTAL, label="Pitch (Semitones)")
        self.pitch_slider.pack(pady=10)

        # Volume
        self.volume_slider = tk.Scale(self.right_panel, from_=-20, to=20, resolution=1, orient=tk.HORIZONTAL, label="Volume (dB)")
        self.volume_slider.pack(pady=10)
    
        # Pan
        self.pan_slider = tk.Scale(self.right_panel, from_=-1, to=1, resolution=0.1, orient=tk.HORIZONTAL, label="Pan (L <> R)")
        self.pan_slider.pack(pady=10)

        # Bind sliders
        self.bit_depth_slider.bind("<ButtonRelease-1>", lambda event: self.apply_changes())
        self.sample_rate_slider.bind("<ButtonRelease-1>", lambda event: self.apply_changes())
        self.pitch_slider.bind("<ButtonRelease-1>", lambda event: self.apply_pitch_change())
        self.volume_slider.bind("<ButtonRelease-1>", lambda event: self.apply_volume_change())
        self.pan_slider.bind("<ButtonRelease-1>", lambda event: self.apply_pan_change())

    def reset_UI(self):
        # update track info label if a file is loaded
        if self.sample and self.sample.file_path:
            file_path = self.sample.file_path
            self.track_info_label.config(text=f"{file_path.split('/')[-1]}\nSample Rate: {self.sample.sr} Hz\nLength: {self.sample.length_seconds} seconds\nChannels: {self.sample.channels}")
        else:
            self.track_info_label.config(text="No file loaded")

        # Reset sliders to default values
        self.bit_depth_slider.set(16)
        self.sample_rate_slider.set(44100)
        self.pitch_slider.set(0)
        self.volume_slider.set(0)
        self.pan_slider.set(0)

        # Reset last values
        self.last_pitch_value = 0
        self.last_volume_value = 0
        self.last_pan_value = 0


#----------------
# Backend
#----------------

    # Load
    def load_audio(self):
        if self.sample:
            self.sample.stop_audio()
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3")])
        if file_path:
            self.sample = Sample(file_path)
            self.reset_UI()
            

    # Playback
    def play_audio(self):
        if self.sample:
            threading.Thread(target=self.sample.play_audio, daemon=True).start()

    def stop_audio(self):
        if self.sample:
            self.sample.stop_audio()

    # Volume Change
    def apply_volume_change(self):
        if self.sample:
            new_volume = self.volume_slider.get()
            volume_change = new_volume - self.last_volume_value
            self.last_volume_value = new_volume  # update last volume value
            threading.Thread(target=self.sample.set_volume, args=(volume_change,), daemon=True).start()


    # Pan Change
    def apply_pan_change(self):
        if self.sample:
            new_pan = self.pan_slider.get()
            pan_change = new_pan - self.last_pan_value
            self.last_pan_value = new_pan  # update last pan value
            threading.Thread(target=self.sample.set_pan, args=(pan_change,), daemon=True).start()


    # Sample Changes
    def apply_changes(self):
        if self.sample:
            threading.Thread(target=self.changes_helper, daemon=True).start()

    def apply_pitch_change(self):
        time.sleep(0.1)
        if self.sample:
            new_pitch = self.pitch_slider.get()
            pitch_change = new_pitch - self.last_pitch_value
            self.last_pitch_value = new_pitch
            threading.Thread(target=self.sample.set_pitch, args=(pitch_change,), daemon=True).start()

    def changes_helper(self):
        bit_depth = self.bit_depth_slider.get()
        sample_rate = self.sample_rate_slider.get()
        time.sleep(0.1)
        self.sample.lower_bd(bit_depth)
        time.sleep(0.1)
        self.sample.lower_sr(sample_rate)
        self.stop_audio()
        self.play_audio()


app = SamplerApp()
app.mainloop()
