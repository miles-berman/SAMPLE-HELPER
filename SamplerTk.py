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
        self.geometry("600x600")
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

        self.save_button = tk.Button(self.left_panel, text="Save Audio File", command=self.save_audio)
        self.save_button.pack(pady=10)

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
        self.pitch_slider.bind("<ButtonRelease-1>", lambda event: self.apply_changes())
        self.volume_slider.bind("<ButtonRelease-1>", lambda event: self.apply_changes())
        self.pan_slider.bind("<ButtonRelease-1>", lambda event: self.apply_changes())

        # LOOPER
        self.loop_start_slider = tk.Scale(self.left_panel, from_=0, to=10000, orient=tk.HORIZONTAL, label="Loop Start (ms)")
        self.loop_start_slider.pack(pady=5)

        self.loop_end_slider = tk.Scale(self.left_panel, from_=0, to=10000, orient=tk.HORIZONTAL, label="Loop End (ms)")
        self.loop_end_slider.pack(pady=5)

        self.loop_count_slider = tk.Scale(self.left_panel, from_=0, to=10, orient=tk.HORIZONTAL, label="Loop Count (0 for infinite)")
        self.loop_count_slider.pack(pady=5)

        self.set_loop_button = tk.Button(self.left_panel, text="Set Loop", command=self.set_loop)
        self.set_loop_button.pack(pady=10)

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

    def update_loop_sliders(self):
        if self.sample:
            max_length_ms = int(self.sample.length_seconds * 1000)
            self.loop_start_slider.config(to=max_length_ms)
            self.loop_end_slider.config(to=max_length_ms)



#----------------
# Backend
#----------------

    # Load
    def load_audio(self):
        if self.sample:
            self.sample.stop_audio()
        file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav *.mp3 *.m4a")])
        if file_path:
            self.sample = Sample(file_path)
            self.reset_UI()
            self.update_loop_sliders()

    # Save
    def save_audio(self):
        if self.sample and self.sample.audio:
            save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav"), ("MP3 files", "*.mp3")])
            if save_path:
                threading.Thread(target=self.sample.save_audio, args=(save_path,), daemon=True).start()
        else:
            tk.messagebox.showinfo("No Audio", "No audio loaded to save.")

            

    # Playback
    def play_audio(self):
        if self.sample:
            threading.Thread(target=self.sample.play_audio, daemon=True).start()

    def stop_audio(self):
        if self.sample:
            self.sample.stop_audio()

    # Sample Changes
    def apply_changes(self):
        if self.sample:
            threading.Thread(target=self.changes_helper, daemon=True).start()


    def changes_helper(self):
        bit_depth = self.bit_depth_slider.get()
        sample_rate = self.sample_rate_slider.get()
        pitch_change = self.pitch_slider.get()
        volume = self.volume_slider.get()
        pan = self.pan_slider.get()

        self.sample.lower_bd(bit_depth)
        time.sleep(0.01)
        self.sample.lower_sr(sample_rate)
        time.sleep(0.01)
        self.sample.set_pitch(pitch_change)
        time.sleep(0.01)
        self.sample.set_volume(volume)
        time.sleep(0.01)
        self.sample.set_pan(pan)
        time.sleep(0.01)
        self.sample.play_audio()

    def set_loop(self):
        if self.sample:
            loop_start = self.loop_start_slider.get()
            loop_end = self.loop_end_slider.get()
            loop_count = self.loop_count_slider.get()

            if loop_end <= loop_start:
                tk.messagebox.showwarning("Invalid Loop Range", "Loop end must be greater than loop start.")
                return

            self.sample.set_loop(loop_start, loop_end, loop_count)
            time.sleep(0.01)
            self.sample.play_audio()




app = SamplerApp()
app.mainloop()