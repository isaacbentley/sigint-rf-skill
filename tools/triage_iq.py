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
    return parser.parse_args()

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
    elif ext == ".sigmf-data" or os.path.exists(filepath + ".sigmf-meta"):
        meta_path = filepath + ".sigmf-meta" if ext != ".sigmf-data" else filename + ".sigmf-meta"
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

def analyze_spectrum(samples, sample_rate):
    # Compute Power Spectral Density (PSD)
    nperseg = min(8192, len(samples))
    freqs, psd = signal.welch(samples, fs=sample_rate, return_onesided=False, nperseg=nperseg, detrend=False)
    
    # Shift to center
    freqs = np.fft.fftshift(freqs)
    psd = np.fft.fftshift(psd)
    
    # Apply VBW smoothing (moving average over 9 bins to reduce noise floor jitter)
    vbw_window = 9
    psd = np.convolve(psd, np.ones(vbw_window)/vbw_window, mode='same')
    
    # Find peak frequency and max power
    peak_idx = np.argmax(psd)
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

def analyze_temporal(samples, sample_rate):
    amp = np.abs(samples)
    mean_amp = np.mean(amp)
    std_amp = np.std(amp)
    amp_std_to_mean = std_amp / (mean_amp + 1e-12)

    power = amp ** 2
    mean_power = np.mean(power)
    max_power = np.max(power)
    papr = max_power / (mean_power + 1e-12)
    papr_db = 10 * np.log10(papr)
    
    # Duty cycle & burst detection
    median_power = np.median(power)
    active_thresh = 3.0 * median_power
    active_mask = power > active_thresh
    duty_cycle = np.mean(active_mask)
    
    # Try to find burst durations
    diffs = np.diff(active_mask.astype(int))
    starts = np.where(diffs == 1)[0]
    ends = np.where(diffs == -1)[0]
    
    if len(starts) > 0 and len(ends) > 0:
        if ends[0] < starts[0]:
            ends = ends[1:]
        min_len = min(len(starts), len(ends))
        burst_lengths = ends[:min_len] - starts[:min_len]
        avg_burst_samples = np.mean(burst_lengths)
        max_burst_samples = np.max(burst_lengths)
    else:
        avg_burst_samples = 0.0
        max_burst_samples = 0.0

    # Demodulate FM to get instantaneous frequency deviation statistics
    n_fm = min(100000, len(samples))
    sub_samples = samples[:n_fm]
    if len(sub_samples) > 2:
        phase_diff = np.angle(sub_samples[1:] * np.conjugate(sub_samples[:-1]))
        inst_freq = phase_diff * sample_rate / (2 * np.pi)
        inst_freq_detrend = inst_freq - np.mean(inst_freq)
        
        # Only compute on active region
        sub_power = power[:n_fm-1]
        active_sub = sub_power > active_thresh
        if np.sum(active_sub) > 100:
            active_freqs = inst_freq_detrend[active_sub]
            freq_std_hz = np.std(active_freqs)
            freq_dev_hz = np.percentile(np.abs(active_freqs), 95)
        else:
            freq_std_hz = np.std(inst_freq_detrend)
            freq_dev_hz = np.percentile(np.abs(inst_freq_detrend), 95)
    else:
        freq_std_hz = 0.0
        freq_dev_hz = 0.0
        
    return {
        "papr_db": papr_db,
        "amp_std_to_mean": amp_std_to_mean,
        "freq_std_hz": freq_std_hz,
        "freq_dev_hz": freq_dev_hz,
        "duty_cycle": duty_cycle,
        "avg_burst_samples": avg_burst_samples,
        "max_burst_samples": max_burst_samples,
        "is_bursty": duty_cycle < 0.85 and papr_db > 6.0
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
            peak_lags.append(lag)
            peak_vals.append(val)
            
    return {
        "peak_lags": peak_lags,
        "peak_vals": peak_vals,
        "acf_mag": acf_mag,
        "sample_rate": sample_rate
    }

def generate_diagnostic_plots(samples, sample_rate, spec_res, temp_res, acf_res, plot_path):
    if not HAS_MATPLOTLIB:
        print("Warning: matplotlib not installed. Skipping image plot generation.", file=sys.stderr)
        return False
        
    try:
        # Create a 2x2 grid
        fig, axs = plt.subplots(2, 2, figsize=(12, 10))
        fig.suptitle(f"IQ Capture Diagnostic Dashboard\nSource: {os.path.basename(plot_path)}", fontsize=16, fontweight='bold')
        
        # 1. PSD Plot (Top-Left)
        ax = axs[0, 0]
        freqs_mhz = spec_res["freqs"] / 1e6
        psd_db = 10 * np.log10(spec_res["psd"] + 1e-12)
        ax.plot(freqs_mhz, psd_db, color='tab:blue', label='PSD')
        ax.set_title("Power Spectral Density (PSD)")
        ax.set_xlabel("Frequency (MHz relative to Center)")
        ax.set_ylabel("Power (dB)")
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # Draw occupied bandwidth lines
        obw_99 = spec_res["obw_99"] / 1e6
        peak_f = spec_res["peak_freq"] / 1e6
        ax.axvline(peak_f, color='tab:red', linestyle=':', label=f'Peak ({peak_f:+.2f} MHz)')
        ax.axvspan(peak_f - obw_99/2, peak_f + obw_99/2, color='tab:green', alpha=0.15, label=f'99% OBW ({obw_99:.2f} MHz)')
        ax.legend(loc='lower center')
        
        # 2. Spectrogram Plot (Top-Right)
        ax = axs[0, 1]
        n_fft = min(8192, len(samples))
        f_s, t_s, Sxx = signal.spectrogram(samples[:100000], fs=sample_rate, nperseg=n_fft)
        f_s = np.fft.fftshift(f_s)
        Sxx = np.fft.fftshift(Sxx, axes=0)
        
        # Apply VBW smoothing on waterfall (frequency axis smoothing)
        Sxx = uniform_filter1d(Sxx, size=5, axis=0)
            
        f_s_mhz = f_s / 1e6
        t_s_ms = t_s * 1000.0
        
        Sxx_db = 10 * np.log10(Sxx + 1e-12)
        pcm = ax.pcolormesh(t_s_ms, f_s_mhz, Sxx_db, shading='gouraud', cmap='viridis')
        ax.set_title("Spectrogram / Waterfall (First 100k samples)")
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Frequency (MHz)")
        fig.colorbar(pcm, ax=ax, label='Power (dB)')
        
        # 3. Temporal Power Envelope (Bottom-Left)
        ax = axs[1, 0]
        power = np.abs(samples[:50000]) ** 2
        t_envelope_ms = (np.arange(len(power)) / sample_rate) * 1000.0
        ax.plot(t_envelope_ms, power, color='tab:orange', alpha=0.8)
        
        median_power = np.median(power)
        active_thresh = 3.0 * median_power
        ax.axhline(active_thresh, color='tab:red', linestyle='--', label='Burst Slicing Threshold')
        ax.set_title("Time-Domain Power Envelope (First 50k samples)")
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Power")
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend()
        
        # 4. Autocorrelation (Bottom-Right)
        ax = axs[1, 1]
        acf_mag = acf_res['acf_mag']
        acf_sample_rate = acf_res['sample_rate']
        
        lag_time_us = (np.arange(len(acf_mag)) / acf_sample_rate) * 1e6
        max_plot_lag = min(4000, len(acf_mag))
        ax.plot(lag_time_us[:max_plot_lag], acf_mag[:max_plot_lag], color='tab:purple')
        ax.set_title("Autocorrelation Magnitude vs. Lag")
        ax.set_xlabel("Lag (µs)")
        ax.set_ylabel("Correlation Coefficient")
        ax.grid(True, linestyle='--', alpha=0.6)
        
        sample_period_us = 1e6 / sample_rate
        for lag in acf_res["peak_lags"][:3]:
            lag_us = lag * sample_period_us
            if lag_us < lag_time_us[max_plot_lag-1]:
                ax.axvline(lag_us, color='tab:red', linestyle=':', alpha=0.7)
                ax.text(lag_us, 0.8, f"{lag_us:.1f}µs", rotation=90, color='tab:red', fontsize=8)
                
        plt.tight_layout()
        plt.savefig(plot_path, dpi=150)
        plt.close()
        print(f"Diagnostic dashboard image saved successfully to: {plot_path}")
        return True
    except Exception as e:
        print(f"Error generating diagnostic plots: {e}", file=sys.stderr)
        return False

def write_markdown_report(output_path, file_path, datatype, rate, freq, spec_res, temp_res, acf_res, plot_filename=None):
    num_samples = spec_res["freqs"].size
    
    # Build text representation of PSD (ascii plot)
    bins = 40
    step = len(spec_res["psd"]) // bins
    ascii_psd = []
    max_val = np.max(spec_res["psd"])
    min_val = np.min(spec_res["psd"])
    val_range = max_val - min_val + 1e-12
    
    for i in range(bins):
        chunk = spec_res["psd"][i*step : (i+1)*step]
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
* **Frequency Standard Deviation**: `{temp_res["freq_std_hz"] / 1e3:.2f} kHz` *(Significant values suggest FSK or FM)*
* **Duty Cycle (Active power ratio)**: `{temp_res["duty_cycle"] * 100:.2f}%`
* **Temporal Classification**: `{"BURSTY (Packetized)" if temp_res["is_bursty"] else "CONTINUOUS (Streaming or Constant FM)"}`
* **Average Active Burst Duration**: `{avg_burst_ms:.3f} ms` (`{temp_res["avg_burst_samples"]:.1f}` samples)
* **Maximum Active Burst Duration**: `{max_burst_ms:.3f} ms` (`{temp_res["max_burst_samples"]:.1f}` samples)

---

## 🧬 Autocorrelation Periodicities (Cyclic Structure)
{lags_str}

---

## 🤖 LLM Analysis Prompt (Copy & Paste below)

Copy and paste this section into the LLM loaded with **SigInt-RF-Expert** instructions:

```text
Please analyze this RF IQ Triage Report and identify the protocol or modulation scheme.

1. Capture Parameters:
   - File: {os.path.basename(file_path)}
   - Sample Rate: {rate / 1e6:.4f} MSPS
   - Assigned Freq: {f"{freq / 1e6:.2f} MHz" if freq is not None else "Unknown"}
   
2. Extracted Features:
   - Occupied Bandwidth (99%): {spec_res["obw_99"] / 1e6:.4f} MHz
   - Peak-to-Median SNR: {spec_res["snr_db"]:.2f} dB
   - OFDM Flatness Score: {spec_res["flatness"]:.3f}
   - Peak-to-Average Power Ratio (PAPR): {temp_res["papr_db"]:.2f} dB
   - Amplitude Variation Coefficient (Std/Mean): {temp_res["amp_std_to_mean"]:.4f}
   - Frequency Deviation (95% Peak): {temp_res["freq_dev_hz"] / 1e3:.2f} kHz
   - Frequency Standard Deviation: {temp_res["freq_std_hz"] / 1e3:.2f} kHz
   - Temporal Pattern: {"BURSTY" if temp_res["is_bursty"] else "CONTINUOUS"}
   - Active Burst Duration: {avg_burst_ms:.3f} ms (Avg), {max_burst_ms:.3f} ms (Max)
   - Auto-correlation peaks: {acf_res["peak_lags"][:3]} samples

Based on the SigInt RF Skill registry:
- What is the most likely protocol or underlying modulation scheme?
- Provide the step-by-step DSP demodulation and decoding procedure (filter bandwidths, sync code details, recovery steps).
- What companion tools or code blocks should I run next to extract telemetry?
```
"""
    with open(output_path, "w") as f:
        f.write(report)
    print(f"Triage report written successfully to: {output_path}")

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
    
    # 3. Compute spectral metrics
    spec_res = analyze_spectrum(samples, sample_rate)
    
    # 4. Compute temporal metrics
    temp_res = analyze_temporal(samples, sample_rate)
    
    # 5. Compute autocorrelation periodicities
    acf_res = analyze_autocorrelation(samples, sample_rate)
    
    # 6. Generate plots if matplotlib is available
    plot_filename = None
    if HAS_MATPLOTLIB and not args.no_plot:
        plot_filename = args.plot
        generate_diagnostic_plots(samples, sample_rate, spec_res, temp_res, acf_res, plot_filename)
        
    # 7. Write markdown output
    write_markdown_report(args.output, args.file, datatype, sample_rate, frequency, spec_res, temp_res, acf_res, plot_filename)

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
