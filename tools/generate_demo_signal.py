#!/usr/bin/env python3
import os
import sys
import json
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

def generate_analog_video(sample_rate, standard, duration, freq_offset, fm_deviation, audio_subcarrier=False, image=None):
    """Synthesize a wideband-FM analog composite-video (CVBS) signal in the style of
    5.8 GHz FPV. Returns (iq_complex64, line_hz, num_lines, label)."""
    if standard == "ntsc":
        line_hz, num_lines, label = 15734.0, 525, "AnalogVideoNtsc"
    else:
        line_hz, num_lines, label = 15625.0, 625, "AnalogVideoPal"

    total = int(duration * sample_rate)
    t = np.arange(total) / sample_rate
    line_phase = (t * line_hz) % 1.0                 # 0..1 within each scan line
    line_idx = (t * line_hz).astype(np.int64)

    # Composite baseband: sync tip most negative, blanking ~0, white +1.
    sync_frac = 4.7e-6 * line_hz                      # H-sync width as a fraction of a line
    back = sync_frac + 0.06
    composite = np.zeros(total, dtype=np.float64)
    composite[line_phase < sync_frac] = -0.3         # horizontal sync tips
    active = (line_phase >= back) & (line_phase < 0.99)
    x = np.clip((line_phase - back) / (0.99 - back), 0.0, 1.0)
    if image is not None:
        # Map (frame line, horizontal position) -> image pixel luma (0..1)
        h, w = image.shape
        frame_line = line_idx % num_lines
        rows = np.clip((frame_line / num_lines * h).astype(int), 0, h - 1)
        cols = np.clip((x * w).astype(int), 0, w - 1)
        luma = image[rows, cols].astype(np.float64) / 255.0
    else:
        luma = np.floor(x * 8.0) / 7.0                # 8-step vertical bar test pattern
    composite[active] = luma[active]
    # Vertical-blanking marker on the first lines of each frame: gives the frame-rate
    # periodicity that analyze_video_standard() uses to count lines/frame.
    vbi = (line_idx % num_lines) < 10
    composite[active & vbi] = 0.0

    composite -= composite.mean()                    # zero-mean modulating signal

    if audio_subcarrier:                             # optional 6.5 MHz FM audio (1 kHz tone)
        composite = composite + 0.12 * np.cos(2 * np.pi * 6.5e6 * t + 2.0 * np.sin(2 * np.pi * 1000.0 * t))

    phase = 2 * np.pi * fm_deviation * np.cumsum(composite) / sample_rate
    phase += 2 * np.pi * freq_offset * t
    iq = np.exp(1j * phase)
    iq += (np.random.randn(total) + 1j * np.random.randn(total)) * 0.02
    return iq.astype(np.complex64), line_hz, num_lines, label


def write_sigmf_meta(data_path, sample_rate, center_hz, fm_deviation, label, freq_offset, occupied, num_samples):
    """Write a SigMF .sigmf-meta sidecar next to a raw cf32 capture."""
    meta = {
        "global": {
            "core:datatype": "cf32_le",
            "core:sample_rate": sample_rate,
            "core:version": "1.0.0",
            "fpv:fm_deviation": fm_deviation,
        },
        "captures": [{"core:frequency": center_hz, "core:sample_start": 0}],
        "annotations": [{
            "core:sample_start": 0,
            "core:sample_count": num_samples,
            "core:freq_lower_edge": center_hz + freq_offset - occupied / 2.0,
            "core:freq_upper_edge": center_hz + freq_offset + occupied / 2.0,
            "core:label": label,
        }],
    }
    meta_path = os.path.splitext(data_path)[0] + ".sigmf-meta"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    return meta_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["gmsk", "fsk", "fm", "analog_video"], default="gmsk")
    parser.add_argument("--standard", choices=["ntsc", "pal"], default="ntsc", help="Analog video standard (analog_video type)")
    parser.add_argument("--duration", type=float, default=None)
    parser.add_argument("--sample_rate", type=float, default=None)
    parser.add_argument("--freq_offset", type=float, default=0)
    parser.add_argument("--fm_deviation", type=float, default=2.0e6, help="FM peak deviation for analog_video (Hz)")
    parser.add_argument("--audio_subcarrier", action="store_true", help="Add a 6.5 MHz FM audio subcarrier (analog_video)")
    parser.add_argument("--image", type=str, default=None, help="Path to an image to transmit as the video content (analog_video; default is a test-bar pattern)")
    parser.add_argument("--output_file", type=str, default="demo_capture.cf32")
    args = parser.parse_args()

    # Per-type sensible defaults (analog video needs a much higher rate)
    if args.sample_rate is None:
        args.sample_rate = 20.0e6 if args.type == "analog_video" else 2048000.0
    if args.duration is None:
        args.duration = 0.1 if args.type == "analog_video" else 0.5

    out_dir = os.path.dirname(os.path.abspath(args.output_file))
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    if args.type == "analog_video":
        video_image = None
        if args.image:
            import cv2
            video_image = cv2.imread(args.image, cv2.IMREAD_GRAYSCALE)
            if video_image is None:
                print(f"Error: could not read image {args.image}", file=sys.stderr)
                sys.exit(1)
        iq, line_hz, num_lines, label = generate_analog_video(
            args.sample_rate, args.standard, args.duration, args.freq_offset,
            args.fm_deviation, args.audio_subcarrier, image=video_image)
        iq.tofile(args.output_file)
        occupied = 2.0 * (args.fm_deviation + 2.0e6)
        meta_path = write_sigmf_meta(args.output_file, args.sample_rate, 5_800_000_000,
                                     args.fm_deviation, label, args.freq_offset, occupied, len(iq))
        sub = " + 6.5 MHz audio subcarrier" if args.audio_subcarrier else ""
        print(f"Generated {args.standard.upper()} analog video{sub} at: {args.output_file} "
              f"({len(iq)} samples @ {args.sample_rate / 1e6:.1f} MSPS)")
        print(f"Wrote SigMF metadata: {meta_path}")
        return

    if args.type in ["gmsk", "fsk"]:
        iq = generate_fsk(args.sample_rate, 100000, args.freq_offset, args.duration, f_dev=50000)
    else:
        iq = generate_fm(args.sample_rate, args.freq_offset, args.duration)

    iq.astype(np.complex64).tofile(args.output_file)
    print(f"Generated {args.type} signal at: {args.output_file} ({len(iq)} samples)")


if __name__ == "__main__":
    main()
