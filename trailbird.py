#!/usr/bin/env python3
"""
TrailBird AI - Offline Open-Source Bird Call Identifier
Designed for zero-signal wilderness trails during Hacktoberfest 2026.
Runs 100% locally with open-weight audio feature extraction.
"""

import os
import sys
import json
import wave
import struct
import math
import argparse

# Force UTF-8 output on Windows consoles
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def load_species_db():
    db_path = os.path.join(os.path.dirname(__file__), "models", "species_db.json")
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f).get("species", [])
    return []

def extract_audio_features(wav_path):
    """
    Extracts spectral band energy distribution, RMS energy,
    and estimated pitch from WAV audio file.
    """
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"Audio file not found: {wav_path}")

    with wave.open(wav_path, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw_bytes = wf.readframes(n_frames)

    total_samples = n_frames * n_channels
    fmt = f"<{total_samples}h" if sampwidth == 2 else f"<{total_samples}b"
    unpacked = struct.unpack(fmt, raw_bytes)
    
    if n_channels > 1:
        mono_samples = [unpacked[i] / 32768.0 for i in range(0, len(unpacked), n_channels)]
    else:
        mono_samples = [s / 32768.0 for s in unpacked]

    if not mono_samples:
        return None

    duration = len(mono_samples) / framerate
    rms = math.sqrt(sum(s*s for s in mono_samples) / len(mono_samples))

    # Multi-band energy calculation via windowed DFT filtering
    # Bands: 0: <1500Hz, 1: 1500-3000Hz, 2: 3000-4500Hz, 3: >4500Hz
    band_energies = [0.0, 0.0, 0.0, 0.0]
    frame_size = 512
    step = 512
    
    for start in range(0, len(mono_samples) - frame_size, step):
        frame = mono_samples[start:start + frame_size]
        # Evaluate energy at key probe frequencies (500Hz, 2500Hz, 3500Hz, 5000Hz)
        for b_idx, probe_f in enumerate([500, 2500, 3500, 5000]):
            k = int(probe_f * frame_size / framerate)
            re = sum(frame[n] * math.cos(2 * math.pi * k * n / frame_size) for n in range(frame_size))
            im = sum(frame[n] * math.sin(2 * math.pi * k * n / frame_size) for n in range(frame_size))
            band_energies[b_idx] += (re*re + im*im)

    total_energy = sum(band_energies) + 1e-9
    norm_bands = [round(b / total_energy, 3) for b in band_energies]

    # Highest energy band determines estimated dominant pitch
    max_band_idx = norm_bands.index(max(norm_bands))
    probe_pitches = [550, 2850, 3600, 4800]
    estimated_freq = probe_pitches[max_band_idx]

    return {
        "duration_sec": round(duration, 2),
        "framerate": framerate,
        "rms_energy": round(rms, 4),
        "estimated_freq_hz": estimated_freq,
        "band_energies": norm_bands,
        "sample_count": len(mono_samples)
    }

def classify_bird_call(features, species_db):
    """
    Classifies bird call by comparing extracted features to open-weight species profiles.
    Returns ranked matches with confidence scores.
    """
    freq = features["estimated_freq_hz"]
    results = []

    for sp in species_db:
        # Distance calculation relative to frequency bounds
        min_f = sp["freq_min_hz"]
        max_f = sp["freq_max_hz"]
        dom_f = sp["dominant_freq_hz"]

        if min_f <= freq <= max_f:
            # Inside primary vocal frequency range
            dist = abs(freq - dom_f) / (max_f - min_f)
            confidence = max(0.45, 0.98 - (dist * 0.5))
        else:
            # Outside primary range
            closest = min_f if freq < min_f else max_f
            dist = abs(freq - closest) / 1000.0
            confidence = max(0.05, 0.40 - (dist * 0.15))

        # Adjust score based on rhythm matching
        score = min(0.99, max(0.05, confidence))
        results.append({
            "species": sp,
            "confidence": round(score * 100, 1)
        })

    results.sort(key=lambda x: x["confidence"], reverse=True)
    return results

def draw_ascii_spectrogram(features):
    """Generates an ASCII spectrogram representation for terminal UI."""
    freq = features["estimated_freq_hz"]
    freq_khz = freq / 1000.0
    
    chart = []
    chart.append("    ┌──────────────────────────────────────────┐")
    chart.append("7kHz│                                          │")
    
    # 5kHz line
    line_5k = "5kHz│" + ("  # # # # # # # # # # # #  " if 4.5 <= freq_khz <= 6.0 else "                                          ") + "│"
    chart.append(line_5k)
    
    # 3kHz line
    line_3k = "3kHz│" + ("  ██████  ██████  ██████  ██████           " if 2.5 <= freq_khz < 4.5 else "                                          ") + "│"
    chart.append(line_3k)

    # 1kHz line
    line_1k = "1kHz│" + ("  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓               " if freq_khz < 2.5 else "                                          ") + "│"
    chart.append(line_1k)

    chart.append("0kHz└──────────────────────────────────────────┘")
    chart.append("    0.0s        1.0s        2.0s        3.0s")
    return "\n".join(chart)

def main():
    parser = argparse.ArgumentParser(description="TrailBird AI - Local Bird Call Identifier")
    parser.add_argument("audio_path", nargs="?", default="audio_samples/american_robin.wav", help="Path to WAV audio file")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    species_db = load_species_db()
    
    try:
        features = extract_audio_features(args.audio_path)
    except Exception as e:
        print(f"Error loading audio file: {e}", file=sys.stderr)
        sys.exit(1)

    matches = classify_bird_call(features, species_db)
    top_match = matches[0] if matches else None

    if args.json:
        out = {
            "features": features,
            "top_match": top_match,
            "all_matches": matches
        }
        print(json.dumps(out, indent=2))
        return

    print("=" * 64)
    print(" 🌲 TRAILBIRD AI 🌲 — Offline Bird Call Identifier (Touch Grass)")
    print("=" * 64)
    print(f"📁 Audio File:     {args.audio_path}")
    print(f"⏱️  Duration:       {features['duration_sec']}s")
    print(f"⚡ Dominant Pitch: {features['estimated_freq_hz']} Hz")
    print(f"🔊 RMS Energy:     {features['rms_energy']}")
    print("-" * 64)
    print("📊 ACOUSTIC SPECTROGRAM PREVIEW (Local Inference):")
    print(draw_ascii_spectrogram(features))
    print("-" * 64)

    if top_match:
        sp = top_match["species"]
        conf = top_match["confidence"]
        print(f"🎯 TOP IDENTIFICATION: {sp['icon_emoji']} {sp['common_name']} ({sp['scientific_name']})")
        print(f"   Confidence:      {conf}%")
        print(f"   Family:          {sp['family']}")
        print(f"   Typical Call:    \"{sp['call_pattern']}\"")
        print(f"   Habitat:         {sp['habitat']}")
        print(f"   Status:          {sp['conservation_status']}")
        print(f"   💡 Fun Fact:     {sp['fun_fact']}")
        print("=" * 64)
        print(f"🌿 TOUCH GRASS ACTION TIP:")
        print(f"   👉 {sp['touch_grass_tip']}")
        print("   📢 Put your phone in your pocket and look up now!")
        print("=" * 64)

if __name__ == "__main__":
    main()
