# main.py
# tester for Sampler class.
from SamplerClass import Sample
import sys

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
        print("2. Lower Bit Depth")
        print("3. Lower Sample Rate")
        print("4. Change Pitch")
        print("5. Save Audio")
        print("6. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            sample.play_audio()
        elif choice == "2":
            bit_depth = int(input("Enter target bit depth: "))
            sample.lower_bd(bit_depth)
        elif choice == "3":
            sr = int(input("Enter target sample rate: "))
            sample.lower_sr(sr)
        elif choice == "4":
            semitones = float(input("Enter semitones to shift: "))
            sample.set_pitch(semitones)
        elif choice == "5":
            save_path = input("Enter path to save audio: ")
            sample.save_audio(save_path)
        elif choice == "6":
            break
        else:
            print("Invalid choice.")

    print("Exiting program.")

if __name__ == "__main__":
    main()
