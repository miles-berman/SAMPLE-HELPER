# SampleHelper
A python "sampler" to change bit depth, sample rate, and pitch of wav &amp; mp3 files. 
The app allows users to load audio files (WAV and MP3), and manipulate the audio in real-time. Users can adjust the bit depth, sample rate, and pitch of the audio, and apply these changes on the fly.

## Features

- Load WAV and MP3 audio files
- Play and pause audio playback
- Adjust the bit depth and sample rate of the audio
- Change the pitch of the audio in semitones
- Real-time audio manipulation with immediate feedback
- Save manipluations in a new file

## Prerequisites

Before running the Python Audio Sampler, you need to have Python installed on your system. The app also depends on several Python libraries such as `tkinter` for the GUI, `pydub` for audio manipulation, and `simpleaudio` for audio playback.

You can install the required libraries using pip:

```bash
pip install pydub simpleaudio numpy
```

## Quick Start

1. Clone the repository or download the source code.
2. Install dependencies
3. Run the app:
4. ```bash
   python main.py <audio_file_path> (replace <audio_file_path> with the path to your audio file).
