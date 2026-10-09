"""
Wilderness Trail Explorer: A Choose Your Own Adventure CLI Game
Built with GitHub Copilot AI Prompt Assistance for MLH Global Hack Week.
"""

import time
import sys

def print_slow(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def start_adventure():
    print("=" * 65)
    print(" 🌲 WILDERNESS TRAIL EXPLORER — CHOOSE YOUR OWN ADVENTURE 🌲")
    print(" (Generated with GitHub Copilot AI Assistance)")
    print("=" * 65)
    print()

    print_slow("You step onto the Pine Ridge Trail. Deep canopy overhead, cell signal drops to ZERO.")
    print_slow("Suddenly, a melodious, whistle-like call echoes through the pine branches...\n")

    print("What do you do?")
    print("1. Pull out TrailBird AI to record & identify the bird call.")
    print("2. Quietly walk deeper into the birch grove toward the sound.")
    print("3. Sit on a mossy log and listen peacefully ('Touch Grass' mode).")
    
    choice = input("\nEnter choice (1, 2, or 3): ").strip()

    if choice == "1":
        print_slow("\n[Audio Spectrum Analyzer Active]")
        print_slow("FFT Pitch: 3400 Hz | Energy: High | Signal Match: 98.2%")
        print_slow("🎯 IDENTIFIED: Black-capped Chickadee (Poecile atricapillus)!")
        print_slow("💡 Action Tip: Look up 10ft into the birch forks. Put your phone in your pocket!")
        print_slow("\n🏆 VICTORY: You successfully identified the bird using open-weight local AI!")
    elif choice == "2":
        print_slow("\nAs you tread softly over pine needles, a curious Chickadee hops down to a low branch.")
        print_slow("It tilts its head, inspecting your boots, before fluttering off into the sunlight.")
        print_slow("\n🌿 VICTORY: An unforgettable close-up bird sighting on the trail!")
    else:
        print_slow("\nYou sit back on the log, close your eyes, and listen to the forest chorus.")
        print_slow("No screens, no notifications—just pure nature.")
        print_slow("\n🧘 TOUCH GRASS VICTORY: You achieved 100% wilderness zen!")

    print("\n" + "=" * 65)
    print("Thanks for playing Wilderness Trail Explorer! (Powered by Copilot & TrailBird AI)")
    print("=" * 65)

if __name__ == "__main__":
    start_adventure()
