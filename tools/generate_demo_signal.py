#!/usr/bin/env python3
import os
import argparse
import numpy as np
import scipy.signal as signal

def generate_fsk(sample_rate, symbol_rate, freq_offset, duration, f_dev=50e3):
    # Instead of continuous noise, generate a bursty packet to emulate telemetry (key fob, drone)
    # We ignore `duration` for the active signal length, keeping it strictly < 50ms 
    # so that the triage tool (which only looks at the first 150ms) can see both the start and end of the burst.
    preamble = [1, 0] * 16
    sync_word = [1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 0]
    
    # Force a 20ms burst maximum
    target_burst_time = 0.02
    num_payload_symbols = int(target_burst_time * symbol_rate) - len(preamble) - len(sync_word)
    if num_payload_symbols < 0:
        num_payload_symbols = 100
        
    # Generate payload that repeats the hacker message "0xDEADBEEF "
    payload_text = "0xDEADBEEF "
    payload_bits = []
    for char in payload_text:
        bin_val = bin(ord(char))[2:].zfill(8)
        payload_bits.extend([int(b) for b in bin_val])
        
    repeats = (num_payload_symbols + len(payload_bits) - 1) // len(payload_bits)
    payload = (payload_bits * repeats)[:num_payload_symbols]
    
    bits = np.array(preamble + sync_word + payload)
    
    sps = int(sample_rate / symbol_rate)
    pulse_train = np.repeat(bits * 2 - 1, sps)
    
    b, a = signal.butter(4, 0.5)
    pulse_train = signal.filtfilt(b, a, pulse_train)
    
    phase = 2 * np.pi * f_dev * np.cumsum(pulse_train) / sample_rate
    t = np.arange(len(phase)) / sample_rate
    phase += 2 * np.pi * freq_offset * t
    iq = np.exp(1j * phase)
    
    # Create the full file duration padded with silence
    total_samples = int(sample_rate * duration)
    if total_samples < len(iq):
        total_samples = len(iq) + int(sample_rate * 0.1) # Minimum 100ms padding
        
    # Put the burst at exactly 0ms in (start of file) so the FSK bits appear immediately in explainable demod
    start_pad = 0
    end_pad = total_samples - len(iq) - start_pad
    if end_pad < 0: end_pad = 0
    
    noise_floor_start = (np.random.randn(start_pad) + 1j * np.random.randn(start_pad)) * 0.03
    noise_floor_end = (np.random.randn(end_pad) + 1j * np.random.randn(end_pad)) * 0.03
    
    packet_noise = (np.random.randn(len(iq)) + 1j * np.random.randn(len(iq))) * 0.03
    iq += packet_noise
    
    return np.concatenate([noise_floor_start, iq, noise_floor_end])

def generate_fm(sample_rate, freq_offset, duration):
    t = np.arange(int(duration * sample_rate)) / sample_rate
    # Simple FM voice/tone approximation (1kHz tone + some harmonics)
    audio = np.sin(2 * np.pi * 1000 * t) + 0.5 * np.sin(2 * np.pi * 2000 * t)
    f_dev = 5000  # 5kHz deviation for narrowband FM (e.g. marine VHF)
    phase = 2 * np.pi * f_dev * np.cumsum(audio) / sample_rate
    phase += 2 * np.pi * freq_offset * t
    iq = np.exp(1j * phase)
    noise = (np.random.randn(len(iq)) + 1j * np.random.randn(len(iq))) * 0.05
    return iq + noise

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["gmsk", "fsk", "fm"], default="gmsk")
    parser.add_argument("--duration", type=float, default=0.5)
    parser.add_argument("--sample_rate", type=float, default=2048000)
    parser.add_argument("--freq_offset", type=float, default=0)
    parser.add_argument("--output_file", type=str, default="demo_capture.cf32")
    args = parser.parse_args()

    if args.type in ["gmsk", "fsk"]:
        iq = generate_fsk(args.sample_rate, 100000, args.freq_offset, args.duration, f_dev=50000)
    else:
        iq = generate_fm(args.sample_rate, args.freq_offset, args.duration)
    
    out_dir = os.path.dirname(os.path.abspath(args.output_file))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)
        
    iq.astype(np.complex64).tofile(args.output_file)
    print(f"Generated {args.type} signal at: {args.output_file} ({len(iq)} samples)")

if __name__ == "__main__":
    main()
