# main_non_interactive.py
# Automated tester for Sampler class

from SamplerClass import Sample
import sys
import time

def main():
    if len(sys.argv) < 2:
        print("Usage: python main_non_interactive.py <audio file path>")
        return

    file_path = sys.argv[1]
    sample = Sample(file_path)

    if sample.err:
        print(f"Error: {sample.err}")
        return

    print(f"Loaded {file_path}.")
    print(f"Sample Rate: {sample.sr}, Channels: {sample.channels}, Length: {sample.length_seconds} seconds")

    # Automated Testing of Effects
    effects = [
        {"desc": "Lower Bit Depth to 8 bits", "func": lambda: sample.lower_bd(8)},
        {"desc": "Change Sample Rate to 22050 Hz", "func": lambda: sample.lower_sr(22050)},
        {"desc": "Increase Pitch by 2 semitones", "func": lambda: sample.set_pitch(2)},
        {"desc": "Increase Volume by 10 dB", "func": lambda: sample.set_volume(10)},
        {"desc": "Pan 50% to the right", "func": lambda: sample.set_pan(0.5)}
    ]

    for effect in effects:
        print(effect["desc"])
        effect["func"]()
        print("Playing modified audio for 5 seconds...")
        sample.play_audio()
        time.sleep(5)
        sample.stop_audio()
        print("Stopped playing.\n")
        # Reset the audio to original state
        sample.audio = sample.original_audio

    print("Finished automated testing of effects.")

if __name__ == "__main__":
    main()
