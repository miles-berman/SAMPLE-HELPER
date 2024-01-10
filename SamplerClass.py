# 1/9/2024

import os
import threading
import time
import io

from pydub import AudioSegment
import numpy as np
import simpleaudio as sa
import wave



#-----------------
# Sample Class
#-----------------
# Class for wav, mp3, & m4a files. Allows sample rate, bit depth, and pitch changes. Stores Metadata as well

class Sample:
    def __init__(self, file_path):
        self.original_audio = None  # original, unaltered audio
        self.preMix_audio = None    # effected audio (pre-gain)
        self.audio = None           # currently modified audio

        self.file_path = file_path
        self.sr = None
        self.channels = None
        self.length_seconds = None

        self.play_obj = None # playback instance
        self.play_thread = None
        self.read_audio()

        self.err = None # error handler 

#-----------------
# Load & Save
#-----------------
    
    # read_audio
    # Reads & sets info from audio file (wav, mp3, & m4a)
    def read_audio(self):
        if not os.path.exists(self.file_path):
            self.err = "File does not exist."
            return

        if self.file_path.endswith('.wav'):
            if self._is_24bit_wav(self.file_path):
                self._convert_24bit_16bit()
            else:
                self.original_audio = AudioSegment.from_wav(self.file_path)
        elif self.file_path.endswith('.mp3'):
            self.original_audio = AudioSegment.from_mp3(self.file_path)
        elif self.file_path.endswith('.m4a'):
            self.original_audio = AudioSegment.from_file(self.file_path)
        else:
            self.err = "Unsupported file format."
            return

        self.audio = self.original_audio
        self.preMix_audio = self.audio

        self.sr = self.audio.frame_rate
        self.length_seconds = len(self.audio) / 1000.0
        self.channels = 'Mono' if self.audio.channels == 1 else 'Stereo'

    # _is_24bit_wav
    # Checks if the WAV file at the given file path is 24-bit.
    def _is_24bit_wav(self, file_path):
        with wave.open(file_path, 'r') as wav_file:
            sample_width = wav_file.getsampwidth()
        return sample_width == 3

    # _convert_24bit_16bit
    # Converts a 24-bit WAV file to 16-bit. Conversion is necessary, 24-bit audio not supported natively.
    def _convert_24bit_16bit(self):
        audio = AudioSegment.from_file(self.file_path, format='wav')

        buffer = io.BytesIO()
        audio.export(buffer, format="wav", parameters=["-acodec", "pcm_s16le"])
        buffer.seek(0)

        self.original_audio = AudioSegment.from_file(buffer, format="wav")

    # update_audio
    # Stores effected audio for non-destructive volume & panning
    def update_audio(self):
        self.preMix_audio = self.audio
            
    def save_audio(self, save_path):
        if self.audio:
            file_format = 'wav' if save_path.endswith('.wav') else 'mp3'
            
            if not file_format:
                self.err = "Unsupported file format for saving."
                return
            self.audio.export(save_path, format=file_format)
        else:
            self.err = "No audio loaded to save."
            
#-----------------
# Playback
#-----------------    
    
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


    # _play_audio_thread
    # Private thread for audio playback
    def _play_audio_thread(self):
        audio_data = np.array(self.audio.get_array_of_samples())
        
        if self.audio.sample_width == 2:
            audio_data = audio_data.astype(np.int16)
        elif self.audio.sample_width == 4:
            audio_data = audio_data.astype(np.int32)

        audio_frames = audio_data.tobytes()
        self.play_obj = sa.play_buffer(audio_frames, self.audio.channels, 2, self.sr)  # Using 2 bytes per sample for playback
        self.play_obj.wait_done()

    # set_volume
    # Sets volume to given db level
    def set_volume(self, gain_db):
        if self.preMix_audio:
            self.audio = self.preMix_audio
            self.audio += gain_db


    # set_pan
    # Sets pan by decreasing opposite channel volume. 
    def set_pan(self, pan):
        print("X")
        if self.preMix_audio and self.preMix_audio.channels == 2:
            self.audio = self.preMix_audio
            left, right = self.audio.split_to_mono()
            
            # Pan range: -1.0 (full left) to 1.0 (full right)
            if pan < 0:  # Pan left
                right = right - abs(pan) * 20 # reduce right channel volume
            elif pan > 0:  # Pan right
                left = left - abs(pan) * 20 # reduce left channel volume

            self.audio = AudioSegment.from_mono_audiosegments(left, right)

#-----------------
# Effects
#-----------------
    
    # lower_bd
    # Resamples & lowers bit depth
    def lower_bd(self, target_bit_depth):
        audio_data = np.array(self.original_audio.get_array_of_samples())

        if self.audio.sample_width == 2: # set np array to correct size
            audio_data = audio_data.astype(np.int16)
        elif self.audio.sample_width == 4:
            audio_data = audio_data.astype(np.int32)
        else:
            audio_data = audio_data.astype(np.int64)

        factor = 2 ** (16 - target_bit_depth) # bit depth math
        lowered_audio_data = (audio_data // factor) * factor

        self.audio = self.original_audio._spawn(lowered_audio_data.tobytes())
        self.update_audio()

    # lower_sr
    # Resamples & lowers sample rate
    def lower_sr(self, target_sr):
        self.audio = self.audio.set_frame_rate(target_sr).set_frame_rate(self.sr) # easy sample rate change w/pydub
        self.update_audio()


    # set_pitch
    # Change the pitch of the audio (semitones)
    def set_pitch(self, semitones):
        new_sr = int(self.audio.frame_rate * (2 ** (semitones / 12.0))) # change sample rate for pitched audio
        shifted_audio = self.audio._spawn(self.audio.raw_data, overrides={'frame_rate': new_sr})
        self.audio = shifted_audio.set_frame_rate(self.audio.frame_rate)
        self.update_audio()


