import time
import numpy as np
from scipy.signal import resample
import wave

import audioread
import miniaudio
import sounddevice as sd


class Sample:
    def __init__(self, path):
        self.path = path

        self.audio_array = None
        self.sample_rate = None
        self.length = 0
        self.channels = 0

        self.original_array = None
        self.original_sample_rate = None

        self.read_audio()


#---------------
# Playback
#---------------

    # play_audio
    # Play audio from a numpy array using sounddevice
    def play_audio(self, blocking=True):
        self.stop_audio
        sd.play(self.audio_array, self.sample_rate)
        #sd.wait()  # wait until the audio is finished playing

    # stop_audio
    # Stops audio & resets array + sample rate
    def stop_audio(self):
        sd.stop()
        self.audio_array = np.copy(self.original_array)
        self.sample_rate = self.original_sample_rate


#---------------
# Read & Save
#---------------

    # read_audio
    # Reads an audio file (MP3 or WAV) using miniaudio and converts it to a numpy array.
    def read_audio(self):
        if self.path.endswith('.mp3'):
            audio_data = miniaudio.mp3_read_file_f32(self.path)
            self.audio_array = np.array(audio_data.samples, dtype=np.float32)
            self.sample_rate = audio_data.sample_rate
        elif self.path.endswith('.wav'):
            audio_data = miniaudio.wav_read_file_f32(self.path)
            self.audio_array = np.array(audio_data.samples, dtype=np.float32)
            self.sample_rate = audio_data.sample_rate
            with wave.open(self.path, 'rb') as wav_file:
                if wav_file.getsampwidth() == 3:
                    print("3-----------------")
                    #self.change_pitch(12)

        elif self.path.endswith('.m4a'):
            with audioread.audio_open(self.path) as f:
                self.sample_rate = f.samplerate
                num_channels = f.channels
                total_samples = int(f.duration * self.sample_rate)  # Convert to integer

                # Initialize audio_data array
                audio_data = np.zeros((total_samples, num_channels), dtype=np.float32)
                current_sample = 0
                for buf in f:
                    new_samples = np.frombuffer(buf, dtype='<i2').reshape(-1, num_channels) / 32768.0
                    samples_to_read = min(new_samples.shape[0], total_samples - current_sample)
                    audio_data[current_sample:current_sample + samples_to_read] = new_samples[:samples_to_read]
                    current_sample += samples_to_read
                    if current_sample >= total_samples:
                        break

                self.audio_array = audio_data
        else:
            raise ValueError("Unsupported file format. Supported formats are MP3, WAV, and M4A.")

        self.change_pitch(12)
        self.original_array = np.copy(self.audio_array)
        self.original_sample_rate = self.sample_rate

    # save_audio
    # Saves the modified audio data to a WAV file.
    def save_audio(self, output_path):
        if self.audio_array is None:
            raise ValueError("Audio data is empty. Nothing to save.")

        # Assuming the audio array is in floating point format (-1.0 to 1.0)
        # Convert it to 16-bit PCM format (int16) for WAV file
        pcm_data = np.int16(self.audio_array * 32767)  # Scale to int16 range

        with wave.open(output_path, 'wb') as wav_file:
            n_channels = 2 if (pcm_data.ndim > 1 and pcm_data.shape[1] == 2) else 1
            sampwidth = 2  # 2 bytes for 16-bit audio
            n_frames = pcm_data.shape[0]

            wav_file.setnchannels(n_channels)
            wav_file.setsampwidth(sampwidth)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(pcm_data.tobytes())


#---------------
# Effects!
#---------------

    # change_bit_depth
    # Change the bit depth of the audio data to a value between 1 and 16 bits.
    def change_bit_depth(self, target_bit_depth):
        if not 1 <= target_bit_depth <= 16:
            raise ValueError("Target bit depth must be between 1 and 16.")

        normalized_audio = (self.audio_array - self.audio_array.min()) / (self.audio_array.max() - self.audio_array.min()) # normalize audio data to the range 0 to 1

        max_val = 2**target_bit_depth - 1 # scale based on the target bit depth
        scaled_audio = (normalized_audio * max_val).astype(np.uint16)

        self.audio_array = ((scaled_audio / max_val) * (self.audio_array.max() - self.audio_array.min())) + self.audio_array.min() #convert back to the range of the original audio

    # change_sample_rate
    # Change the sample rate of the audio data by resampling.
    def change_sample_rate(self, new_sample_rate):
        num_samples = int(len(self.audio_array) * new_sample_rate / self.sample_rate)
        self.audio_array = resample(self.audio_array, num_samples)
        self.sample_rate = new_sample_rate


    # change_pitch
    # Change the pitch of the audio data by a number of semitones.
    def change_pitch(self, semitones):
        factor = 2 ** (semitones / 12)
        new_length = int(len(self.audio_array) / factor)
        self.audio_array = resample(self.audio_array, new_length)

    # adjust_volume
    # Multiplies audio array for gain
    def change_volume(self, gain):
        self.audio_array *= gain

    # pan_audio
    # Pans audio by decreasing opposite gain
    def change_pan(self, pan):
        if self.audio_array.ndim != 2 or self.audio_array.shape[1] != 2:
            print("Panning is only applicable to stereo audio.")
            return

        left_gain = np.cos((pan + 1) * np.pi / 4)
        right_gain = np.sin((pan + 1) * np.pi / 4)

        self.audio_array[:, 0] *= left_gain
        self.audio_array[:, 1] *= right_gain




