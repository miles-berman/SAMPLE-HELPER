# main_non_interactive.py
# Automated tester for Sample class

from SampleClass import Sample

import sys
import time

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <audio file path>")
        return

    file_path = sys.argv[1]
    sample = Sample(file_path)

    print(f"Loaded {file_path}.")
    print(f"Sample Rate: {sample.sample_rate}, Channels: {sample.channels}, Length: {sample.length} seconds")

    # Automated Testing of Individual Effects
    effects = [
        {"desc": "Change Bit Depth to 8 bits", "func": lambda: sample.change_bit_depth(8)},
        {"desc": "Change Sample Rate to 22050 Hz", "func": lambda: sample.change_sample_rate(22050)},
        {"desc": "Increase Pitch by 2 semitones", "func": lambda: sample.change_pitch(2)},
        {"desc": "Increase Volume by a factor of 1.5", "func": lambda: sample.change_volume(1.5)},
        {"desc": "Pan 50% to the right", "func": lambda: sample.change_pan(0.5)}
    ]

    for effect in effects:
        print(effect["desc"])
        effect["func"]()
        print("Playing modified audio for 5 seconds...")
        sample.play_audio(blocking=False)
        time.sleep(5)
        sample.stop_audio()
        print("Stopped playing.\n")
        # Reset the audio to original state
        sample.audio_array = sample.original_array
        sample.sample_rate = sample.original_sample_rate

    # Combined Effects
    print("Applying a combination of effects...")
    sample.change_bit_depth(12)
    sample.change_sample_rate(32000)
    sample.change_pitch(1)
    sample.change_volume(1.2)
    sample.change_pan(0.3)
    print("Playing audio with combined effects for 5 seconds...")
    sample.play_audio(blocking=False)
    time.sleep(5)
    sample.stop_audio()
    print("Stopped playing combined effects.\n")

    print("Finished automated testing of effects.")

if __name__ == "__main__":
    main()
