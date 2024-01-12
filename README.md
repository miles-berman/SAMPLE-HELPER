# SMPL-HLPR
A python "sampler" to change bit depth, sample rate, and pitch of WAV, MP3, & M4A files. 
The app allows users to load files and manipulate the audio in real-time. Users can adjust the bit depth, sample rate, and pitch of the audio, and apply these changes on the fly.

## Features

- Load WAV, MP3, & M4A audio files
- Export Manipulated samples
- Play and pause audio playback
- Adjust the bit depth and sample rate of the audio
- Change the pitch of the audio in semitones
- Real-time audio manipulation with immediate feedback
- Save manipluations in a new file
- Supports 16, 24, and 32-bit samples

## Prerequisites

Before running the Python Audio Sampler, you need to have Python installed on your system. The app also depends on some Python libraries such as `tkinter` for the GUI, `miniaudio` for file reading, and `sounddevice` for audio playback.


## Quick Start

1. Clone the repository or download the source code.
2. Create a Virtual Environment (Optional but recommended):
   ```bash
   python3 -m venv venv
   ```
   Activate the virtual environment:
   - On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
   - On Windows:
   ```bash
   venv\Scripts\activate
   pip install -r requirements.txt
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements.txt
4. **Run the Application**:
- To run the GUI version:
  ```
  python SamplerTk.py
  ```
- To run the command line version, use:
  ```
  python main.py <audio_file_path>
  ```
  Replace `<audio_file_path>` with the path to your audio file.

## Usage

- After starting the application, load an audio file using the interface.
- Use the controls to adjust bit depth, sample rate, and pitch.
- Export or save the manipulated audio as needed.


