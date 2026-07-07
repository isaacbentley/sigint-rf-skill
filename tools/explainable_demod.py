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

def apply_premium_dark_theme():
    if not HAS_MATPLOTLIB:
        return
    plt.style.use('dark_background')
    plt.rcParams.update({
        'figure.facecolor': '#0B0F19',
        'axes.facecolor': '#161B26',
        'axes.edgecolor': '#2A3142',
        'grid.color': '#2A3142',
        'grid.linestyle': ':',
        'grid.alpha': 0.6,
        'text.color': '#E2E8F0',
        'axes.labelcolor': '#94A3B8',
        'xtick.color': '#94A3B8',
        'ytick.color': '#94A3B8',
        'font.family': 'sans-serif',
        'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica', 'sans-serif']
    })

def parse_args():
    parser = argparse.ArgumentParser(
        description="Explainable & Human-in-the-Loop RF Signal Demodulator"
    )
    parser.add_argument("--file", "-f", required=True, help="Path to IQ sample file")
    parser.add_argument("--rate", "-r", type=float, default=15.36e6, help="Sample rate in Hz")
    parser.add_argument("--freq", "-c", type=float, default=None, help="Assigned center frequency in Hz")
    parser.add_argument("--format", choices=["cf32_le", "ci16_le", "cu8", "ci8"], default=None, help="IQ format: cf32_le, ci16_le, cu8 (RTL-SDR uint8), ci8 (HackRF int8). Autodetected / from SigMF metadata if omitted.")
    parser.add_argument("--duration", type=float, default=0.0, help="Seconds of data to read (0 = use --max-samples)")
    parser.add_argument("--max-samples", type=int, default=20_000_000, help="Max complex samples to read when --duration is 0 (bounds RAM on large captures)")
    parser.add_argument("--mode", choices=["fsk", "ook", "fm_audio", "am_audio", "analog_video", "psk", "qam", "lora", "ofdm", "sc-fdma", "analog_fm", "analog_am"], required=True, help="Demodulation mode")
    
    # Signal tuning & decoding parameters
    parser.add_argument("--symbol-rate", type=float, help="Expected symbol rate (Baud). Required for FSK, PSK, QAM")
    parser.add_argument("--offset-hz", type=float, default=0.0, help="Manual frequency offset to correct (Hz)")
    parser.add_argument("--channel-bw", type=float, help="Bandwidth of the channel to isolate (Hz). Eliminates adjacent signals.")
    parser.add_argument("--audio-rate", type=float, default=48000.0, help="Target FM audio sample rate")
    parser.add_argument("--line-samples", type=int, default=None, help="PAL/NTSC video samples per line (auto-measured if omitted)")
    parser.add_argument("--video-lines", type=int, default=None, help="Video active line count (auto-derived from detected standard if omitted)")
    parser.add_argument("--psk-order", type=int, default=4, help="Order of PSK (2=BPSK, 4=QPSK, 8=8PSK)")
    parser.add_argument("--qam-order", type=int, default=16, help="Order of QAM (16, 64, 256)")
    
    # LoRa & OFDM parameters
    parser.add_argument("--lora-bw", type=float, default=125e3, help="LoRa bandwidth (Hz)")
    parser.add_argument("--lora-sf", type=int, default=7, help="LoRa Spreading Factor (SF)")
    parser.add_argument("--ofdm-profile", choices=["custom", "wifi", "lte", "ocusync", "atsc", "dvb"], default="custom", help="Auto-configure OFDM parameters for common protocols")
    parser.add_argument("--ofdm-fft", type=int, default=64, help="OFDM FFT size / Subcarriers (used if profile is custom)")
    parser.add_argument("--ofdm-cp", type=int, default=16, help="OFDM Cyclic Prefix length (used if profile is custom)")
    parser.add_argument("--sc-fdma-alloc", type=int, default=144, help="SC-FDMA Active Subcarrier Allocation Size (Number of contiguous subcarriers allocated to user)")
    
    # Visualization
    parser.add_argument("--plot-path", default="demod_diagnostics.png", help="Path to save intermediate DSP diagnostics plot")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed DSP steps and logic")
    parser.add_argument("--output-bits", default=None, help="Path to write recovered FSK bits as a text file (one char per bit, newline every 128 bits)")
    parser.add_argument("--json-output", default=None, help="Path to write a JSON file with mode-specific analysis (e.g. analog_video standard + audio subcarrier)")
    
    return parser.parse_args(normalize_numeric_argv())

def explain_step(title, description, math_formula=None):
    print(f"\n💡 [DSP STEP] {title}")
    print(f"   Description: {description}")
    if math_formula:
        print(f"   Formula:     {math_formula}")
    print("-" * 60)

def load_sigmf_metadata(meta_path):
    with open(meta_path, "r") as f:
        meta = json.load(f)

    # Try to find core properties
    global_meta = meta.get("global", {})
    datatype = global_meta.get("core:datatype", "cf32_le")
    sample_rate = global_meta.get("core:sample_rate", None)

    captures = meta.get("captures", [])
    frequency = None
    if captures:
        frequency = captures[0].get("core:frequency", None)

    return datatype, sample_rate, frequency


def resolve_paths_and_metadata(args):
    filepath = args.file
    filename, ext = os.path.splitext(filepath)

    datatype = args.format
    sample_rate = args.rate
    frequency = args.freq
    data_path = filepath

    # Check if we were passed a .sigmf-meta or if one exists alongside a raw file
    if ext == ".sigmf-meta":
        datatype_meta, rate_meta, freq_meta = load_sigmf_metadata(filepath)
        if not datatype:
            datatype = datatype_meta
        if rate_meta is not None:
            sample_rate = rate_meta
        if freq_meta is not None:
            frequency = freq_meta
        # Find data file
        for suffix in [".sigmf-data", ".data", ".bin", ".cf32", ".raw", ".iq"]:
            test_path = filename + suffix
            if os.path.exists(test_path):
                data_path = test_path
                break
    elif ext == ".sigmf-data" or os.path.exists(filename + ".sigmf-meta"):
        meta_path = filename + ".sigmf-meta"
        if os.path.exists(meta_path):
            datatype_meta, rate_meta, freq_meta = load_sigmf_metadata(meta_path)
            if not datatype:
                datatype = datatype_meta
            if rate_meta is not None:
                sample_rate = rate_meta
            if freq_meta is not None:
                frequency = freq_meta

    # Fallback auto-detection by extension
    if not datatype:
        if ext in [".cf32", ".data"] or "cf32" in filepath:
            datatype = "cf32_le"
        else:
            datatype = "ci16_le"  # Default fallback safe for SDR captures

    return data_path, datatype, sample_rate, frequency


def read_iq_samples(file_path, datatype, max_samples):
    if not os.path.exists(file_path):
        print(f"Error: Data file not found at {file_path}", file=sys.stderr)
        sys.exit(1)

    # SigMF and the SDR toolchain spell the same format several ways; fold the
    # common aliases (and the raw uint8/int8 that rtl_sdr / hackrf_transfer emit)
    # onto the four datatypes we actually decode below.
    dt = (datatype or "").strip().lower()
    dt = {
        "fc32": "cf32_le", "cf32": "cf32_le",
        "cs16_le": "ci16_le", "ci16": "ci16_le", "sc16": "ci16_le",
        "uint8": "cu8", "u8": "cu8", "cu8_le": "cu8", "rtl": "cu8",
        "int8": "ci8", "i8": "ci8", "ci8_le": "ci8", "sc8": "ci8", "hackrf": "ci8",
    }.get(dt, dt)

    if dt == "cf32_le":
        count = max_samples * 2
        raw = np.fromfile(file_path, dtype=np.float32, count=count)
        if len(raw) % 2 != 0:
            raw = raw[:-1]
        samples = raw[0::2] + 1j * raw[1::2]
    elif dt == "ci16_le":
        count = max_samples * 2
        raw = np.fromfile(file_path, dtype=np.int16, count=count)
        if len(raw) % 2 != 0:
            raw = raw[:-1]
        samples = (raw[0::2] + 1j * raw[1::2]) / 32768.0
    elif dt == "cu8":
        # RTL-SDR native: unsigned 8-bit IQ with a DC bias at 127.5
        count = max_samples * 2
        raw = np.fromfile(file_path, dtype=np.uint8, count=count).astype(np.float32)
        if len(raw) % 2 != 0:
            raw = raw[:-1]
        raw -= 127.5          # in place: a full wideband read is big, avoid copies
        raw /= 127.5
        samples = raw[0::2] + 1j * raw[1::2]
    elif dt == "ci8":
        # HackRF native: signed 8-bit IQ; normalize to [-1.0, 1.0]
        count = max_samples * 2
        raw = np.fromfile(file_path, dtype=np.int8, count=count).astype(np.float32)
        if len(raw) % 2 != 0:
            raw = raw[:-1]
        raw /= 127.5          # in place
        samples = raw[0::2] + 1j * raw[1::2]
    else:
        print(f"Error: Unsupported datatype {datatype}", file=sys.stderr)
        sys.exit(1)

    # Guard against corrupt captures: scrub non-finite samples and clamp absurd
    # magnitudes so a bad file degrades gracefully instead of poisoning the DSP.
    invalid_mask = ~np.isfinite(samples)
    if np.any(invalid_mask):
        print(f"Warning: Replaced {np.sum(invalid_mask)} NaN/Inf samples with 0+0j.", file=sys.stderr)
        samples[invalid_mask] = 0.0 + 0.0j
    # Clamp in place (bool compares + out=) to avoid a second big transient copy.
    max_val = 1000.0
    if (np.any(samples.real > max_val) or np.any(samples.real < -max_val)
            or np.any(samples.imag > max_val) or np.any(samples.imag < -max_val)):
        print("Warning: Clamping extremely large values to prevent overflow. Data may be corrupted.", file=sys.stderr)
        np.clip(samples.real, -max_val, max_val, out=samples.real)
        np.clip(samples.imag, -max_val, max_val, out=samples.imag)

    return samples


# Options that take a (possibly negative) numeric value. argparse's built-in
# negative-number detector rejects scientific notation (e.g. -25e6) and treats it
# as an unknown option, so we merge "--flag -25e6" -> "--flag=-25e6".
_NUMERIC_FLAGS = {
    "--offset-hz", "--channel-bw", "--freq", "-c", "--rate", "-r",
    "--symbol-rate", "--audio-rate", "--lora-bw", "--duration", "--max-samples",
    "--start", "--stop",
}


def _looks_like_negative_number(s):
    if not s.startswith("-"):
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def normalize_numeric_argv(argv=None):
    """Rewrite "--flag -25e6" to "--flag=-25e6" for known numeric options so a
    negative scientific-notation value is not misparsed by argparse as a flag."""
    src = list(sys.argv[1:] if argv is None else argv)
    out = []
    i = 0
    while i < len(src):
        tok = src[i]
        if tok in _NUMERIC_FLAGS and i + 1 < len(src) and _looks_like_negative_number(src[i + 1]):
            out.append(f"{tok}={src[i + 1]}")
            i += 2
        else:
            out.append(tok)
            i += 1
    return out


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

def apply_channel_filter(samples, sample_rate, channel_bw):
    """
    Applies a digital low-pass filter to isolate the channel of interest.
    Since the target signal has already been shifted to DC (0 Hz), a low-pass 
    filter acts as a band-pass filter around the original center frequency.
    """
    explain_step(
        "Channel Isolation Filter",
        f"Applying a digital low-pass filter with a cutoff of {channel_bw/2 / 1e3:.1f} kHz to isolate the target channel and reject adjacent signals.",
        "x_filt[n] = LPF(x[n])"
    )
    from scipy.signal import butter, lfilter
    nyq = 0.5 * sample_rate
    cutoff = min(channel_bw / 2.0, nyq - 1000)
    b, a = butter(4, cutoff / nyq, btype='low')
    return lfilter(b, a, samples)


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
    
    # Render Diagnostics Plot (Eye Diagram, Variance, and Hybrid Protocol Decode)
    if HAS_MATPLOTLIB:
        apply_premium_dark_theme()
        fig = plt.figure(figsize=(14, 8))
        gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.2])
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, :])
        
        # 1. Plot Clock Recovery Variance curve
        ax1.plot(offsets, variances, marker='o', color='#BF5AF2')
        ax1.axvline(best_offset, color='#FF007F', linestyle='--', label=f'Best Offset ({best_offset})')
        ax1.set_title("Clock Recovery Phase Sweep", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax1.set_xlabel("Sample Phase Offset", fontsize=9)
        ax1.set_ylabel("Variance", fontsize=9)
        ax1.grid(True)
        ax1.legend(facecolor='#161B26', edgecolor='#2A3142', labelcolor='#E2E8F0')
        
        # 2. Plot Eye Diagram (overlaying 100 symbol segments)
        ax2.set_title("FSK Eye Diagram (Demodulated Frequency)", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax2.set_xlabel("Sample Offset in Symbol Period", fontsize=9)
        ax2.set_ylabel("Frequency Deviation (Hz)", fontsize=9)
        ax2.grid(True)
        
        num_eyes = min(100, len(demod) // (sps_int * 2))
        eye_len = sps_int * 2
        for i in range(num_eyes):
            start = i * sps_int
            end = start + eye_len
            if end < len(demod):
                # Phosphor persistence effect using very low alpha
                ax2.plot(demod[start:end], color='#00E5FF', alpha=0.08, linewidth=0.6)
                
        # Draw slicing threshold and sample points
        ax2.axhline(0, color='#FF007F', linestyle=':', label='Slicing Threshold')
        ax2.axvline(best_offset, color='#00E676', linestyle='--', alpha=0.7, label='Sampling Points')
        ax2.axvline(best_offset + sps_int, color='#00E676', linestyle='--', alpha=0.7)
        ax2.legend(loc='lower right', facecolor='#161B26', edgecolor='#2A3142', labelcolor='#E2E8F0')
        
        # 3. Hybrid Oscilloscope Decode Mode (Bottom Timeline)
        num_symbols_plot = 128
        samples_plot = num_symbols_plot * sps_int
        t_plot = np.arange(min(samples_plot, len(demod)))
        
        # Plot the raw frequency demodulated signal
        ax3.plot(t_plot, demod[:len(t_plot)], color='#00E5FF', linewidth=1.5, label='Demodulated Freq')
        ax3.axhline(0, color='#2A3142', linestyle=':', alpha=0.7)
        
        # Draw sampling ticks and bit labels
        y_min = np.min(demod[:len(t_plot)])
        y_max = np.max(demod[:len(t_plot)])
        y_range = y_max - y_min if (y_max - y_min) > 0 else 1.0
        
        for k in range(num_symbols_plot):
            sample_idx = best_offset + k * sps_int
            if sample_idx >= len(t_plot):
                break
            bit_val = bits[k]
            color = '#00E676' if bit_val == 1 else '#FF3D00'
            ax3.scatter(sample_idx, demod[sample_idx], color=color, s=25, zorder=5)
            # Show bit values above the sampling point
            ax3.text(sample_idx, demod[sample_idx] + (y_range * 0.08), str(bit_val), 
                     color=color, fontsize=8, ha='center', fontweight='bold')
            # Draw vertical dashed line for symbol boundaries
            ax3.axvline(sample_idx, color='#2A3142', linestyle='--', alpha=0.25)
            # Draw byte boundaries (solid vertical lines)
            if k % 8 == 0:
                ax3.axvline(sample_idx - sps_int/2, color='#475569', linestyle='-', linewidth=1.2, alpha=0.8)
            
        # Draw byte boundaries and ASCII/Hex labels
        num_bytes_plot = num_symbols_plot // 8
        for b_idx in range(num_bytes_plot):
            byte_start_sample = best_offset + b_idx * 8 * sps_int
            byte_end_sample = best_offset + (b_idx + 1) * 8 * sps_int
            if byte_end_sample >= len(t_plot):
                break
                
            # Extract byte value
            byte_bits = bits[b_idx*8 : (b_idx+1)*8]
            byte_val = int("".join(map(str, byte_bits)), 2)
            hex_str = f"0x{byte_val:02X}"
            ascii_char = chr(byte_val) if 32 <= byte_val <= 126 else "."
            
            # Bounding box coordinates
            box_y_bottom = y_min - 0.38 * y_range
            box_y_top = y_min - 0.08 * y_range
            
            # Fill the box with glassmorphic colors
            if ascii_char != '.':
                facecolor = '#00E5FF'
                edgecolor = '#00E5FF'
                alpha = 0.15
                border_alpha = 0.5
            else:
                facecolor = '#64748B'
                edgecolor = '#64748B'
                alpha = 0.08
                border_alpha = 0.3
                
            ax3.fill_between([byte_start_sample + 1, byte_end_sample - 1], box_y_bottom, box_y_top, 
                             facecolor=facecolor, edgecolor=edgecolor, alpha=alpha, linewidth=1, zorder=4)
            
            # Add thin outline manually to have clean alpha control
            rect = plt.Rectangle((byte_start_sample + 1, box_y_bottom), (byte_end_sample - byte_start_sample - 2), 
                                 (box_y_top - box_y_bottom), fill=False, edgecolor=edgecolor, alpha=border_alpha, linewidth=1, zorder=4)
            ax3.add_patch(rect)
            
            # Center the ASCII character
            center_x = (byte_start_sample + byte_end_sample) / 2
            ax3.text(center_x, (box_y_bottom + box_y_top)/2 + 0.03*y_range, ascii_char, 
                     color='#FFFFFF', fontsize=12, fontweight='bold', ha='center', va='center', zorder=5)
            # Center the hex value below it
            ax3.text(center_x, (box_y_bottom + box_y_top)/2 - 0.08*y_range, hex_str, 
                     color='#FFEA00', fontsize=8, ha='center', va='center', zorder=5)
            
        ax3.set_title("Hybrid Protocol Decode (Time-Domain Waveform aligned to ASCII / Hex)", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax3.set_xlabel("Sample Index", fontsize=9)
        ax3.set_ylabel("Freq Deviation (Hz)", fontsize=9)
        ax3.grid(True)
        # Expand y limits to fit the boxes at the bottom
        ax3.set_ylim(y_min - 0.48 * y_range, y_max + 0.18 * y_range)
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"🎨 Saved DSP hybrid protocol decode diagnostics plot to: {plot_path}")
        
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
        apply_premium_dark_theme()
        fig, ax = plt.subplots(figsize=(10, 4))
        t_ms = (np.arange(len(envelope_smoothed)) / sample_rate) * 1000.0
        
        # Plot up to first 20k samples to show clear pulse shape
        plot_limit = min(20000, len(envelope_smoothed))
        ax.plot(t_ms[:plot_limit], envelope[:plot_limit], color='#00E5FF', alpha=0.15, label='Raw Envelope')
        ax.plot(t_ms[:plot_limit], envelope_smoothed[:plot_limit], color='#00E5FF', linewidth=1.5, label='Smoothed Envelope')
        ax.axhline(threshold, color='#FF007F', linestyle='--', label=f'Threshold ({threshold:.2f})')
        
        # Draw binary sliced pulse train overlay at 80% height of max_env
        ax.plot(t_ms[:plot_limit], sliced[:plot_limit] * (max_env * 0.8), color='#00E676', linewidth=1.5, label='Sliced Digital Pulse')
        
        ax.set_title("OOK/ASK Amplitude Envelope & Sliced Pulse Train", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax.set_xlabel("Time (ms)", fontsize=9)
        ax.set_ylabel("Amplitude", fontsize=9)
        ax.legend(loc='upper right', facecolor='#161B26', edgecolor='#2A3142', labelcolor='#E2E8F0')
        ax.grid(True)
        
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
        apply_premium_dark_theme()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        ax1.scatter(recovered.real, recovered.imag, color='#00E5FF', alpha=0.3, s=10)
        ax1.axhline(0, color='#2A3142', linestyle='--')
        ax1.axvline(0, color='#2A3142', linestyle='--')
        ax1.set_title(f"{psk_order}-PSK Constellation", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax1.set_xlabel("In-Phase (I)", fontsize=9)
        ax1.set_ylabel("Quadrature (Q)", fontsize=9)
        ax1.set_aspect('equal', 'box')
        ax1.grid(True)
        
        ax2.plot(phase_track, color='#BF5AF2')
        ax2.set_title("Costas Loop Phase Error Track", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax2.set_xlabel("Symbol Index", fontsize=9)
        ax2.set_ylabel("Phase Offset (Radians)", fontsize=9)
        ax2.grid(True)
        
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
        apply_premium_dark_theme()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.scatter(recovered.real, recovered.imag, color='#00E676', alpha=0.3, s=10)
        ax.axhline(0, color='#2A3142', linestyle='--')
        ax.axvline(0, color='#2A3142', linestyle='--')
        ax.set_title(f"{qam_order}-QAM Constellation", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax.set_xlabel("In-Phase (I)", fontsize=9)
        ax.set_ylabel("Quadrature (Q)", fontsize=9)
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"🎨 Saved DSP diagnostic QAM constellation plot to: {plot_path}")
        
    return recovered

def process_lora(samples, sample_rate, bw, sf, plot_path, verbose=False):
    """
    Demonstrates basic LoRa (Chirp Spread Spectrum) de-chirping for a single symbol.
    """
    explain_step(
        "LoRa Base Down-Chirp Generation",
        f"Generating an ideal down-chirp sweeping from +{bw/2/1e3} kHz to -{bw/2/1e3} kHz over the symbol duration.",
        "DownChirp(t) = exp(-j * 2*pi * (bw / (2*T)) * t^2)"
    )
    
    symbol_duration = (2 ** sf) / bw
    samples_per_symbol = int(sample_rate * symbol_duration)
    if samples_per_symbol > len(samples):
        print(f"Error: Not enough samples for a full LoRa symbol. Need {samples_per_symbol}, got {len(samples)}.", file=sys.stderr)
        sys.exit(1)
        
    t = np.arange(samples_per_symbol) / sample_rate
    
    # Generate ideal down-chirp
    # Freq sweeps from bw/2 to -bw/2. Phase is integral of freq.
    f0 = bw / 2
    f1 = -bw / 2
    chirp_rate = (f1 - f0) / symbol_duration
    phase = 2 * np.pi * (f0 * t + 0.5 * chirp_rate * t**2)
    down_chirp = np.exp(1j * phase)
    
    # Loop through available full symbols
    num_symbols = len(samples) // samples_per_symbol
    if num_symbols == 0:
        print(f"Error: Not enough samples for a full LoRa symbol. Need {samples_per_symbol}, got {len(samples)}.", file=sys.stderr)
        sys.exit(1)
        
    symbol_vals = []
    fft_mags = []
    
    explain_step(
        "De-chirping & FFT Peak Extraction (Multiple Symbols)",
        f"Multiplying IQ samples by the down-chirp symbol-by-symbol, then running an FFT to extract the symbol value (0 to {2**sf - 1}).",
        "Symbol = argmax( abs(FFT(Dechirped)) )"
    )
    
    for i in range(num_symbols):
        start = i * samples_per_symbol
        end = start + samples_per_symbol
        symbol_samples = samples[start:end]
        
        dechirped = symbol_samples * down_chirp
        
        decim_factor = int(sample_rate / bw)
        if decim_factor > 1:
            dechirped_decim = signal.decimate(dechirped, decim_factor)
        else:
            dechirped_decim = dechirped
            
        fft_size = 2 ** sf
        if len(dechirped_decim) < fft_size:
            dechirped_decim = np.pad(dechirped_decim, (0, fft_size - len(dechirped_decim)))
            
        fft_result = np.fft.fft(dechirped_decim[:fft_size])
        fft_mag = np.abs(fft_result)
        symbol_val = np.argmax(fft_mag)
        
        symbol_vals.append(symbol_val)
        fft_mags.append(fft_mag)
    
    if HAS_MATPLOTLIB:
        apply_premium_dark_theme()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot spectrogram of raw vs dechirped (First 5 symbols max)
        plot_samples = min(samples_per_symbol * 5, len(samples))
        f_s, t_s, Sxx = signal.spectrogram(samples[:plot_samples], fs=sample_rate, nperseg=256, noverlap=128)
        f_s = np.fft.fftshift(f_s)
        Sxx = np.fft.fftshift(Sxx, axes=0)
        ax1.pcolormesh(t_s*1000, f_s/1e3, 10*np.log10(Sxx+1e-12), shading='gouraud', cmap='turbo')
        ax1.set_title(f"Raw LoRa Up-Chirps (First {min(num_symbols, 5)} symbols)", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax1.set_xlabel("Time (ms)", fontsize=9)
        ax1.set_ylabel("Frequency (kHz)", fontsize=9)
        
        # Plot FFT result of the FIRST symbol
        bins = np.arange(fft_size)
        ax2.plot(bins, fft_mags[0], color='#00E5FF')
        ax2.axvline(symbol_vals[0], color='#00E676', linestyle='--', label=f'Peak Symbol 1: {symbol_vals[0]}')
        ax2.set_title("De-chirped FFT Output (Symbol 1)", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax2.set_xlabel("Symbol Bin", fontsize=9)
        ax2.set_ylabel("Magnitude", fontsize=9)
        ax2.legend(facecolor='#161B26', edgecolor='#2A3142', labelcolor='#E2E8F0')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"🎨 Saved DSP diagnostic LoRa de-chirping plot to: {plot_path}")
        
    return symbol_vals

def process_ofdm(samples, sample_rate, fft_size, cp_len, profile, plot_path, verbose=False):
    """
    Demonstrates basic OFDM subcarrier extraction.
    """
    sym_len = fft_size + cp_len
    
    explain_step(
        "Symbol Synchronization (CP Autocorrelation)",
        f"Searching for the Cyclic Prefix (CP) of length {cp_len} to find the exact start of the OFDM symbol.",
        "R[d] = sum( x[n+d] * conj(x[n+d+fft_size]) )"
    )
    
    # Schmidl-Cox / CP correlation approach over the first few symbols
    search_len = min(sym_len * 10, len(samples) - fft_size)
    corr = np.zeros(search_len)
    
    # We correlate a window of length cp_len with the signal delayed by fft_size
    # This creates a peak when the CP perfectly overlaps with the end of the symbol it was copied from.
    for i in range(search_len - cp_len):
        window = samples[i:i+cp_len]
        delayed = samples[i+fft_size : i+fft_size+cp_len]
        corr[i] = np.abs(np.vdot(window, delayed))
        
    symbol_start = np.argmax(corr[:sym_len*3]) # Look in first few symbols
    
    explain_step(
        "Cyclic Prefix Removal & FFT",
        f"Removing {cp_len} CP samples and taking the FFT of the next {fft_size} samples to separate the orthogonal subcarriers.",
        "Subcarriers = FFT( x[start + cp_len : start + cp_len + fft_size] )"
    )
    
    data_start = symbol_start + cp_len
    data_end = data_start + fft_size
    if data_end > len(samples):
        print("Error: Not enough samples for a full OFDM symbol.", file=sys.stderr)
        sys.exit(1)
        
    symbol_data = samples[data_start:data_end]
    subcarriers = np.fft.fft(symbol_data)
    subcarriers = np.fft.fftshift(subcarriers) # Center DC
    
    # Identify pilot tones based on profile
    pilots = []
    pilot_indices = []
    if profile == "wifi":
        # WiFi 802.11a uses subcarriers -21, -7, 7, 21 (relative to center DC)
        center = fft_size // 2
        pilot_indices = [center - 21, center - 7, center + 7, center + 21]
    elif profile == "lte":
        # LTE uses scattered pilots, pick a few for educational illustration
        center = fft_size // 2
        spacing = fft_size // 6
        pilot_indices = [center - spacing*2, center - spacing, center + spacing, center + spacing*2]
    elif profile in ["ocusync", "atsc", "dvb"]:
        # Generalized scattered pilots for these formats
        center = fft_size // 2
        spacing = fft_size // (12 if profile in ["atsc", "dvb"] else 8)
        pilot_indices = [center - spacing*3, center - spacing, center + spacing, center + spacing*3]
        
    if pilot_indices:
        # Ensure indices are within bounds
        pilot_indices = [idx for idx in pilot_indices if 0 <= idx < fft_size]
        explain_step(
            "Pilot Tone Extraction & Channel Estimation",
            f"Extracting known pilot subcarriers for phase/amplitude tracking. Profile '{profile}' defines pilots at indices: {[idx - (fft_size//2) for idx in pilot_indices]} (relative to DC).",
            "H_est = Received_Pilot / Known_Pilot"
        )
        for idx in pilot_indices:
            pilots.append(subcarriers[idx])
    
    if HAS_MATPLOTLIB:
        apply_premium_dark_theme()
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot Correlation
        ax1.plot(corr, color='#00E5FF')
        ax1.axvline(symbol_start, color='#FF007F', linestyle='--', label=f'Symbol Start ({symbol_start})')
        ax1.set_title("Cyclic Prefix Correlation (Timing Sync)", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax1.set_xlabel("Sample Delay", fontsize=9)
        ax1.set_ylabel("Correlation Magnitude", fontsize=9)
        ax1.legend(facecolor='#161B26', edgecolor='#2A3142', labelcolor='#E2E8F0')
        ax1.grid(True)
        
        # Plot Constellation
        if pilot_indices:
            data_mask = np.ones(fft_size, dtype=bool)
            data_mask[pilot_indices] = False
            data_sc = subcarriers[data_mask]
            pilot_sc = subcarriers[pilot_indices]
            
            ax2.scatter(data_sc.real, data_sc.imag, color='#00E676', alpha=0.5, s=20, label='Data Subcarriers')
            ax2.scatter(pilot_sc.real, pilot_sc.imag, color='#FF007F', alpha=1.0, s=80, marker='*', label='Pilot Tones')
            ax2.legend(loc='upper right', facecolor='#161B26', edgecolor='#2A3142', labelcolor='#E2E8F0')
        else:
            ax2.scatter(subcarriers.real, subcarriers.imag, color='#00E676', alpha=0.5, s=20)
            
        ax2.axhline(0, color='#2A3142', linestyle='--')
        ax2.axvline(0, color='#2A3142', linestyle='--')
        ax2.set_title(f"OFDM Subcarriers ({fft_size} bins)", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax2.set_xlabel("In-Phase (I)", fontsize=9)
        ax2.set_ylabel("Quadrature (Q)", fontsize=9)
        ax2.set_aspect('equal', 'box')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"🎨 Saved DSP diagnostic OFDM plot to: {plot_path}")
        
    return subcarriers

def process_sc_fdma(samples, sample_rate, fft_size, cp_len, alloc_size, plot_path, verbose=False):
    """
    Demonstrates SC-FDMA (Single-Carrier FDMA) used in LTE Uplink.
    It performs the OFDM subcarrier extraction (FFT) and then an Inverse FFT (IFFT) 
    on the allocated block to recover the single-carrier time-domain symbols.
    """
    sym_len = fft_size + cp_len
    
    explain_step(
        "SC-FDMA Symbol Sync",
        f"Searching for the Cyclic Prefix (CP) of length {cp_len} to find the exact start of the SC-FDMA symbol.",
        "R[d] = sum( x[n+d] * conj(x[n+d+fft_size]) )"
    )
    
    search_len = min(sym_len * 10, len(samples) - fft_size)
    corr = np.zeros(search_len)
    for i in range(search_len - cp_len):
        window = samples[i:i+cp_len]
        delayed = samples[i+fft_size : i+fft_size+cp_len]
        corr[i] = np.abs(np.vdot(window, delayed))
        
    symbol_start = np.argmax(corr[:sym_len*3])
    
    explain_step(
        "SC-FDMA Precoding Reversal (FFT -> IFFT)",
        f"1. Remove CP and perform a {fft_size}-point FFT to extract orthogonal subcarriers.\n"
        f"2. Isolate a contiguous block of {alloc_size} subcarriers allocated to the user.\n"
        f"3. Perform an {alloc_size}-point Inverse FFT (IFFT) on the block to recover the single-carrier time-domain symbols.",
        "Subcarriers = FFT(x); Block = Subcarriers[start:start+N]; Symbols = IFFT(Block)"
    )
    
    data_start = symbol_start + cp_len
    data_end = data_start + fft_size
    if data_end > len(samples):
        print("Error: Not enough samples for a full SC-FDMA symbol.", file=sys.stderr)
        sys.exit(1)
        
    # Step 1: OFDM Demodulation (FFT)
    symbol_data = samples[data_start:data_end]
    subcarriers = np.fft.fft(symbol_data)
    subcarriers = np.fft.fftshift(subcarriers)
    
    # Step 2: Extract allocated block (Assuming block is placed just above DC for demonstration)
    center = fft_size // 2
    # Ensure allocation fits
    alloc_size = min(alloc_size, fft_size - 2)
    block_start = center + 1 # Skip DC
    block_end = block_start + alloc_size
    allocated_block = subcarriers[block_start:block_end]
    
    # Step 3: SC-FDMA IFFT to recover time-domain single-carrier symbols
    sc_symbols = np.fft.ifft(allocated_block)
    
    if HAS_MATPLOTLIB:
        apply_premium_dark_theme()
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))
        
        # Plot 1: Full Subcarriers
        freq_bins = np.arange(-center, center)
        ax1.plot(freq_bins, np.abs(subcarriers), color='#64748B', alpha=0.5, label='Other Subcarriers')
        ax1.plot(freq_bins[block_start:block_end], np.abs(allocated_block), color='#00E5FF', label=f'Allocated Block ({alloc_size})')
        ax1.set_title("SC-FDMA Subcarrier Allocation", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax1.set_xlabel("Subcarrier Offset", fontsize=9)
        ax1.set_ylabel("Magnitude", fontsize=9)
        ax1.legend(facecolor='#161B26', edgecolor='#2A3142', labelcolor='#E2E8F0')
        ax1.grid(True)
        
        # Plot 2: Frequency Domain Constellation (The "Block")
        ax2.scatter(allocated_block.real, allocated_block.imag, color='#FF9100', alpha=0.7, s=20)
        ax2.axhline(0, color='#2A3142', linestyle='--')
        ax2.axvline(0, color='#2A3142', linestyle='--')
        ax2.set_title("Frequency Domain (Precoded)", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax2.set_xlabel("In-Phase (I)", fontsize=9)
        ax2.set_ylabel("Quadrature (Q)", fontsize=9)
        ax2.set_aspect('equal', 'box')
        ax2.grid(True)
        
        # Plot 3: Time Domain Constellation (After IFFT)
        ax3.scatter(sc_symbols.real, sc_symbols.imag, color='#00E676', alpha=0.8, s=30)
        ax3.axhline(0, color='#2A3142', linestyle='--')
        ax3.axvline(0, color='#2A3142', linestyle='--')
        ax3.set_title("Recovered SC-FDMA Constellation", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax3.set_xlabel("In-Phase (I)", fontsize=9)
        ax3.set_ylabel("Quadrature (Q)", fontsize=9)
        ax3.set_aspect('equal', 'box')
        ax3.grid(True)
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"🎨 Saved DSP diagnostic SC-FDMA plot to: {plot_path}")
        
    return subcarriers, sc_symbols


def plot_baseband_dashboard(demod, sample_rate, plot_path, title, is_am=False):
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(title, fontsize=16)
    
    color = 'orange' if is_am else 'blue'
    y_label = 'Amplitude' if is_am else 'Instantaneous Freq (Hz)'
    t_short_len = 0.005 if is_am else 0.002
    t_long_len = 0.100 if is_am else 0.035
    
    # 1. Short Time Domain
    samples_short = int(sample_rate * t_short_len)
    segment_short = demod[:samples_short]
    t_short = np.arange(len(segment_short)) * 1000 / sample_rate
    axs[0, 0].plot(t_short, segment_short, color=color, alpha=0.8)
    axs[0, 0].set_title(f"Short Baseband Waveform ({int(t_short_len*1000)}ms)")
    axs[0, 0].set_xlabel("Time (ms)")
    axs[0, 0].set_ylabel(y_label)
    axs[0, 0].grid(True, alpha=0.3)
    
    # 2. Long Time Domain
    samples_long = int(sample_rate * t_long_len)
    segment_long = demod[:samples_long]
    t_long = np.arange(len(segment_long)) * 1000 / sample_rate
    axs[0, 1].plot(t_long, segment_long, color=color, alpha=0.8)
    axs[0, 1].set_title(f"Long Baseband Waveform ({int(t_long_len*1000)}ms)")
    axs[0, 1].set_xlabel("Time (ms)")
    axs[0, 1].set_ylabel(y_label)
    axs[0, 1].grid(True, alpha=0.3)
    
    # 3. Baseband Power Spectral Density (PSD)
    decimation_psd = 8 if is_am else 4
    axs[1, 0].psd(demod[::decimation_psd], NFFT=2048, Fs=sample_rate/decimation_psd, color='purple')
    axs[1, 0].set_title("Baseband Power Spectral Density")
    axs[1, 0].set_xlabel("Frequency (Hz)")
    
    # 4. Baseband Spectrogram (Waterfall)
    decimation_spec = 16 if is_am else 8
    axs[1, 1].specgram(demod[::decimation_spec], NFFT=256, Fs=sample_rate/decimation_spec, cmap='viridis')
    axs[1, 1].set_title("Baseband Spectrogram")
    axs[1, 1].set_xlabel("Time (s)")
    axs[1, 1].set_ylabel("Frequency (Hz)")
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(plot_path, dpi=150)
    plt.close()

def analyze_video_standard(demod, sample_rate):
    """Measure the horizontal line rate and lines-per-frame from FM-demodulated
    composite video and classify NTSC vs PAL. Label-independent. Returns a dict
    or None if no clear raster periodicity is present.

    Line rate is the primary discriminator (NTSC 15734 Hz vs PAL 15625 Hz);
    lines-per-frame corroborates (NTSC 525 vs PAL 625). The frame count is found
    by collapsing each line to its mean (which kills in-line picture content) so
    the residual periodicity is the vertical/frame structure."""
    v = np.asarray(demod, dtype=float)
    n = len(v)
    if n < int(0.02 * sample_rate):            # need a few tens of lines
        return None
    # Bound the analysis window to ~0.2 s (still spans many lines and several
    # frames) so we never FFT a multi-second capture.
    w = min(n, int(0.2 * sample_rate))
    v = v[:w] - v[:w].mean()
    n = w

    def _acf(x):
        m = len(x)
        f = np.fft.rfft(x, 2 * m)
        a = np.fft.irfft(f * np.conj(f))[:m]
        return a / (a[0] + 1e-12)

    a = _acf(v)
    lo, hi = int(60e-6 * sample_rate), int(67e-6 * sample_rate)
    if hi >= len(a) or hi <= lo:
        return None
    line_len = lo + int(np.argmax(a[lo:hi]))   # samples per horizontal line
    if line_len <= 0:
        return None
    line_hz = sample_rate / line_len

    frame_lines_meas = None
    m = n // line_len
    if m >= 700:                               # need >1 full frame for a valid [400,700] search
        rows = v[:m * line_len].reshape(m, line_len).mean(axis=1)
        al = _acf(rows - rows.mean())
        flo, fhi = 400, min(700, len(al) - 1)
        if fhi > flo:
            frame_lines_meas = flo + int(np.argmax(al[flo:fhi]))

    if abs(line_hz - 15734.0) <= abs(line_hz - 15625.0):
        name, lines_canon, line_hz_canon = "NTSC", 525, 15734.0
    else:
        name, lines_canon, line_hz_canon = "PAL", 625, 15625.0

    return {
        "standard": name,
        "line_samples": int(line_len),
        "line_us": 1e6 / line_hz,
        "line_hz": line_hz,
        "line_hz_canonical": line_hz_canon,
        "frame_lines_measured": frame_lines_meas,
        "frame_lines_canonical": lines_canon,
    }


def detect_audio_subcarrier(demod, sample_rate, line_hz=0.0):
    """Detect an FM audio subcarrier near 6.0/6.5 MHz in the composite baseband.
    Rejects candidates that are integer multiples of the line rate, which are
    horizontal-sync harmonics rather than a genuine subcarrier (e.g. for PAL,
    6.0 and 6.5 MHz are exactly 384x and 416x the 15625 Hz line rate)."""
    v = np.asarray(demod, dtype=float)
    v = v[:min(len(v), 2_000_000)]             # bound welch input on large captures
    nper = int(min(131072, len(v)))
    if nper < 1024:
        return {"present": False}
    f, P = signal.welch(v, fs=sample_rate, nperseg=nper)
    PdB = 10.0 * np.log10(P + 1e-20)
    candidates = []
    for target in (6.0e6, 6.5e6):
        if target >= f[-1]:
            continue
        k = int(np.argmin(np.abs(f - target)))
        local = (f > target - 3e5) & (f < target + 3e5)
        prom = float(PdB[k] - np.median(PdB[local]))
        ratio = target / line_hz if line_hz else 0.0
        harmonic = (abs(ratio - round(ratio)) < 0.01) if line_hz else False
        candidates.append({"freq_hz": target, "prominence_db": prom,
                           "harmonic": harmonic, "harmonic_index": int(round(ratio))})
    strong = [c for c in candidates if c["prominence_db"] > 6.0]
    if not strong:
        return {"status": "absent"}
    best = max(strong, key=lambda c: c["prominence_db"])
    # A real subcarrier and a line-rate harmonic can land on the same frequency
    # (on PAL, 6.0/6.5 MHz are exact line harmonics). If the strongest candidate
    # coincides with a harmonic, don't claim a distinct subcarrier.
    if best["harmonic"]:
        return {"status": "ambiguous_harmonic", **best}
    return {"status": "present", **best}


def process_analog_video(samples, sample_rate, line_samples, num_lines, plot_path=None):
    """
    Rasterizes an FM-demodulated analog video baseband signal into a 2D image 
    using an amplitude sync-pulse separator to prevent frame shearing.
    """
    # 1. Demodulate FM envelope
    demod = demodulate_fm(samples, sample_rate)

    # Measure the video standard straight from the demod (label-independent) and
    # auto-derive raster geometry when the operator did not specify it.
    std_info = analyze_video_standard(demod, sample_rate)
    if std_info:
        fl = std_info["frame_lines_measured"]
        fl_txt = f"~{fl} lines/frame" if fl else "frame count unresolved"
        print(f"   📺 Detected standard: {std_info['standard']} "
              f"(line {std_info['line_us']:.2f} us / {std_info['line_hz']:.0f} Hz, {fl_txt})")
    canon_line = std_info["line_hz_canonical"] if std_info else 0.0
    sc = detect_audio_subcarrier(demod, sample_rate, canon_line)
    if sc.get("status") == "present":
        print(f"   🔊 Audio subcarrier: PRESENT near {sc['freq_hz'] / 1e6:.1f} MHz "
              f"(+{sc['prominence_db']:.1f} dB above local floor)")
    elif sc.get("status") == "ambiguous_harmonic":
        print(f"   ⚠️ Audio subcarrier: energy near {sc['freq_hz'] / 1e6:.1f} MHz coincides with the "
              f"{sc['harmonic_index']}x line-rate harmonic — cannot confirm a distinct subcarrier")
    else:
        print(f"   🔇 Audio subcarrier: not detected near 6.0/6.5 MHz")
    if line_samples is None:
        line_samples = std_info["line_samples"] if std_info else 1280
        print(f"   Auto-derived line length: {line_samples} samples/line")
    if num_lines is None:
        num_lines = std_info["frame_lines_canonical"] if std_info else 576

    analysis = {
        "video_standard": std_info["standard"] if std_info else None,
        "video_line_us": round(std_info["line_us"], 3) if std_info else None,
        "video_line_hz": round(std_info["line_hz"], 1) if std_info else None,
        "video_frame_lines": std_info["frame_lines_measured"] if std_info else None,
        "audio_subcarrier_status": sc.get("status", "absent"),
        "audio_subcarrier_hz": sc.get("freq_hz"),
        "audio_subcarrier_prominence_db": (round(sc["prominence_db"], 1)
                                           if "prominence_db" in sc else None),
    }


    if plot_path:
        plot_baseband_dashboard(demod, sample_rate, plot_path.replace(".png", "_dashboard.png"), title="Analog Video Baseband Diagnostics", is_am=False)

    explain_step(
        "Sync Separator & Frame Reconstruction",
        f"Detecting horizontal sync pulses to dynamically lock and align rows of length ~{line_samples} samples.",
        "Frame[line, pixel] = Demod[sync_indices[line] + pixel]"
    )
    
    # 2. Sync Pulse Separation
    # Light low-pass filter to smooth out high frequency video chroma/luma
    from scipy.signal import butter, lfilter
    nyq = 0.5 * sample_rate
    cutoff = 500000.0  # 500 kHz lowpass for syncs
    b, a = butter(2, cutoff / nyq, btype='low')
    demod_lpf = lfilter(b, a, demod)
    
    # Auto-polarity: In standard NTSC/PAL FM, sync pulses are the lowest frequency (most negative).
    # If the SDR tuner inverted the spectrum, they might be positive.
    # We assume sync pulses are sharp, rare extremes. We look at the 1st and 99th percentile.
    p1 = np.percentile(demod_lpf, 1)
    p99 = np.percentile(demod_lpf, 99)
    median = np.median(demod_lpf)
    
    if abs(p1 - median) > abs(p99 - median):
        # Syncs are negative
        threshold = p1 + 0.2 * (median - p1)
        sync_mask = demod_lpf < threshold
    else:
        # Syncs are positive
        threshold = p99 - 0.2 * (p99 - median)
        sync_mask = demod_lpf > threshold
        
    # Find indices where sync_mask goes from False to True (edge detection)
    edges = np.where((sync_mask[:-1] == False) & (sync_mask[1:] == True))[0]
    
    # Debounce: ensure edges are at least 0.8 * line_samples apart
    min_dist = int(line_samples * 0.8)
    sync_indices = []
    if len(edges) > 0:
        last_edge = edges[0]
        sync_indices.append(last_edge)
        for e in edges[1:]:
            if e - last_edge > min_dist:
                sync_indices.append(e)
                last_edge = e

    # Validate sync pulses: if the median distance is wildly different from line_samples,
    # the signal might not have standard sync pulses (e.g., a pure synthetic test pattern).
    use_sync = False
    if len(sync_indices) > 2:
        median_diff = np.median(np.diff(sync_indices))
        if abs(median_diff - line_samples) / line_samples < 0.05:
            use_sync = True
            
    if use_sync:
        print(f"   Detected {len(sync_indices)} valid sync pulses. Rasterizing with Sync-Lock...")
    else:
        print(f"   ⚠️ Could not lock onto regular sync pulses (found {len(sync_indices)} irregular edges).")
        print(f"   Falling back to blind rasterization stride of {line_samples} samples.")
        sync_indices = [int(i * line_samples) for i in range(int(len(demod) / line_samples))]

    # 3. Rasterization
    demod_frame = demod

    # Invert the signal if the polarity is positive (meaning syncs were high)
    is_inverted = False
    if not (abs(p1 - median) > abs(p99 - median)):
        demod_frame = -demod_frame
        is_inverted = True
        
    print(f"   Rasterizing full-bandwidth baseband (Inverted Polarity: {is_inverted})")

    frame = []
    # Try to grab `num_lines` starting from an arbitrary offset, or just grab the first available lines
    start_idx = 0
    # Find a vertical sync (a gap in horizontal syncs or a long sync pulse) to align the frame vertically?
    # For a simple educational tool, we'll just take the first `num_lines` syncs.
    
    for i in range(min(num_lines, len(sync_indices))):
        start = sync_indices[i]
        # To avoid jagged edges on the right side if the sync drifts slightly, 
        # we always take exactly `line_samples` amount of data.
        end = start + line_samples
        if end > len(demod_frame):
            break
        row = demod_frame[start:end]
        frame.append(row)
        
    if len(frame) == 0:
        return np.array([]), analysis
        
    # Normalize the entire frame at once (better than row-by-row to preserve brightness)
    frame_array = np.array(frame)
    # Sync pulses and porches take up ~15-20% of the horizontal space and are the darkest elements.
    # By using the 15th percentile as black, we map the actual active picture black to 0, maximizing contrast.
    f_min = np.percentile(frame_array, 15)
    f_max = np.percentile(frame_array, 98)
    frame_norm = np.clip((frame_array - f_min) / (f_max - f_min + 1e-12), 0, 1) * 255
    
    return frame_norm.astype(np.uint8), analysis



def process_analog_fm(samples, sample_rate, plot_path, verbose=False):
    """
    Demodulates Analog FM signals (e.g., FPV NTSC, Broadcast FM, Marine VHF).
    Instead of performing clock recovery and slicing, it outputs the continuous 
    baseband waveform and plots a comprehensive dashboard.
    """
    demod = demodulate_fm(samples, sample_rate)
    
    if plot_path:
        plot_baseband_dashboard(demod, sample_rate, plot_path, title="Analog FM Baseband Diagnostics", is_am=False)
        
    return demod

def process_analog_am(samples, sample_rate, plot_path, verbose=False):
    """
    Demodulates Analog AM signals (e.g., Aviation, AM Broadcast).
    Extracts the magnitude (envelope) of the complex signal and plots a comprehensive dashboard.
    """
    explain_step(
        "AM Envelope Detector",
        "Computing the absolute magnitude of the complex IQ samples to extract the AM envelope.",
        "y[n] = abs(I[n] + j*Q[n])"
    )
    demod = np.abs(samples)
    
    # Remove DC offset (the carrier)
    demod = demod - np.mean(demod)
    
    if plot_path:
        plot_baseband_dashboard(demod, sample_rate, plot_path, title="Analog AM Baseband Diagnostics", is_am=True)
        
    return demod

def main():
    args = parse_args()
    
    # 1. Resolve SigMF / raw paths + metadata, then read a bounded slice of IQ
    data_path, datatype, sample_rate, frequency = resolve_paths_and_metadata(args)
    if sample_rate:
        args.rate = sample_rate
    if frequency is not None and args.freq is None:
        args.freq = frequency
    max_samples = int(args.duration * args.rate) if args.duration and args.duration > 0 else args.max_samples
    samples = read_iq_samples(data_path, datatype, max_samples)
    print(f"   Loaded {len(samples)} complex samples from {os.path.basename(data_path)} "
          f"(format {datatype}, rate {args.rate / 1e6:.3f} MSPS).")
    
    # 2. Baseband Frequency Shift
    if args.offset_hz != 0:
        samples = apply_frequency_shift(samples, args.rate, args.offset_hz)
        
    # 3. Channel Isolation Filter
    if args.channel_bw:
        samples = apply_channel_filter(samples, args.rate, args.channel_bw)
        
    # Dispatch to appropriate demodulation routine
    if args.mode == "analog_fm":
        demod = process_analog_fm(samples, args.rate, args.plot_path, args.verbose)
        print(f"\n📊 Demodulation Completed (Analog FM Mode)")
        print(f"   Extracted {len(demod)} continuous baseband samples.")
        if args.plot_path:
            print(f"   Plotted 2ms baseband segment to {args.plot_path}")
            
    elif args.mode == "analog_am":
        demod = process_analog_am(samples, args.rate, args.plot_path, args.verbose)
        print(f"\n📊 Demodulation Completed (Analog AM Mode)")
        print(f"   Extracted {len(demod)} continuous baseband samples.")
        if args.plot_path:
            print(f"   Plotted 5ms baseband segment to {args.plot_path}")

    elif args.mode == "fsk":
        bits, sliced_wave = process_fsk(samples, args.rate, args.symbol_rate, args.plot_path, args.verbose)
        
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
        audio = process_fm_audio(samples, args.rate, args.audio_rate)
        
        # Export to wav file
        import scipy.io.wavfile as wav
        output_wav = "demodulated_audio.wav"
        audio_int16 = (audio * 32767).astype(np.int16)
        wav.write(output_wav, int(args.audio_rate), audio_int16)
        
        print(f"\n📊 Demodulation Completed (FM Audio Mode)")
        print(f"   Audio duration: {len(audio)/args.audio_rate:.2f} seconds.")
        print(f"   WAV file saved to: {output_wav}")
        
    elif args.mode == "am_audio":
        audio = process_am_audio(samples, args.rate, args.audio_rate)
        
        # Export to wav file
        import scipy.io.wavfile as wav
        output_wav = "demodulated_audio.wav"
        audio_int16 = (audio * 32767).astype(np.int16)
        wav.write(output_wav, int(args.audio_rate), audio_int16)
        
        print(f"\n📊 Demodulation Completed (AM Audio Mode)")
        print(f"   Audio duration: {len(audio)/args.audio_rate:.2f} seconds.")
        print(f"   WAV file saved to: {output_wav}")
        
    elif args.mode == "ook":
        sliced, run_lengths, run_values = process_ook(samples, args.rate, args.plot_path, args.verbose)
        
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
        symbols = process_psk(samples, args.rate, args.symbol_rate, args.psk_order, args.plot_path, args.verbose)
        
        print(f"\n📊 Demodulation Completed (PSK Mode)")
        print(f"   Recovered Symbols Count: {len(symbols)}")
        print(f"   First 128 Symbols:")
        sym_str = "".join(map(str, symbols[:128]))
        print(f"     [ {sym_str} ]")
        
    elif args.mode == "qam":
        symbols = process_qam(samples, args.rate, args.symbol_rate, args.qam_order, args.plot_path, args.verbose)
        
        print(f"\n📊 Demodulation Completed (QAM Mode)")
        print(f"   Recovered Symbols Count: {len(symbols)}")
        print(f"   (See constellation plot for grid alignment)")

    elif args.mode == "analog_video":
        frame_img, analysis = process_analog_video(samples, args.rate, args.line_samples, args.video_lines, args.plot_path)
        
        if len(frame_img) > 0:
            try:
                import cv2
            except ImportError:
                print("Error: OpenCV (cv2) is required for analog_video mode but is not installed.", file=sys.stderr)
                print("Install it with: pip install opencv-python", file=sys.stderr)
                sys.exit(1)
            
            # Resize to standard 4:3 aspect ratio (640x480) for NTSC/PAL
            frame_resized = cv2.resize(frame_img, (640, 480), interpolation=cv2.INTER_AREA)
            
            output_png = args.plot_path.replace(".png", "_frame.png") if args.plot_path else "reconstructed_frame.png"
            cv2.imwrite(output_png, frame_resized)
            print(f"\n📊 Demodulation Completed (Analog Video Mode)")
            print(f"   Raw dimensions: {frame_img.shape[1]}x{frame_img.shape[0]} (Gray)")
            print(f"   Resized 4:3 frame saved to: {output_png} (640x480)")
            if args.plot_path:
                print(f"   Dashboard saved to: {args.plot_path.replace('.png', '_dashboard.png')}")
        else:
            print("Error: Could not reconstruct any video lines from baseband samples.", file=sys.stderr)

        if args.json_output:
            out = {
                "mode": "analog_video",
                "sample_rate": args.rate,
                "center_freq": args.freq,
                "num_samples": int(len(samples)),
                **analysis,
            }
            with open(args.json_output, "w") as jf:
                json.dump(out, jf, indent=2)
            print(f"   JSON analysis written to: {args.json_output}")

    elif args.mode == "lora":
        symbol_vals = process_lora(samples, args.rate, args.lora_bw, args.lora_sf, args.plot_path, args.verbose)
        print(f"\n📊 Demodulation Completed (LoRa Mode)")
        print(f"   Extracted {len(symbol_vals)} symbols.")
        print(f"   First 32 symbols: {symbol_vals[:32]}")
        print(f"   (See plot for de-chirped FFT peak of the first symbol)")
        
    elif args.mode == "ofdm":
        fft_size = args.ofdm_fft
        cp_len = args.ofdm_cp
        if args.ofdm_profile == "wifi":
            fft_size, cp_len = 64, 16
            print("   Using WiFi OFDM Profile: FFT=64, CP=16")
        elif args.ofdm_profile == "lte":
            fft_size, cp_len = 2048, 144
            print("   Using LTE OFDM Profile: FFT=2048, CP=144")
        elif args.ofdm_profile == "ocusync":
            fft_size, cp_len = 1024, 72 # Approximate
            print("   Using OcuSync OFDM Profile: FFT=1024, CP=72")
        elif args.ofdm_profile == "atsc":
            fft_size, cp_len = 8192, 768 # ATSC 3.0 8K mode example
            print("   Using ATSC 3.0 OFDM Profile: FFT=8192, CP=768")
        elif args.ofdm_profile == "dvb":
            fft_size, cp_len = 2048, 64 # DVB-T 2K mode example
            print("   Using DVB-T OFDM Profile: FFT=2048, CP=64")
            
        subcarriers = process_ofdm(samples, args.rate, fft_size, cp_len, args.ofdm_profile, args.plot_path, args.verbose)
        print(f"\n📊 Demodulation Completed (OFDM Mode)")
        print(f"   Extracted {len(subcarriers)} subcarriers from first valid symbol.")
        print(f"   (See plot for timing sync and subcarrier constellation)")
        
    elif args.mode == "sc-fdma":
        print(f"\n=== SC-FDMA Demodulation Setup ===")
        if args.ofdm_profile == "custom":
            fft_size = args.ofdm_fft
            cp_len = args.ofdm_cp
        else:
            fft_size, cp_len = 1024, 72
            if args.ofdm_profile == "lte":
                print("   Using LTE Uplink SC-FDMA Profile: FFT=1024, CP=72")
            else:
                print(f"   Falling back to generic 1024/72 profile (ignoring downlink-only profile '{args.ofdm_profile}')")
        
        subcarriers, sc_symbols = process_sc_fdma(samples, args.rate, fft_size, cp_len, args.sc_fdma_alloc, args.plot_path, args.verbose)
        print(f"\n📊 Demodulation Completed (SC-FDMA Mode)")
        print(f"   Extracted {len(subcarriers)} total subcarriers, isolated {args.sc_fdma_alloc} subcarriers, and recovered {len(sc_symbols)} time-domain constellation symbols.")
        print(f"   (See plot for the IFFT precoding recovery visualization)")

if __name__ == "__main__":
    main()
