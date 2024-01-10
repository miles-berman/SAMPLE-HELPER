# main.py
# tester for Sampler class

from SamplerClass import Sample
import sys
import time

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <audio file path>")
        return

    file_path = sys.argv[1]
    sample = Sample(file_path)

    if sample.err:
        print(f"Error: {sample.err}")
        return

    print(f"Loaded {file_path}.")
    print(f"Sample Rate: {sample.sr}, Channels: {sample.channels}, Length: {sample.length_seconds} seconds")

    # Example operations
    while True:
        print("\nOptions:")
        print("1. Play Audio")
        print("2. Stop Audio")
        print("3. Lower Bit Depth")
        print("4. Lower Sample Rate")
        print("5. Change Pitch")
        print("6. Adjust Volume")
        print("7. Adjust Pan")
        print("8. Save Audio")
        print("9. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            sample.play_audio()
        elif choice == "2":
            sample.stop_audio()
        elif choice == "3":
            bit_depth = int(input("Enter target bit depth: "))
            sample.lower_bd(bit_depth)
        elif choice == "4":
            sr = int(input("Enter target sample rate: "))
            sample.lower_sr(sr)
        elif choice == "5":
            semitones = float(input("Enter semitones to shift: "))
            sample.set_pitch(semitones)
        elif choice == "6":
            gain_db = float(input("Enter volume change in dB: "))
            sample.set_volume(gain_db)
        elif choice == "7":
            pan = float(input("Enter pan value (-1.0 to 1.0): "))
            sample.set_pan(pan)
        elif choice == "8":
            save_path = input("Enter path to save audio: ")
            sample.save_audio(save_path)
        elif choice == "9":
            break
        else:
            print("Invalid choice.")

        # Wait for the operation to take effect
        time.sleep(0.1)

    print("Exiting program.")

if __name__ == "__main__":
    main()
