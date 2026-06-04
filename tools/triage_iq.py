#!/usr/bin/env python3
import os
import sys
import json
import argparse
import numpy as np
from scipy import signal
from scipy.ndimage import uniform_filter1d

HAS_MATPLOTLIB = False
try:
    import matplotlib
    matplotlib.use('Agg')  # Headless rendering
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    pass

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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract spectral and temporal features from IQ data to generate an LLM Triage Report."
    )
    parser.add_argument(
        "--file", "-f",
        required=True,
        help="Path to the IQ file (.bin, .cf32, .sigmf-data, or .sigmf-meta)"
    )
    parser.add_argument(
        "--mode",
        choices=["overview", "triage"],
        default="triage",
        help="Run in 'overview' mode (wideband plot only) or 'triage' mode (isolated statistical analysis)"
    )
    parser.add_argument(
        "--offset-hz",
        type=float,
        default=0.0,
        help="Manual frequency offset to isolate signal (used in triage mode)"
    )
    parser.add_argument(
        "--channel-bw",
        type=float,
        default=None,
        help="Channel bandwidth to isolate via low-pass filter (used in triage mode)"
    )
    parser.add_argument(
        "--rate", "-r",
        type=float,
        default=15.36e6,
        help="Sample rate in Hz (default: 15.36 MSPS, ignored if SigMF metadata is available)"
    )
    parser.add_argument(
        "--freq", "-c",
        type=float,
        default=None,
        help="Center frequency in Hz (optional, loaded from SigMF if available)"
    )
    parser.add_argument(
        "--format",
        choices=["cf32_le", "ci16_le"],
        default=None,
        help="IQ data format: cf32_le (float32) or ci16_le (int16). Detected automatically if omitted."
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=2000000,
        help="Maximum samples to read for triage if --duration is 0 (default: 2,000,000)"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0.150,
        help="Duration of IQ data to analyze in seconds (default: 0.150 s / 150 ms). Set to 0 to use --max-samples."
    )
    parser.add_argument(
        "--output", "-o",
        default="triage_report.md",
        help="Output markdown report filename (default: triage_report.md)"
    )
    parser.add_argument(
        "--plot", "-p",
        default="triage_plot.png",
        help="Path to save the visual diagnostic plot (default: triage_plot.png)"
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Disable generating diagnostic plots"
    )
    parser.add_argument(
        "--json-output",
        default=None,
        help="Path to write a JSON file containing all numeric triage metrics"
    )
    parser.add_argument(
        "--keep-dc",
        action="store_true",
        help="Do not suppress the central DC local oscillator (LO) leakage spike in PSD peak finding."
    )
    return parser.parse_args(normalize_numeric_argv())

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
            datatype = "ci16_le" # Default fallback safe for SDR captures
            
    return data_path, datatype, sample_rate, frequency

def read_iq_samples(file_path, datatype, max_samples):
    if not os.path.exists(file_path):
        print(f"Error: Data file not found at {file_path}", file=sys.stderr)
        sys.exit(1)
        
    if datatype == "cf32_le":
        # float32 complex = 2 * 4 bytes = 8 bytes per sample
        bytes_per_sample = 8
        count = max_samples * 2
        raw = np.fromfile(file_path, dtype=np.float32, count=count)
        if len(raw) % 2 != 0:
            raw = raw[:-1]
        samples = raw[0::2] + 1j * raw[1::2]
    elif datatype == "ci16_le":
        # int16 complex = 2 * 2 bytes = 4 bytes per sample
        bytes_per_sample = 4
        count = max_samples * 2
        raw = np.fromfile(file_path, dtype=np.int16, count=count)
        if len(raw) % 2 != 0:
            raw = raw[:-1]
        # Normalize to float32 range [-1.0, 1.0]
        samples = (raw[0::2] + 1j * raw[1::2]) / 32768.0
    else:
        print(f"Error: Unsupported datatype {datatype}", file=sys.stderr)
        sys.exit(1)
        
    return samples

def apply_frequency_shift(samples, sample_rate, offset_hz):
    if offset_hz == 0:
        return samples
    t = np.arange(len(samples)) / sample_rate
    shifted = samples * np.exp(-1j * 2 * np.pi * offset_hz * t)
    return shifted

def apply_channel_filter(samples, sample_rate, channel_bw):
    from scipy.signal import butter, lfilter
    nyq = 0.5 * sample_rate
    cutoff = min(channel_bw / 2.0, nyq - 1000)
    b, a = butter(4, cutoff / nyq, btype='low')
    return lfilter(b, a, samples)

def analyze_spectrum(samples, sample_rate, suppress_dc=True):
    # Compute Power Spectral Density (PSD)
    nperseg = min(8192, len(samples))
    freqs, psd = signal.welch(samples, fs=sample_rate, return_onesided=False, nperseg=nperseg, detrend=False)
    
    # Shift to center
    freqs = np.fft.fftshift(freqs)
    psd = np.fft.fftshift(psd)
    
    # Apply VBW smoothing (moving average over 9 bins to reduce noise floor jitter)
    vbw_window = 9
    psd = np.convolve(psd, np.ones(vbw_window)/vbw_window, mode='same')
    
    # Find peak frequency and max power, suppressing DC offset spike (common LO leakage)
    search_psd = psd.copy()
    if suppress_dc:
        dc_idx = np.argmin(np.abs(freqs))
        # Zero out the central 5 bins around DC to ignore LO spike during peak searching
        search_psd[max(0, dc_idx - 2) : min(len(psd), dc_idx + 3)] = 0.0
    
    peak_idx = np.argmax(search_psd)
    peak_freq = freqs[peak_idx]
    
    # Compute SNR (peak vs median noise floor)
    median_psd = np.median(psd)
    max_psd = psd[peak_idx]
    snr_db = 10 * np.log10(max_psd / (median_psd + 1e-12))
    
    # Occupied Bandwidth (99% power)
    total_power = np.sum(psd)
    cum_power = np.cumsum(psd)
    idx_99_low = np.where(cum_power >= total_power * 0.005)[0][0]
    idx_99_high = np.where(cum_power >= total_power * 0.995)[0][0]
    obw = freqs[idx_99_high] - freqs[idx_99_low]
    
    # Occupied Bandwidth (90% power)
    idx_90_low = np.where(cum_power >= total_power * 0.05)[0][0]
    idx_90_high = np.where(cum_power >= total_power * 0.95)[0][0]
    obw_90 = freqs[idx_90_high] - freqs[idx_90_low]
    
    # Flatness ratio of peak power region (to detect OFDM flat tops)
    # Average power in 50% central region of OBW divided by peak power
    obw_indices = np.where((freqs >= freqs[idx_99_low]) & (freqs <= freqs[idx_99_high]))[0]
    if len(obw_indices) > 10:
        central_region = obw_indices[len(obw_indices)//4 : 3*len(obw_indices)//4]
        avg_central = np.mean(psd[central_region])
        flatness = avg_central / (max_psd + 1e-12)
    else:
        flatness = 0.0

    return {
        "peak_freq": peak_freq,
        "snr_db": snr_db,
        "obw_99": obw,
        "obw_90": obw_90,
        "flatness": flatness,
        "psd": psd,
        "freqs": freqs
    }

def analyze_temporal(samples, sample_rate, snr_db=None, acf_res=None):
    amp = np.abs(samples)
    mean_amp = np.mean(amp)
    std_amp = np.std(amp)
    amp_std_to_mean = std_amp / (mean_amp + 1e-12)

    power = amp ** 2
    # Compute PAPR on the raw power envelope
    mean_power = np.mean(power)
    max_power = np.max(power)
    papr = max_power / (mean_power + 1e-12)
    papr_db = 10 * np.log10(papr)
    
    # Smooth power envelope using a moving average to avoid noise spikes causing fake bursts
    smooth_power = uniform_filter1d(power, size=min(50, len(power) // 10))
    
    # Dynamic log-power thresholding
    log_power = 10 * np.log10(smooth_power + 1e-12)
    max_log = np.max(log_power)
    min_log = np.min(log_power)
    log_range = max_log - min_log
    
    if log_range > 6.0:
        # Use 30% of the range above minimum as threshold
        thresh_db = min_log + 0.3 * log_range
        active_thresh = 10 ** (thresh_db / 10.0)
        active_mask = smooth_power > active_thresh
        duty_cycle = np.mean(active_mask)
    else:
        # Very flat envelope, classify as continuous
        active_thresh = 0.0
        active_mask = np.ones_like(smooth_power, dtype=bool)
        duty_cycle = 1.0
        
    # Try to find burst durations (padding with False to detect boundary-touching bursts)
    padded_mask = np.concatenate([[False], active_mask, [False]])
    diffs = np.diff(padded_mask.astype(int))
    starts = np.where(diffs == 1)[0]
    ends = np.where(diffs == -1)[0]
    
    if len(starts) > 0 and len(ends) > 0:
        min_len = min(len(starts), len(ends))
        burst_lengths = ends[:min_len] - starts[:min_len]
        
        # Filter out bursts shorter than 10 samples (transient noise spikes)
        filtered_bursts = burst_lengths[burst_lengths >= 10]
        if len(filtered_bursts) > 0:
            avg_burst_samples = np.mean(filtered_bursts)
            max_burst_samples = np.max(filtered_bursts)
        else:
            avg_burst_samples = 0.0
            max_burst_samples = 0.0
    else:
        avg_burst_samples = 0.0
        max_burst_samples = 0.0

    # Demodulate FM to get instantaneous frequency deviation statistics
    n_fm = min(100000, len(samples))
    sub_samples = samples[:n_fm]
    if len(sub_samples) > 2:
        phase_diff = np.angle(sub_samples[1:] * np.conjugate(sub_samples[:-1]))
        inst_freq = phase_diff * sample_rate / (2 * np.pi)
        
        # Only compute on active region
        sub_power = power[:n_fm-1]
        active_sub = sub_power > active_thresh
        if np.sum(active_sub) > 100:
            active_freqs = inst_freq[active_sub]
            # Robust active frequency detrending (invariant to center frequency offsets)
            active_freqs_detrend = active_freqs - np.mean(active_freqs)
            freq_std_hz = np.std(active_freqs_detrend)
            freq_dev_hz = np.percentile(np.abs(active_freqs_detrend), 95)
        else:
            inst_freq_detrend = inst_freq - np.mean(inst_freq)
            freq_std_hz = np.std(inst_freq_detrend)
            freq_dev_hz = np.percentile(np.abs(inst_freq_detrend), 95)
    else:
        freq_std_hz = 0.0
        freq_dev_hz = 0.0
        
    # Calculate Frequency Distribution Shape (CSS / Chirp indicator)
    freq_dist_shape = freq_std_hz / (freq_dev_hz + 1e-12)
    
    # Determine low SNR / noisy status
    is_noisy = snr_db is not None and snr_db < 5.0
    if is_noisy and acf_res is not None:
        peak_vals = acf_res.get("peak_vals", [])
        if len(peak_vals) > 0 and max(peak_vals) > 0.2:
            is_noisy = False
        
    return {
        "papr_db": float(papr_db),
        "amp_std_to_mean": float(amp_std_to_mean),
        "freq_std_hz": float(freq_std_hz),
        "freq_dev_hz": float(freq_dev_hz),
        "freq_dist_shape": float(freq_dist_shape),
        "duty_cycle": float(duty_cycle),
        "avg_burst_samples": float(avg_burst_samples),
        "max_burst_samples": float(max_burst_samples),
        "is_bursty": bool(duty_cycle < 0.85 and papr_db > 6.0 and not is_noisy),
        "is_noisy": bool(is_noisy)
    }

def analyze_autocorrelation(samples, sample_rate, max_lag=4000):
    # Standard autocorrelation to find periodic signals (OFDM symbol duration, etc.)
    # We do this on a subset to keep execution fast
    n_acf = min(100000, len(samples))
    subset = samples[:n_acf]
    
    # Compute auto-correlation
    acf = np.correlate(subset, subset, mode='full')
    acf = acf[acf.size // 2:]
    acf_mag = np.abs(acf)
    acf_mag = acf_mag / (acf_mag[0] + 1e-12) # Normalize
    
    # Find peaks in autocorrelation (excluding the zero lag)
    # Set height threshold and distance threshold
    min_dist = 10
    peaks, properties = signal.find_peaks(acf_mag[min_dist:max_lag], height=0.1, distance=20)
    peaks = peaks + min_dist
    
    peak_lags = []
    peak_vals = []
    if len(peaks) > 0:
        # Sort by peak value
        sorted_indices = np.argsort(acf_mag[peaks])[::-1]
        for idx in sorted_indices[:5]: # Take top 5 peaks
            lag = peaks[idx]
            val = acf_mag[lag]
            peak_lags.append(int(lag))
            peak_vals.append(float(val))
            
    return {
        "peak_lags": peak_lags,
        "peak_vals": peak_vals,
        "acf_mag": acf_mag,
        "sample_rate": sample_rate
    }

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

def generate_overview_plot(samples, sample_rate, spec_res, plot_path):
    if not HAS_MATPLOTLIB:
        print("Warning: matplotlib not installed. Skipping image plot generation.", file=sys.stderr)
        return False
        
    try:
        apply_premium_dark_theme()
        
        # Create a 1x2 wide grid for the overview
        fig, axs = plt.subplots(1, 2, figsize=(20, 8))
        
        # 1. PSD Plot (Left)
        ax = axs[0]
        freqs_mhz = spec_res["freqs"] / 1e6
        psd_db = 10 * np.log10(spec_res["psd"] + 1e-12)
        ax.plot(freqs_mhz, psd_db, color='#00E5FF', linewidth=1.5, label='PSD')
        ax.fill_between(freqs_mhz, psd_db, np.min(psd_db), color='#00E5FF', alpha=0.12)
        ax.set_title("Wideband Power Spectral Density (PSD)", fontsize=13, fontweight='bold', color='#E2E8F0')
        ax.set_xlabel("Frequency (MHz relative to Center)", fontsize=11)
        ax.set_ylabel("Power (dB)", fontsize=11)
        ax.grid(True)
        
        # 2. Spectrogram Plot (Right)
        ax = axs[1]
        n_fft = 1024  # Higher res for overview
        n_overlap = 512
        f_s, t_s, Sxx = signal.spectrogram(samples[:500000], fs=sample_rate, nperseg=n_fft, noverlap=n_overlap, return_onesided=False)
        f_s = np.fft.fftshift(f_s)
        Sxx = np.fft.fftshift(Sxx, axes=0)
        
        Sxx = uniform_filter1d(Sxx, size=3, axis=0)
            
        f_s_mhz = f_s / 1e6
        t_s_ms = t_s * 1000.0
        
        Sxx_db = 10 * np.log10(Sxx + 1e-12)
        vmax = np.max(Sxx_db)
        vmin = vmax - 50.0
        
        pcm = ax.pcolormesh(t_s_ms, f_s_mhz, Sxx_db, shading='gouraud', cmap='turbo', vmin=vmin, vmax=vmax)
        ax.set_title("Wideband Spectrogram / Waterfall", fontsize=13, fontweight='bold', color='#E2E8F0')
        ax.set_xlabel("Time (ms)", fontsize=11)
        ax.set_ylabel("Frequency (MHz)", fontsize=11)
        
        cbar = fig.colorbar(pcm, ax=ax, label='Power (dB)')
        cbar.ax.yaxis.label.set_color('#E2E8F0')
        cbar.ax.tick_params(colors='#E2E8F0')
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"Overview dashboard image saved successfully to: {plot_path}")
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error generating overview plots: {e}", file=sys.stderr)
        return False

def generate_diagnostic_plots(samples, sample_rate, spec_res, temp_res, acf_res, plot_path):
    if not HAS_MATPLOTLIB:
        print("Warning: matplotlib not installed. Skipping image plot generation.", file=sys.stderr)
        return False
        
    try:
        apply_premium_dark_theme()
        
        # Create a 2x3 grid
        fig, axs = plt.subplots(2, 3, figsize=(16, 10))
        
        # 1. PSD Plot (Top-Left)
        ax = axs[0, 0]
        freqs_mhz = spec_res["freqs"] / 1e6
        psd_db = 10 * np.log10(spec_res["psd"] + 1e-12)
        ax.plot(freqs_mhz, psd_db, color='#00E5FF', linewidth=1.5, label='PSD')
        ax.fill_between(freqs_mhz, psd_db, np.min(psd_db), color='#00E5FF', alpha=0.12)
        ax.set_title("Power Spectral Density (PSD)", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax.set_xlabel("Frequency (MHz relative to Center)", fontsize=9)
        ax.set_ylabel("Power (dB)", fontsize=9)
        ax.grid(True)
        
        # Draw occupied bandwidth lines
        obw_99 = spec_res["obw_99"] / 1e6
        peak_f = spec_res["peak_freq"] / 1e6
        ax.axvline(peak_f, color='#FF007F', linestyle=':', label=f'Peak ({peak_f:+.2f} MHz)')
        ax.axvspan(peak_f - obw_99/2, peak_f + obw_99/2, color='#00E676', alpha=0.1, label=f'99% OBW ({obw_99:.2f} MHz)')
        ax.legend(loc='lower center', facecolor='#161B26', edgecolor='#2A3142', labelcolor='#E2E8F0', fontsize=8)
        
        # 2. Spectrogram Plot (Top-Middle)
        ax = axs[0, 1]
        n_fft = 512
        n_overlap = 384
        # Pass return_onesided=False to silence warning
        f_s, t_s, Sxx = signal.spectrogram(samples[:100000], fs=sample_rate, nperseg=n_fft, noverlap=n_overlap, return_onesided=False)
        f_s = np.fft.fftshift(f_s)
        Sxx = np.fft.fftshift(Sxx, axes=0)
        
        # Apply VBW smoothing on waterfall (frequency axis smoothing)
        Sxx = uniform_filter1d(Sxx, size=5, axis=0)
            
        f_s_mhz = f_s / 1e6
        t_s_ms = t_s * 1000.0
        
        Sxx_db = 10 * np.log10(Sxx + 1e-12)
        
        # Set dynamic color scale limits to make the signal pop against a dark noise floor
        vmax = np.max(Sxx_db)
        vmin = vmax - 45.0
        
        pcm = ax.pcolormesh(t_s_ms, f_s_mhz, Sxx_db, shading='gouraud', cmap='turbo', vmin=vmin, vmax=vmax)
        ax.set_title("Spectrogram / Waterfall (First 100k)", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax.set_xlabel("Time (ms)", fontsize=9)
        ax.set_ylabel("Frequency (MHz)", fontsize=9)
        
        # Zoom in on the active occupied bandwidth to show the keying tracks clearly
        peak_f = spec_res["peak_freq"]
        obw = spec_res["obw_99"]
        y_limit_low = max(-sample_rate/2, peak_f - 1.5 * obw) / 1e6
        y_limit_high = min(sample_rate/2, peak_f + 1.5 * obw) / 1e6
        ax.set_ylim(y_limit_low, y_limit_high)
        
        cbar = fig.colorbar(pcm, ax=ax, label='Power (dB)')
        cbar.ax.yaxis.label.set_color('#E2E8F0')
        cbar.ax.tick_params(colors='#E2E8F0')
        
        # 3. IQ Constellation Plot (Top-Right)
        ax = axs[0, 2]
        # Plot up to 10,000 raw complex samples
        num_const = min(10000, len(samples))
        const_samples = samples[:num_const]
        ax.scatter(const_samples.real, const_samples.imag, color='#00E5FF', s=1.5, alpha=0.25, label='Raw IQ')
        ax.axhline(0, color='#2A3142', linestyle='--', linewidth=0.8)
        ax.axvline(0, color='#2A3142', linestyle='--', linewidth=0.8)
        ax.set_title("IQ Constellation (Raw Baseband)", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax.set_xlabel("In-Phase (I)", fontsize=9)
        ax.set_ylabel("Quadrature (Q)", fontsize=9)
        ax.set_aspect('equal', 'box')
        ax.grid(True)
        # Dynamic limits based on max amp to keep it compact
        max_amp = np.max(np.abs(const_samples))
        ax.set_xlim(-max_amp * 1.15, max_amp * 1.15)
        ax.set_ylim(-max_amp * 1.15, max_amp * 1.15)
        
        # 4. Temporal Power Envelope (Bottom-Left)
        ax = axs[1, 0]
        power = np.abs(samples[:50000]) ** 2
        t_envelope_ms = (np.arange(len(power)) / sample_rate) * 1000.0
        
        # Smooth envelope for primary trace, overlay on top of lighter raw envelope
        smooth_power_env = uniform_filter1d(power, size=min(100, len(power) // 10))
        ax.plot(t_envelope_ms, power, color='#FF9100', alpha=0.15, label='Raw Envelope')
        ax.plot(t_envelope_ms, smooth_power_env, color='#FF9100', linewidth=1.5, alpha=0.9, label='Smoothed Envelope')
        ax.fill_between(t_envelope_ms, smooth_power_env, 0, color='#FF9100', alpha=0.08)
        
        # Recalculate dynamic active threshold for visualization
        smooth_power_full = uniform_filter1d(np.abs(samples) ** 2, size=min(50, len(samples) // 10))
        log_power = 10 * np.log10(smooth_power_full + 1e-12)
        log_range = np.max(log_power) - np.min(log_power)
        if log_range > 6.0:
            thresh_db = np.min(log_power) + 0.3 * log_range
            active_thresh = 10 ** (thresh_db / 10.0)
        else:
            active_thresh = 0.5 * np.mean(power)
            
        ax.axhline(active_thresh, color='#FF007F', linestyle='--', label='Slicing Threshold')
        ax.set_title("Temporal Power Envelope (First 50k)", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax.set_xlabel("Time (ms)", fontsize=9)
        ax.set_ylabel("Power", fontsize=9)
        ax.grid(True)
        ax.legend(loc='upper right', facecolor='#161B26', edgecolor='#2A3142', labelcolor='#E2E8F0', fontsize=8)
        
        # 5. Autocorrelation (Bottom-Middle)
        ax = axs[1, 1]
        acf_mag = acf_res['acf_mag']
        acf_sample_rate = acf_res['sample_rate']
        
        lag_time_us = (np.arange(len(acf_mag)) / acf_sample_rate) * 1e6
        max_plot_lag = min(4000, len(acf_mag))
        ax.plot(lag_time_us[:max_plot_lag], acf_mag[:max_plot_lag], color='#BF5AF2', linewidth=1.5, label='ACF')
        ax.fill_between(lag_time_us[:max_plot_lag], acf_mag[:max_plot_lag], 0, color='#BF5AF2', alpha=0.1)
        ax.set_title("Autocorrelation Magnitude", fontsize=11, fontweight='bold', color='#E2E8F0')
        ax.set_xlabel("Lag (µs)", fontsize=9)
        ax.set_ylabel("Correlation Coefficient", fontsize=9)
        ax.grid(True)
        
        sample_period_us = 1e6 / sample_rate
        for lag in acf_res["peak_lags"][:3]:
            lag_us = lag * sample_period_us
            if lag_us < lag_time_us[max_plot_lag-1]:
                ax.axvline(lag_us, color='#FF007F', linestyle=':', alpha=0.6)
                ax.text(lag_us, 0.82, f" {lag_us:.1f}µs", rotation=90, color='#FF007F', fontsize=8, fontweight='bold')
                ax.scatter(lag_us, acf_mag[lag], color='#FF007F', marker='o', s=20, zorder=5)
                
        # 6. Instantaneous Frequency Deviation Histogram (Bottom-Right)
        ax = axs[1, 2]
        # Calculate FM demodulated phase difference to get frequency deviation
        n_fm = min(100000, len(samples))
        sub_samples = samples[:n_fm]
        if len(sub_samples) > 2:
            phase_diff = np.angle(sub_samples[1:] * np.conjugate(sub_samples[:-1]))
            inst_freq = phase_diff * sample_rate / (2 * np.pi)
            
            # Recalculate envelope active mask for histogram gating
            power_fm = np.abs(sub_samples[:-1]) ** 2
            smooth_power_fm = uniform_filter1d(power_fm, size=min(50, len(power_fm) // 10))
            active_fm = smooth_power_fm > active_thresh
            
            if np.sum(active_fm) > 100:
                active_freqs = inst_freq[active_fm]
                active_freqs_detrend = active_freqs - np.mean(active_freqs)
            else:
                active_freqs_detrend = inst_freq - np.mean(inst_freq)
                
            # Plot the distribution of the active burst frequency deviation
            ax.hist(active_freqs_detrend / 1e3, bins=60, color='#00E676', alpha=0.4, edgecolor='#00E676', linewidth=1.2, histtype='stepfilled')
            ax.set_title("Frequency Deviation Distribution", fontsize=11, fontweight='bold', color='#E2E8F0')
            ax.set_xlabel("Frequency Deviation (kHz)", fontsize=9)
            ax.set_ylabel("Sample Count", fontsize=9)
        else:
            ax.text(0.5, 0.5, "Insufficient samples\nfor FM deviation", ha='center', va='center', color='#94A3B8')
            ax.set_title("Frequency Deviation Distribution", fontsize=11, fontweight='bold', color='#E2E8F0')
            
        ax.grid(True)
        
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"Diagnostic dashboard image saved successfully to: {plot_path}")
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error generating diagnostic plots: {e}", file=sys.stderr)
        return False

def write_markdown_report(output_path, file_path, datatype, rate, freq, spec_res, temp_res, acf_res, plot_filename=None, suppress_dc=True):
    num_samples = spec_res["freqs"].size
    
    # Build text representation of PSD (ascii plot) in decibel (logarithmic) scale
    bins = 40
    step = len(spec_res["psd"]) // bins
    ascii_psd = []
    psd_db = 10 * np.log10(spec_res["psd"] + 1e-12)
    max_val = np.max(psd_db)
    min_val = np.min(psd_db)
    val_range = max_val - min_val + 1e-12
    
    for i in range(bins):
        chunk = psd_db[i*step : (i+1)*step]
        avg = np.mean(chunk)
        norm_val = int(((avg - min_val) / val_range) * 8)
        char = " _..,,--==##"[norm_val]
        ascii_psd.append(char)
    ascii_psd_str = "".join(ascii_psd)
    
    # Convert duration metrics to milliseconds/microseconds
    sample_period_us = 1e6 / rate
    avg_burst_ms = (temp_res["avg_burst_samples"] * sample_period_us) / 1000.0
    max_burst_ms = (temp_res["max_burst_samples"] * sample_period_us) / 1000.0
    
    # Format lags
    lags_info = []
    for lag, val in zip(acf_res["peak_lags"], acf_res["peak_vals"]):
        lag_time_us = lag * sample_period_us
        lags_info.append(f"Lag: {lag} samples ({lag_time_us:.2f} µs) | Correlation: {val:.3f}")
    lags_str = "\n".join([f"- {item}" for item in lags_info]) if lags_info else "No significant periodic peaks found."

    # Render Visuals Section
    visual_section = ""
    if plot_filename:
        visual_section = f"\n## 🎨 Visual Diagnostics\n![Triage Diagnostic Plot]({plot_filename})\n"

    # Render Report
    report = f"""# IQ Capture Triage Report 📊

This report has been automatically compiled by `triage_iq.py` from raw capture metadata and statistical analysis. It is optimized to be pasted directly into an LLM equipped with the **SigInt RF Skill**.

{visual_section}
---

## 💾 Capture Metadata
* **File Source**: `{os.path.basename(file_path)}`
* **Sample Rate**: `{rate / 1e6:.4f} MSPS` (Sampling Period: `{sample_period_us:.4f} µs`)
* **Datatype Format**: `{datatype}`
* **Assigned Center Frequency**: `{f"{freq / 1e6:.2f} MHz" if freq is not None else "Unknown"}`
* **LO DC Suppression**: `{"Enabled (zeroed central 5 bins)" if suppress_dc else "Disabled (kept DC center bin)"}`

---

## 📈 Spectral Characteristics
* **Peak Power Frequency (Relative to Center)**: `{spec_res["peak_freq"] / 1e6:+.4f} MHz`
* **Estimated Occupied Bandwidth (99% Power)**: `{spec_res["obw_99"] / 1e6:.4f} MHz`
* **Estimated Occupied Bandwidth (90% Power)**: `{spec_res["obw_90"] / 1e6:.4f} MHz`
* **Estimated SNR (Peak-to-Median)**: `{spec_res["snr_db"]:.2f} dB`
* **OFDM Flatness Ratio (Central 50% vs. Peak)**: `{spec_res["flatness"]:.3f}` *(Values >0.7 indicate a flat-top multi-carrier OFDM signal)*

### ASCII PSD Shape:
```
Low-Freq [{ascii_psd_str}] High-Freq
```

---

## ⏱ Temporal & Modulation Characteristics
* **Peak-to-Average Power Ratio (PAPR)**: `{temp_res["papr_db"]:.2f} dB`
* **Amplitude Variation Coefficient (Std/Mean)**: `{temp_res["amp_std_to_mean"]:.4f}` *(High values >0.4 suggest OOK/ASK or high-order QAM)*
* **Frequency Deviation (95% Peak)**: `{temp_res["freq_dev_hz"] / 1e3:.2f} kHz`
* **Frequency Standard Deviation**: `{temp_res["freq_std_hz"] / 1e3:.2f} kHz`
* **FM Sweep Shape (Std/Peak Ratio)**: `{temp_res["freq_dist_shape"]:.3f}` *(~0.58 indicates a uniform CSS/Chirp sweep. ~1.0 indicates discrete FSK)*
* **Duty Cycle (Active power ratio)**: `{temp_res["duty_cycle"] * 100:.2f}%`
* **Temporal Classification**: `{"NOISY (No signal detected or SNR too low)" if temp_res.get("is_noisy", False) else ("BURSTY (Packetized)" if temp_res["is_bursty"] else "CONTINUOUS (Streaming or Constant FM)")}`
* **Average Active Burst Duration**: `{avg_burst_ms:.3f} ms` (`{temp_res["avg_burst_samples"]:.1f}` samples)
* **Maximum Active Burst Duration**: `{max_burst_ms:.3f} ms` (`{temp_res["max_burst_samples"]:.1f}` samples)

---

## 🧬 Autocorrelation Periodicities (Cyclic Structure)
{lags_str}

"""
    with open(output_path, "w") as f:
        f.write(report)
    print(f"Triage report written successfully to: {output_path}")

def write_overview_report(output_path, file_path, datatype, rate, freq, spec_res, plot_filename=None):
    bins = 40
    step = len(spec_res["psd"]) // bins
    ascii_psd = []
    psd_db = 10 * np.log10(spec_res["psd"] + 1e-12)
    max_val = np.max(psd_db)
    min_val = np.min(psd_db)
    val_range = max_val - min_val + 1e-12
    
    for i in range(bins):
        chunk = psd_db[i*step : (i+1)*step]
        avg = np.mean(chunk)
        norm_val = int(((avg - min_val) / val_range) * 8)
        char = " _..,,--==##"[norm_val]
        ascii_psd.append(char)
    ascii_psd_str = "".join(ascii_psd)
    
    visual_section = f"\n## 🎨 Wideband Visual Overview\n![Overview Plot]({plot_filename})\n" if plot_filename else ""
    
    report = f"""# IQ Capture Wideband Overview 📡

This report provides a global snapshot of the capture file. If multiple multiplexed signals are visible in the waterfall or in the metadata annotations, you must use triage mode on a specific signal before attempting demodulation.

{visual_section}
---

## 💾 Capture Metadata
* **File Source**: `{os.path.basename(file_path)}`
* **Sample Rate**: `{rate / 1e6:.4f} MSPS`
* **Datatype Format**: `{datatype}`
* **Assigned Center Frequency**: `{f"{freq / 1e6:.2f} MHz" if freq is not None else "Unknown"}`

### ASCII PSD Shape:
```
Low-Freq [{ascii_psd_str}] High-Freq
```
"""
    with open(output_path, "w") as f:
        f.write(report)
    print(f"Overview report written successfully to: {output_path}")

def main():
    args = parse_args()
    
    # 1. Resolve paths and extract metadata
    data_path, datatype, sample_rate, frequency = resolve_paths_and_metadata(args)
    print(f"Resolved file: {data_path}")
    print(f"Format: {datatype} | Sample Rate: {sample_rate / 1e6:.3f} MSPS | Center Freq: {frequency}")
    
    # 2. Read IQ data
    max_samples = args.max_samples
    if args.duration > 0:
        max_samples = int(args.duration * sample_rate)
        
    samples = read_iq_samples(data_path, datatype, max_samples)
    print(f"Read {len(samples)} complex samples successfully.")
    
    if args.mode == "overview":
        # 3. Compute spectral metrics ONLY
        spec_res = analyze_spectrum(samples, sample_rate, suppress_dc=not args.keep_dc)
        
        plot_filename = None
        if HAS_MATPLOTLIB and not args.no_plot:
            plot_filename = args.plot
            generate_overview_plot(samples, sample_rate, spec_res, plot_filename)
            
        write_overview_report(args.output, args.file, datatype, sample_rate, frequency, spec_res, plot_filename)
        return
        
    # --- TRIAGE MODE ---
    # Apply filters if requested
    if args.offset_hz != 0:
        samples = apply_frequency_shift(samples, sample_rate, args.offset_hz)
    if args.channel_bw:
        samples = apply_channel_filter(samples, sample_rate, args.channel_bw)
        
    # 3. Compute spectral metrics
    spec_res = analyze_spectrum(samples, sample_rate, suppress_dc=not args.keep_dc)
    
    # 4. Compute autocorrelation periodicities
    acf_res = analyze_autocorrelation(samples, sample_rate)
    
    # 5. Compute temporal metrics
    temp_res = analyze_temporal(samples, sample_rate, snr_db=spec_res["snr_db"], acf_res=acf_res)
    
    # 6. Generate plots if matplotlib is available
    plot_filename = None
    if HAS_MATPLOTLIB and not args.no_plot:
        plot_filename = args.plot
        generate_diagnostic_plots(samples, sample_rate, spec_res, temp_res, acf_res, plot_filename)
        
    # 7. Write markdown output
    write_markdown_report(args.output, args.file, datatype, sample_rate, frequency, spec_res, temp_res, acf_res, plot_filename, suppress_dc=not args.keep_dc)

    # 8. Write JSON metrics output if requested
    if args.json_output:
        json_metrics = {
            "peak_freq": float(spec_res["peak_freq"]),
            "snr_db": float(spec_res["snr_db"]),
            "obw_99": float(spec_res["obw_99"]),
            "obw_90": float(spec_res["obw_90"]),
            "flatness": float(spec_res["flatness"]),
            "papr_db": float(temp_res["papr_db"]),
            "amp_std_to_mean": float(temp_res["amp_std_to_mean"]),
            "freq_std_hz": float(temp_res["freq_std_hz"]),
            "freq_dev_hz": float(temp_res["freq_dev_hz"]),
            "freq_dist_shape": float(temp_res["freq_dist_shape"]),
            "duty_cycle": float(temp_res["duty_cycle"]),
            "is_bursty": bool(temp_res["is_bursty"]),
            "avg_burst_samples": float(temp_res["avg_burst_samples"]),
            "max_burst_samples": float(temp_res["max_burst_samples"]),
            "peak_lags": [int(x) for x in acf_res["peak_lags"]],
            "peak_vals": [float(x) for x in acf_res["peak_vals"]],
        }
        with open(args.json_output, "w") as jf:
            json.dump(json_metrics, jf, indent=2)
        print(f"JSON metrics written to: {args.json_output}")

if __name__ == "__main__":
    main()
