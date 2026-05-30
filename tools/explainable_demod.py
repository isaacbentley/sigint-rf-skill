#!/usr/bin/env python3
import os
import sys
import json
import argparse
import numpy as np
from scipy import signal

HAS_MATPLOTLIB = False
try:
    import matplotlib
    matplotlib.use('Agg') # Headless
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    pass

def parse_args():
    parser = argparse.ArgumentParser(
        description="Explainable & Human-in-the-Loop RF Signal Demodulator"
    )
    parser.add_argument("--file", "-f", required=True, help="Path to IQ sample file")
    parser.add_argument("--rate", "-r", type=float, default=15.36e6, help="Sample rate in Hz")
    parser.add_argument("--freq", "-c", type=float, default=None, help="Assigned center frequency in Hz")
    parser.add_argument("--format", choices=["cf32_le", "ci16_le"], default="cf32_le", help="IQ format")
    parser.add_argument("--mode", choices=["fsk", "ook", "fm_audio", "am_audio", "analog_video", "psk", "qam"], required=True, help="Demodulation mode")
    
    # Mode-specific parameters
    parser.add_argument("--symbol-rate", type=float, default=250e3, help="Expected FSK/PSK/QAM symbol rate (baud)")
    parser.add_argument("--offset-hz", type=float, default=0.0, help="Manual frequency offset correction in Hz")
    parser.add_argument("--audio-rate", type=float, default=48000.0, help="Target FM audio sample rate")
    parser.add_argument("--line-samples", type=int, default=1280, help="PAL/NTSC video samples per line")
    parser.add_argument("--video-lines", type=int, default=576, help="Video active line count")
    parser.add_argument("--psk-order", type=int, default=4, help="Order of PSK (2=BPSK, 4=QPSK, 8=8PSK)")
    parser.add_argument("--qam-order", type=int, default=16, help="Order of QAM (16, 64, 256)")
    
    # Visualization
    parser.add_argument("--plot-path", default="demod_diagnostics.png", help="Path to save intermediate DSP diagnostics plot")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed DSP steps and logic")
    parser.add_argument("--output-bits", default=None, help="Path to write recovered FSK bits as a text file (one char per bit, newline every 128 bits)")
    
    return parser.parse_args()

def explain_step(title, description, math_formula=None):
    print(f"\n💡 [DSP STEP] {title}")
    print(f"   Description: {description}")
    if math_formula:
        print(f"   Formula:     {math_formula}")
    print("-" * 60)

def load_iq(filepath, datatype):
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}", file=sys.stderr)
        sys.exit(1)
    
    explain_step(
        "Loading IQ Samples",
        f"Reading raw IQ data from {os.path.basename(filepath)} using format {datatype}.",
        "Complex Sample = I[n] + j*Q[n]"
    )
    
    if datatype == "cf32_le":
        raw = np.fromfile(filepath, dtype=np.float32)
        if len(raw) % 2 != 0:
            raw = raw[:-1]
        samples = raw[0::2] + 1j * raw[1::2]
    else: # ci16_le
        raw = np.fromfile(filepath, dtype=np.int16)
        if len(raw) % 2 != 0:
            raw = raw[:-1]
        samples = (raw[0::2] + 1j * raw[1::2]) / 32768.0
        
    print(f"   Successfully loaded {len(samples)} complex samples.")
    return samples

def apply_frequency_shift(samples, sample_rate, offset_hz):
    """
    Shifts the entire frequency spectrum of the baseband IQ samples by a given offset.
    
    Educational Note: 
    Multiplying a time-domain signal by a complex exponential e^(-j*2*pi*f*t) shifts its 
    entire frequency spectrum by 'f' Hz. This is exactly how we computationally "tune" 
    a radio after it has already been recorded!
    """
    if offset_hz == 0:
        return samples
        
    explain_step(
        "Frequency Shift Correction",
        f"Correcting a manual frequency offset of {offset_hz / 1e3:+.2f} kHz relative to the center frequency.",
        "x_shifted[n] = x[n] * e^{-j * 2*pi * f_offset * n / f_s}"
    )
    
    t = np.arange(len(samples)) / sample_rate
    shifted = samples * np.exp(-1j * 2 * np.pi * offset_hz * t)
    return shifted

def demodulate_fm(samples, sample_rate):
    """
    Extracts the instantaneous frequency of an FM signal using a Quadrature Phase Discriminator.
    
    Educational Note:
    Instead of calculating the absolute phase of every sample (which wraps around at 2*pi 
    and causes massive spikes), we multiply the current sample by the complex conjugate 
    of the previous sample. The angle of this resulting vector is the phase difference, 
    which gives us a clean, continuous instantaneous frequency!
    """
    explain_step(
        "FM Quadrature Demodulator (Phase Discriminator)",
        "Computing the phase difference between adjacent samples to extract instantaneous frequency.",
        "y[n] = angle(x[n] * conj(x[n-1])) * f_s / (2*pi)"
    )
    
    # Avoid phase wrapping anomalies by multiplying adjacent complex samples
    phase_diff = np.angle(samples[1:] * np.conjugate(samples[:-1]))
    inst_freq = phase_diff * sample_rate / (2 * np.pi)
    
    # Remove remaining minor DC tuning error
    dc_offset = np.mean(inst_freq)
    inst_freq_corrected = inst_freq - dc_offset
    
    print(f"   Extracted frequency envelope. Measured average DC tuning error: {dc_offset/1e3:+.2f} kHz.")
    return inst_freq_corrected

def process_fsk(samples, sample_rate, symbol_rate, plot_path, verbose=False):
    """
    Demodulates Frequency Shift Keying (FSK/GFSK) signals into raw binary bits.
    
    This function performs FM demodulation, mathematically recovers the symbol clock 
    by finding the widest opening in the "eye diagram", and slices the result into bits.
    """
    # 1. FM Demodulation
    demod = demodulate_fm(samples, sample_rate)
    
    # 2. Clock Recovery
    samples_per_symbol = sample_rate / symbol_rate
    explain_step(
        "Symbol Clock Recovery (Variance-Maximization)",
        f"Searching for the optimal decimation phase offset. Expected Samples per Symbol (Sps): {samples_per_symbol:.2f}.\n"
        f"   We scan all possible integer offsets from 0 to {int(samples_per_symbol)-1}.\n"
        f"   The offset that maximizes the variance of the decimated signal aligns with the center of the 'eye' diagram.",
        "Variance[offset] = Var( demod[offset :: samples_per_symbol] )"
    )
    
    sps_int = int(np.round(samples_per_symbol))
    if sps_int < 2:
        print(f"Error: Sample rate {sample_rate/1e6:.2f} MHz is too low for symbol rate {symbol_rate/1e3:.2f} kHz.", file=sys.stderr)
        sys.exit(1)
        
    variances = []
    offsets = list(range(sps_int))
    
    # Make sure we don't index past length
    for offset in offsets:
        decim = demod[offset::sps_int]
        # Educational Note: A filtered digital pulse creates an "eye pattern" over time. 
        # The point where the variance (energy spread) is highest is exactly where the 
        # "eye" is widest open, which is the perfect, noise-free spot to sample our bit!
        variances.append(np.var(decim))
        
    best_offset = np.argmax(variances)
    explain_step(
        "Optimal Phase Selected",
        f"Scanned {sps_int} phases. Phase index {best_offset} yielded the maximum variance of {variances[best_offset]:.4e}.",
        f"Selected Offset = {best_offset}"
    )
    
    if verbose:
        print("   Variance Sweep Details:")
        for off, var in zip(offsets, variances):
            indicator = "⭐" if off == best_offset else "  "
            print(f"     Offset {off:02d}: Var = {var:.4e} {indicator}")
            
    # Slicing
    sliced_wave = demod[best_offset::sps_int]
    bits = (sliced_wave > 0).astype(int)
    
    explain_step(
        "Bit Slicing / Hard Decisions",
        "Converting frequency offsets to binary data. positive frequency -> 1, negative frequency -> 0.",
        "Bit[n] = 1 if Freq[n] > 0 else 0"
    )
    
    # Render Diagnostics Plot (Eye Diagram & Variance)
    if HAS_MATPLOTLIB:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot Variance curve
        ax1.plot(offsets, variances, marker='o', color='tab:purple')
        ax1.axvline(best_offset, color='tab:red', linestyle='--', label=f'Best Offset ({best_offset})')
        ax1.set_title("Clock Recovery Phase Sweep")
        ax1.set_xlabel("Sample Phase Offset")
        ax1.set_ylabel("Variance")
        ax1.grid(True, alpha=0.5)
        ax1.legend()
        
        # Plot Eye Diagram (overlaying 100 symbol segments)
        ax2.set_title("FSK Eye Diagram (Demodulated Frequency)")
        ax2.set_xlabel("Sample Offset in Symbol Period")
        ax2.set_ylabel("Frequency Deviation (Hz)")
        
        num_eyes = min(100, len(demod) // (sps_int * 2))
        eye_len = sps_int * 2
        for i in range(num_eyes):
            start = i * sps_int
            end = start + eye_len
            if end < len(demod):
                ax2.plot(demod[start:end], color='tab:blue', alpha=0.1)
                
        # Draw slicing threshold and sample points
        ax2.axhline(0, color='tab:red', linestyle=':', label='Slicing Threshold')
        ax2.axvline(best_offset, color='tab:green', linestyle='--', alpha=0.7, label='Sampling Points')
        ax2.axvline(best_offset + sps_int, color='tab:green', linestyle='--', alpha=0.7)
        ax2.legend(loc='lower right')
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"🎨 Saved DSP diagnostic eye diagram to: {plot_path}")
        
    return bits, sliced_wave

def process_fm_audio(samples, sample_rate, audio_rate):
    """
    Demodulates wideband or narrowband FM into an audio waveform.
    
    This function performs FM demodulation, severely decimates the high-speed RF 
    samples down to an audible rate (e.g. 48kHz), and applies a standard 75µs 
    de-emphasis filter to undo the pre-emphasis applied by FM broadcasters.
    """
    # 1. FM Demodulation
    demod = demodulate_fm(samples, sample_rate)
    
    explain_step(
        "Audio Decimation Filter",
        f"Downsampling frequency demodulated wave from {sample_rate/1e6:.2f} MSPS to audio rate {audio_rate/1e3:.1f} kHz.",
        "y_audio[n] = decimate( y_fm[n], factor )"
    )
    
    decim_factor = int(sample_rate / audio_rate)
    if decim_factor > 1:
        audio_raw = signal.decimate(demod, decim_factor)
    else:
        audio_raw = demod
        
    explain_step(
        "FM De-emphasis Filtering",
        "Applying a low-pass de-emphasis filter with a 75 µs time constant to restore audio balance.",
        "H(z) = alpha / (1 - (1 - alpha)*z^-1)"
    )
    
    tau = 75e-6
    alpha = 1.0 / (1.0 + (tau * audio_rate))
    audio_deemph = signal.lfilter([alpha], [1.0, -(1.0 - alpha)], audio_raw)
    
    # Normalize to prevent clipping
    audio_out = audio_deemph / (np.max(np.abs(audio_deemph)) + 1e-12)
    return audio_out

def process_am_audio(samples, sample_rate, audio_rate):
    """
    Demodulates Amplitude Modulation (AM) into an audio waveform.
    
    This uses a simple envelope detector followed by a DC-blocking (AC coupling) filter
    to remove the strong carrier wave, leaving only the riding audio wave behind.
    """
    explain_step(
        "AM Envelope Detection (Amplitude Demodulator)",
        "Computing the absolute magnitude of complex IQ samples to recover the amplitude envelope.",
        "y[n] = abs(x[n]) = sqrt( I[n]^2 + Q[n]^2 )"
    )
    envelope = np.abs(samples)
    
    explain_step(
        "DC Component Removal (AC Coupling)",
        "Subtracting the mean amplitude of the carrier wave to isolate the audio message.",
        "y_ac[n] = y[n] - Mean(y)"
    )
    audio_ac = envelope - np.mean(envelope)
    
    explain_step(
        "Audio Decimation Filter",
        f"Downsampling from {sample_rate/1e6:.2f} MSPS to audio rate {audio_rate/1e3:.1f} kHz.",
        "y_audio[n] = decimate( y_ac[n], factor )"
    )
    decim_factor = int(sample_rate / audio_rate)
    if decim_factor > 1:
        if len(audio_ac) > 27 * decim_factor:
            audio_raw = signal.decimate(audio_ac, decim_factor)
        else:
            audio_raw = audio_ac[::decim_factor]
    else:
        audio_raw = audio_ac
        
    # Normalize to prevent clipping
    audio_out = audio_raw / (np.max(np.abs(audio_raw)) + 1e-12)
    return audio_out

def process_ook(samples, sample_rate, plot_path, verbose=False):
    """
    Demodulates On-Off Keying (OOK) or Amplitude Shift Keying (ASK) signals.
    
    OOK is widely used in simple ISM band devices (key fobs, weather stations). 
    This function traces the amplitude envelope, calculates a dynamic threshold, 
    and slices the signal into discrete digital pulses.
    """
    explain_step(
        "OOK Amplitude Envelope Detection",
        "Computing the absolute magnitude of complex IQ samples to extract the amplitude envelope.",
        "y[n] = abs(x[n]) = sqrt( I[n]^2 + Q[n]^2 )"
    )
    envelope = np.abs(samples)
    
    # Smooth envelope slightly using a 5-point moving average to filter noise spikes
    smooth_window = 5
    envelope_smoothed = np.convolve(envelope, np.ones(smooth_window)/smooth_window, mode='same')
    
    # Compute threshold (midpoint of min and max)
    min_env = np.min(envelope_smoothed)
    max_env = np.max(envelope_smoothed)
    threshold = (min_env + max_env) / 2
    
    explain_step(
        "OOK Threshold Slicing",
        f"Determining bit boundaries using a slicing threshold of {threshold:.4f} (midway between Min: {min_env:.4f} and Max: {max_env:.4f}).",
        "Bit[n] = 1 if Envelope[n] > Threshold else 0"
    )
    
    sliced = (envelope_smoothed > threshold).astype(int)
    
    # Extract pulse durations / run-length encoding
    explain_step(
        "Run-Length Encoding (RLE) / Pulse Width Detection",
        "Grouping consecutive active (1) and inactive (0) samples to measure pulse durations.",
        "RLE: Count consecutive identical sample values"
    )
    
    diffs = np.diff(sliced)
    transitions = np.where(diffs != 0)[0] + 1
    # Split into runs
    if len(transitions) > 0:
        runs = np.split(sliced, transitions)
        run_lengths = [len(run) for run in runs]
        run_values = [run[0] for run in runs]
    else:
        run_lengths = [len(sliced)]
        run_values = [sliced[0]]
        
    # Render Diagnostics Plot (Envelope & Slicing)
    if HAS_MATPLOTLIB:
        fig, ax = plt.subplots(figsize=(10, 4))
        t_ms = (np.arange(len(envelope_smoothed)) / sample_rate) * 1000.0
        
        # Plot up to first 20k samples to show clear pulse shape
        plot_limit = min(20000, len(envelope_smoothed))
        ax.plot(t_ms[:plot_limit], envelope[:plot_limit], color='tab:blue', alpha=0.4, label='Raw Envelope')
        ax.plot(t_ms[:plot_limit], envelope_smoothed[:plot_limit], color='tab:blue', linewidth=1.5, label='Smoothed Envelope')
        ax.axhline(threshold, color='tab:red', linestyle='--', label=f'Threshold ({threshold:.2f})')
        
        # Draw binary sliced pulse train overlay at 80% height of max_env
        ax.plot(t_ms[:plot_limit], sliced[:plot_limit] * (max_env * 0.8), color='tab:green', linewidth=1.5, label='Sliced Digital Pulse')
        
        ax.set_title("OOK/ASK Amplitude Envelope & Sliced Pulse Train")
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Amplitude")
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"🎨 Saved DSP diagnostic OOK plot to: {plot_path}")
        
    return sliced, run_lengths, run_values



def process_psk(samples, sample_rate, symbol_rate, psk_order, plot_path, verbose=False):
    sps = sample_rate / symbol_rate
    sps_int = int(np.round(sps))
    
    if sps_int < 2:
        print(f"Error: Sample rate {sample_rate/1e6:.2f} MHz is too low for symbol rate {symbol_rate/1e3:.2f} kHz.", file=sys.stderr)
        sys.exit(1)
        
    explain_step(
        "Symbol Clock Recovery (Energy Maximization)",
        f"Scanning {sps_int} phase offsets to maximize the instantaneous energy of the complex envelope.",
        "Energy[offset] = Mean( abs(x[offset :: sps])^2 )"
    )
    
    energies = []
    offsets = list(range(sps_int))
    for offset in offsets:
        decim = samples[offset::sps_int]
        energies.append(np.mean(np.abs(decim)**2))
        
    best_offset = np.argmax(energies)
    sampled = samples[best_offset::sps_int]
    
    explain_step(
        "Carrier Phase Recovery (Decision-Directed Costas Loop)",
        f"Tracking phase rotation over time to lock the {psk_order}-PSK constellation axes.",
        "Phase_error = angle(symbol^M) / M, Phase -= alpha * Phase_error"
    )
    
    alpha = 0.05
    recovered = np.zeros_like(sampled)
    phase_track = np.zeros(len(sampled))
    current_phase = 0.0
    
    for i in range(len(sampled)):
        sym = sampled[i] * np.exp(-1j * current_phase)
        recovered[i] = sym
        
        # Error metric using M-th power
        # Educational Note: By raising the complex symbol to the M-th power (where M is the PSK order),
        # we mathematically multiply the phase by M. Because the ideal PSK phases are spaced by 2*pi/M,
        # multiplying by M collapses all ideal constellation points to the positive real axis (angle = 0).
        # Therefore, any non-zero angle after this M-th power operation is our exact phase error!
        err = np.angle(sym ** psk_order) / psk_order
        
        # Apply the error to our running phase estimate using our loop bandwidth (alpha)
        current_phase += alpha * err
        phase_track[i] = current_phase
        
    explain_step(
        "Symbol Slicing (Phase Demapping)",
        f"Mapping the rotated phase angle to one of {psk_order} ideal symbols.",
        "Symbol = floor( (angle(x) + pi/M) / (2*pi/M) ) % M"
    )
    
    # Demap the continuous phase angles back to discrete symbols
    angles = np.angle(recovered)
    
    # Educational Note: We rotate the grid by half a symbol segment (pi / M) so that 
    # the symbol decision boundaries align neatly on the axes, allowing us to just use floor().
    rotated_angles = (angles - (np.pi / psk_order)) % (2 * np.pi)
    symbols = np.floor(rotated_angles / (2 * np.pi / psk_order)).astype(int)
    
    if HAS_MATPLOTLIB:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        ax1.scatter(recovered.real, recovered.imag, color='tab:blue', alpha=0.3, s=10)
        ax1.axhline(0, color='gray', linestyle='--', alpha=0.5)
        ax1.axvline(0, color='gray', linestyle='--', alpha=0.5)
        ax1.set_title(f"{psk_order}-PSK Constellation")
        ax1.set_xlabel("In-Phase (I)")
        ax1.set_ylabel("Quadrature (Q)")
        ax1.set_aspect('equal', 'box')
        
        ax2.plot(phase_track, color='tab:purple')
        ax2.set_title("Costas Loop Phase Error Track")
        ax2.set_xlabel("Symbol Index")
        ax2.set_ylabel("Phase Offset (Radians)")
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"🎨 Saved DSP diagnostic PSK constellation plot to: {plot_path}")
        
    return symbols

def process_qam(samples, sample_rate, symbol_rate, qam_order, plot_path, verbose=False):
    sps = sample_rate / symbol_rate
    sps_int = int(np.round(sps))
    
    if sps_int < 2:
        print(f"Error: Sample rate {sample_rate/1e6:.2f} MHz is too low for symbol rate {symbol_rate/1e3:.2f} kHz.", file=sys.stderr)
        sys.exit(1)
        
    explain_step(
        "Symbol Clock Recovery (Energy Maximization)",
        "Finding optimal sample phase.",
        "Energy[offset] = Mean( abs(x[offset :: sps])^2 )"
    )
    
    energies = []
    for offset in range(sps_int):
        energies.append(np.mean(np.abs(samples[offset::sps_int])**2))
    best_offset = np.argmax(energies)
    sampled = samples[best_offset::sps_int]
    
    explain_step(
        "Automatic Gain Control (AGC)",
        "Normalizing the amplitude of the signal so the outermost points align with the QAM grid.",
        "y[n] = x[n] / RMS(x)"
    )
    
    rms = np.sqrt(np.mean(np.abs(sampled)**2))
    sampled_agc = sampled / rms
    
    explain_step(
        "Carrier Phase Recovery (4th Power Loop)",
        "Tracking phase rotation to keep the QAM grid perfectly vertical/horizontal.",
        "Phase_error = angle(symbol^4) / 4"
    )
    
    alpha = 0.05
    recovered = np.zeros_like(sampled_agc)
    current_phase = 0.0
    
    for i in range(len(sampled_agc)):
        sym = sampled_agc[i] * np.exp(-1j * current_phase)
        recovered[i] = sym
        # QAM 4th power error: This is a simplified decision-directed error metric.
        # Educational Note: Unlike PSK, raising QAM to the 4th power doesn't perfectly collapse all
        # points to the real axis because inner points have different angle offsets than corners.
        # However, for a simple lock, the corner points dominate the 4th power average, 
        # effectively forcing the grid to align horizontally and vertically.
        err = np.angle(sym ** 4) / 4
        
        # Apply the error to rotate our grid tracker
        current_phase += alpha * err
        
    explain_step(
        "Symbol Slicing (Grid Demapping)",
        f"Mapping each point to the nearest of the {qam_order} ideal grid coordinates.",
        "Min Euclidean Distance"
    )
    
    if HAS_MATPLOTLIB:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.scatter(recovered.real, recovered.imag, color='tab:green', alpha=0.3, s=10)
        ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
        ax.set_title(f"{qam_order}-QAM Constellation")
        ax.set_xlabel("In-Phase (I)")
        ax.set_ylabel("Quadrature (Q)")
        ax.set_aspect('equal', 'box')
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"🎨 Saved DSP diagnostic QAM constellation plot to: {plot_path}")
        
    return recovered

def process_analog_video(samples, sample_rate, line_samples, num_lines):
    """
    Blindly rasterizes an FM-demodulated analog video baseband signal into a 2D image.
    
    Educational Note:
    Analog video (like PAL/NTSC or FPV drone video) encodes brightness (luma) as 
    frequency deviation. By FM demodulating the signal and chopping it into rows of 
    exact time lengths, the image naturally reconstructs itself as a 2D array!
    """
    # 1. Demodulate FM envelope
    demod = demodulate_fm(samples, sample_rate)
    
    explain_step(
        "Raster Frame Reconstruction",
        f"Segmenting the continuous frequency amplitude into rows of length {line_samples} samples, for {num_lines} lines.",
        "Frame[line, pixel] = Demod[line * line_samples + pixel]"
    )
    
    # Simple line-by-line rasterization (PAL defaults to 64 µs per line)
    frame = []
    for i in range(num_lines):
        start = i * line_samples
        end = start + line_samples
        if end > len(demod):
            break
        row = demod[start:end]
        # Normalize row to 8-bit gray [0, 255]
        row_min = np.min(row)
        row_max = np.max(row)
        row_norm = ((row - row_min) / (row_max - row_min + 1e-12)) * 255
        frame.append(row_norm.astype(np.uint8))
        
    return np.array(frame)

def main():
    args = parse_args()
    
    # 1. Load IQ data
    samples = load_iq(args.file, args.format)
    
    # 2. Correct frequency offset if requested
    samples_shifted = apply_frequency_shift(samples, args.rate, args.offset_hz)
    
    # 3. Demodulate based on mode
    if args.mode == "fsk":
        bits, sliced_wave = process_fsk(samples_shifted, args.rate, args.symbol_rate, args.plot_path, args.verbose)
        
        # Display bits
        print(f"\n📊 Demodulation Completed (FSK Mode)")
        print(f"   Recovered Bits Count: {len(bits)}")
        print(f"   First 128 Bits:")
        bit_str = "".join(map(str, bits[:128]))
        print(f"     [ {bit_str} ]")
        
        # Print Hex & ASCII representation of first 128 bytes
        print(f"   First 128 Bytes (Hex & ASCII Dump):")
        for row_start in range(0, min(1024, len(bits)), 128):
            row_bits = bits[row_start:row_start+128]
            byte_vals = []
            ascii_chars = []
            for i in range(0, len(row_bits), 8):
                chunk = row_bits[i:i+8]
                if len(chunk) == 8:
                    val = int("".join(map(str, chunk)), 2)
                    byte_vals.append(f"{val:02X}")
                    ascii_chars.append(chr(val) if 32 <= val <= 126 else ".")
            if byte_vals:
                hex_part = " ".join(byte_vals)
                ascii_part = "".join(ascii_chars)
                print(f"     {hex_part:<47}  |  {ascii_part}")
        
        
        # Write bits to file if --output-bits was specified
        if args.output_bits:
            with open(args.output_bits, 'w') as bf:
                bit_string = ''.join(map(str, bits))
                for i in range(0, len(bit_string), 128):
                    bf.write(bit_string[i:i+128] + '\n')
            print(f"   💾 Recovered bits saved to: {args.output_bits}")
            
    elif args.mode == "fm_audio":
        audio = process_fm_audio(samples_shifted, args.rate, args.audio_rate)
        
        # Export to wav file
        import scipy.io.wavfile as wav
        output_wav = "demodulated_audio.wav"
        audio_int16 = (audio * 32767).astype(np.int16)
        wav.write(output_wav, int(args.audio_rate), audio_int16)
        
        print(f"\n📊 Demodulation Completed (FM Audio Mode)")
        print(f"   Audio duration: {len(audio)/args.audio_rate:.2f} seconds.")
        print(f"   WAV file saved to: {output_wav}")
        
    elif args.mode == "am_audio":
        audio = process_am_audio(samples_shifted, args.rate, args.audio_rate)
        
        # Export to wav file
        import scipy.io.wavfile as wav
        output_wav = "demodulated_audio.wav"
        audio_int16 = (audio * 32767).astype(np.int16)
        wav.write(output_wav, int(args.audio_rate), audio_int16)
        
        print(f"\n📊 Demodulation Completed (AM Audio Mode)")
        print(f"   Audio duration: {len(audio)/args.audio_rate:.2f} seconds.")
        print(f"   WAV file saved to: {output_wav}")
        
    elif args.mode == "ook":
        sliced, run_lengths, run_values = process_ook(samples_shifted, args.rate, args.plot_path, args.verbose)
        
        print(f"\n📊 Demodulation Completed (OOK/ASK Mode)")
        print(f"   Total Sliced Samples: {len(sliced)}")
        print(f"   Detected {len(run_lengths)} state transitions.")
        print(f"   First 30 Pulse Durations (Runs in samples & ms):")
        
        sample_period_ms = 1000.0 / args.rate
        for idx, (length, val) in enumerate(zip(run_lengths[:30], run_values[:30])):
            duration_ms = length * sample_period_ms
            state_str = "HIGH (ON)" if val == 1 else "LOW (OFF)"
            print(f"     Run {idx+1:02d}: {state_str:<9} | Length: {length:6d} samples ({duration_ms:.3f} ms)")


        
    elif args.mode == "psk":
        symbols = process_psk(samples_shifted, args.rate, args.symbol_rate, args.psk_order, args.plot_path, args.verbose)
        
        print(f"\n📊 Demodulation Completed (PSK Mode)")
        print(f"   Recovered Symbols Count: {len(symbols)}")
        print(f"   First 128 Symbols:")
        sym_str = "".join(map(str, symbols[:128]))
        print(f"     [ {sym_str} ]")
        
    elif args.mode == "qam":
        symbols = process_qam(samples_shifted, args.rate, args.symbol_rate, args.qam_order, args.plot_path, args.verbose)
        
        print(f"\n📊 Demodulation Completed (QAM Mode)")
        print(f"   Recovered Symbols Count: {len(symbols)}")
        print(f"   (See constellation plot for grid alignment)")

    elif args.mode == "analog_video":
        frame_img = process_analog_video(samples_shifted, args.rate, args.line_samples, args.video_lines)
        
        if len(frame_img) > 0:
            try:
                import cv2
            except ImportError:
                print("Error: OpenCV (cv2) is required for analog_video mode but is not installed.", file=sys.stderr)
                print("Install it with: pip install opencv-python", file=sys.stderr)
                sys.exit(1)
            output_png = "reconstructed_frame.png"
            cv2.imwrite(output_png, frame_img)
            print(f"\n📊 Demodulation Completed (Analog Video Mode)")
            print(f"   Reconstructed frame dimensions: {frame_img.shape[1]}x{frame_img.shape[0]} (Gray)")
            print(f"   Frame saved to: {output_png}")
        else:
            print("Error: Could not reconstruct any video lines from baseband samples.", file=sys.stderr)

if __name__ == "__main__":
    main()
