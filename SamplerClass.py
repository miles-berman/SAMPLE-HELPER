# 1/9/2024

import os
import threading
import time

from pydub import AudioSegment
import numpy as np
import simpleaudio as sa


#-----------------
# Sample Class
#-----------------
# Class for wav and mp3 files. Allows sample rate, bit depth, and pitch changes. Stores Metadata as well
class Sample:
    def __init__(self, file_path):
        self.original_audio = None  # original, unaltered audio
        self.audio = None           # currently modified audio

        self.file_path = file_path
        self.sr = None
        self.channels = None
        self.length_seconds = None

        self.play_obj = None # playback instance
        self.play_thread = None
        self.read_audio()

        self.err = None # error handler 

    # read_audio
    # Reads & sets info from audoi file (wav + mp3)
    def read_audio(self):
        if not os.path.exists(self.file_path):
            self.err = "File does not exist."
            return

        if self.file_path.endswith('.wav'):
            self.original_audio = AudioSegment.from_wav(self.file_path)
        elif self.file_path.endswith('.mp3'):
            self.original_audio = AudioSegment.from_mp3(self.file_path)
        else:
            self.err = "Unsupported file format."
            return

        self.audio = self.original_audio  

        self.sr = self.audio.frame_rate
        self.length_seconds = len(self.audio) / 1000.0
        self.channels = 'Mono' if self.audio.channels == 1 else 'Stereo'

    # update_audio
    # Update main audio with current changes and restart if playing
    def update_audio(self):
        if self.play_thread and self.play_thread.is_alive():
            self.stop_audio()
            self.play_audio()

    # lower_bd
    # Resamples & lowers bit depth
    def lower_bd(self, target_bit_depth):
        audio_data = np.array(self.original_audio.get_array_of_samples())

        if self.audio.sample_width == 2: # set np array to correct size
            audio_data = audio_data.astype(np.int16)
        elif self.audio.sample_width == 4:
            audio_data = audio_data.astype(np.int32)

        factor = 2 ** (16 - target_bit_depth) # bit depth math
        lowered_audio_data = (audio_data // factor) * factor

        self.audio = self.original_audio._spawn(lowered_audio_data.tobytes())
        #self.update_audio()

    # lower_sr
    # Resamples & lowers sample rate
    def lower_sr(self, target_sr):
        self.audio = self.audio.set_frame_rate(target_sr).set_frame_rate(self.sr) # easy sample rate change w/pydub
        #self.update_audio()


    # set_pitch
    # Change the pitch of the audio (semitones)
    def set_pitch(self, semitones):
        new_sr = int(self.audio.frame_rate * (2 ** (semitones / 12.0))) # change sample rate for pitched audio
        shifted_audio = self.audio._spawn(self.audio.raw_data, overrides={'frame_rate': new_sr})
        self.audio = shifted_audio.set_frame_rate(self.audio.frame_rate)
        self.update_audio()


    # play_audio
    # Stops audio then plays from beginning
    def play_audio(self):
        self.stop_audio()  
        self.play_thread = threading.Thread(target=self._play_audio_thread)
        self.play_thread.start()

    # stop_audio
    # Stops play thread completely
    def stop_audio(self):
        if self.play_obj and self.play_obj.is_playing():
            self.play_obj.stop()
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join()


    def save_audio(self, save_path):
        if self.audio:
            file_format = 'wav' if save_path.endswith('.wav') else 'mp3'
            
            if not file_format:
                self.err = "Unsupported file format for saving."
                return
            self.audio.export(save_path, format=file_format)
        else:
            self.err = "No audio loaded to save."


    # _play_audio_thread
    # private thread for audio playback
    def _play_audio_thread(self):
        audio_data = np.array(self.audio.get_array_of_samples())
        if self.audio.sample_width == 2:
            audio_data = audio_data.astype(np.int16)
        elif self.audio.sample_width == 4:
            audio_data = audio_data.astype(np.int32)

        audio_frames = audio_data.tobytes()
        self.play_obj = sa.play_buffer(audio_frames, self.audio.channels, self.audio.sample_width, self.sr)
        self.play_obj.wait_done()



