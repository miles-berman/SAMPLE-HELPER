# wavTester.py


import wave
import os
import sys

def get_wav_properties(file_path):
    with wave.open(file_path, 'r') as wav_file:
        length = wav_file.getnframes()
        sample_rate = wav_file.getframerate()
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        duration = length / float(sample_rate)

    file_size = os.path.getsize(file_path)

    return {
        "Sample Rate": sample_rate,
        "Channels": channels,
        "Sample Width": sample_width,
        "Duration (seconds)": duration,
        "File Size (bytes)": file_size
    }

def print_properties(file_path):
    print(f"Properties for {file_path}:")
    try:
        properties = get_wav_properties(file_path)
        for key, value in properties.items():
            print(f"{key}: {value}")
    except wave.Error as e:
        print(f"Error reading file: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    if len(sys.argv) != 3:
        print("Please drag and drop two WAV files onto this script.")
        return

    file1, file2 = sys.argv[1], sys.argv[2]
    print_properties(file1)
    print("\n")
    print_properties(file2)

if __name__ == "__main__":
    main()
