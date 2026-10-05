import os
import math
import wave
import struct

def create_wav(filename, duration_sec=3.0, sample_rate=44100, bird_type="robin"):
    num_samples = int(duration_sec * sample_rate)
    samples = []
    
    for i in range(num_samples):
        t = i / sample_rate
        val = 0.0
        
        if bird_type == "robin":
            # American Robin: cheerily-cheer-up trill (~3100Hz)
            freq = 3100 + 400 * math.sin(2 * math.pi * 3.5 * t)
            envelope = math.exp(-((t % 0.4 - 0.15) ** 2) / 0.01)
            val = 0.6 * math.sin(2 * math.pi * freq * t) * envelope
            
        elif bird_type == "cardinal":
            # Northern Cardinal: clear whistle down-sweep (~3300Hz peak)
            cycle = t % 0.5
            freq = 3600 - 600 * cycle
            envelope = math.sin(math.pi * (cycle / 0.5)) if cycle < 0.5 else 0
            val = 0.7 * math.sin(2 * math.pi * freq * t) * envelope
            
        elif bird_type == "chickadee":
            # Black-capped Chickadee: ~3400Hz
            if t < 0.4:
                freq = 3400
                env = math.sin(math.pi * (t / 0.4))
            elif 0.5 < t < 0.8:
                freq = 3200
                env = math.sin(math.pi * ((t - 0.5) / 0.3))
            elif t > 0.9:
                sub_t = (t - 0.9) % 0.25
                freq = 3500 + 200 * math.sin(2 * math.pi * 15 * sub_t)
                env = 0.8 if sub_t < 0.18 else 0.1
            else:
                env = 0
                freq = 3400
            val = 0.65 * math.sin(2 * math.pi * freq * t) * env
            
        elif bird_type == "bluejay":
            # Blue Jay: ~2900Hz
            cycle = t % 0.6
            freq = 2900 + 100 * math.sin(2 * math.pi * 8 * cycle)
            envelope = math.exp(-((cycle - 0.2) ** 2) / 0.03)
            val = 0.6 * math.sin(2 * math.pi * freq * t) * envelope
            
        else:
            freq = 3000
            val = 0.5 * math.sin(2 * math.pi * freq * t)
            
        final_sample = max(-1.0, min(1.0, val))
        int_sample = int(final_sample * 32767)
        samples.append(int_sample)
        
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        packed_data = bytearray()
        for sample in samples:
            packed_data.extend(struct.pack('<h', sample))
        wav_file.writeframes(packed_data)
    print(f"Generated sample: {filename}")

if __name__ == "__main__":
    out_dir = os.path.join("audio_samples")
    create_wav(os.path.join(out_dir, "american_robin.wav"), bird_type="robin")
    create_wav(os.path.join(out_dir, "northern_cardinal.wav"), bird_type="cardinal")
    create_wav(os.path.join(out_dir, "black_capped_chickadee.wav"), bird_type="chickadee")
    create_wav(os.path.join(out_dir, "blue_jay.wav"), bird_type="bluejay")
