#!/usr/bin/env python3
import os
import sys
import csv
import argparse
import subprocess
import numpy as np

# ---------------------------------------------------------------------------
# SDR Backend Definitions
# ---------------------------------------------------------------------------
SDR_BACKENDS = {
    "usrp": {
        "label": "USRP (Ettus)",
        "sweep_tool": "python_uhd",
        "capture_tool": "python_uhd",
        "install_hint": "brew install uhd or pip install uhd",
        "native_format": "cf32",   # Native float32 complex
    },
    "rtl": {
        "label": "RTL-SDR",
        "sweep_tool": "rtl_power",
        "capture_tool": "rtl_sdr",
        "install_hint": "brew install rtl-sdr (macOS) or sudo apt install rtl-sdr (Debian/Ubuntu)",
        "native_format": "cu8",   # Unsigned 8-bit interleaved I/Q
    },
    "hackrf": {
        "label": "HackRF",
        "sweep_tool": "hackrf_sweep",
        "capture_tool": "hackrf_transfer",
        "install_hint": "brew install hackrf (macOS) or sudo apt install hackrf (Debian/Ubuntu)",
        "native_format": "cs8",   # Signed 8-bit interleaved I/Q
    },
}

# ---------------------------------------------------------------------------
# Argument Parsing
# ---------------------------------------------------------------------------
def parse_args():
    parser = argparse.ArgumentParser(
        description="Automated RF Signal Discovery, Capture, and Triage Pipeline."
    )
    parser.add_argument("--freq", default=None, help="Specific target frequency to capture. Bypasses the wideband sweep.")
    parser.add_argument("--start", default="433M", help="Start frequency for wideband sweep (e.g., 433M, 868M, 118M)")
    parser.add_argument("--stop", default="435M", help="Stop frequency for wideband sweep (e.g., 435M, 870M, 137M)")
    parser.add_argument("--step", default="10k", help="Frequency bin step size for RTL-SDR sweep (e.g., 10k, 25k, 100k). Ignored for HackRF/USRP.")
    parser.add_argument("--bin-width", type=int, default=100000, help="FFT bin width in Hz for HackRF sweep (default: 100000). Ignored for RTL-SDR/USRP.")
    parser.add_argument("--scan-sec", type=int, default=5, help="Duration of wideband sweep in seconds")
    parser.add_argument("--cap-sec", type=float, default=1.0, help="Duration of targeted IQ capture in seconds")
    parser.add_argument("--rate", type=float, default=2.4e6, help="Target sample rate for IQ capture (default: 2.4 MSPS)")
    parser.add_argument("--gain", default="0", help="Receiver gain in dB (default: 0 = AGC for RTL-SDR, 40 for USRP).")
    parser.add_argument("--lna-gain", type=int, default=32, help="HackRF LNA gain in dB (0-40, 8 dB steps, default: 32). Ignored for RTL-SDR/USRP.")
    parser.add_argument("--amp", action="store_true", help="Enable HackRF antenna port power (bias-tee). Ignored for RTL-SDR/USRP.")
    parser.add_argument("--sdr", choices=["rtl", "hackrf", "usrp", "auto"], default="auto",
                        help="SDR backend to use (default: auto-detect based on installed tools)")
    parser.add_argument("--output", "-o", default="capture.cf32", help="Output path for standard complex float32 IQ file")
    return parser.parse_args()

# ---------------------------------------------------------------------------
# Utility Helpers
# ---------------------------------------------------------------------------
def check_utility(name):
    try:
        subprocess.run(["which", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def parse_freq_string(freq_str):
    """Convert frequency strings like '433M', '2.4G', '915M', '100k' to Hz."""
    freq_str = freq_str.strip().upper()
    multipliers = {"K": 1e3, "M": 1e6, "G": 1e9}
    for suffix, mult in multipliers.items():
        if freq_str.endswith(suffix):
            return float(freq_str[:-1]) * mult
    return float(freq_str)

def detect_sdr_backend():
    """Auto-detect which SDR tools are installed. Prefer USRP, then RTL-SDR, then HackRF."""
    try:
        import uhd
        print("🔎 Auto-detected SDR backend: USRP (Ettus)")
        return "usrp"
    except ImportError:
        pass

    for backend_key in ["rtl", "hackrf"]:
        backend = SDR_BACKENDS[backend_key]
        if check_utility(backend["sweep_tool"]) and check_utility(backend["capture_tool"]):
            print(f"🔎 Auto-detected SDR backend: {backend['label']}")
            return backend_key
    return None

def verify_sdr_tools(backend_key):
    """Check that the required tools for the selected backend are installed."""
    if backend_key == "usrp":
        try:
            import uhd
            return
        except ImportError:
            print("❌ Missing required python 'uhd' module for USRP backend.", file=sys.stderr)
            print("   Install: brew install uhd or pip install uhd", file=sys.stderr)
            sys.exit(1)

    backend = SDR_BACKENDS[backend_key]
    missing = []
    for tool_key in ["sweep_tool", "capture_tool"]:
        tool_name = backend[tool_key]
        if not check_utility(tool_name):
            missing.append(tool_name)
    if missing:
        print(f"❌ Missing required {backend['label']} CLI utilities:", file=sys.stderr)
        for tool in missing:
            print(f"   - {tool}", file=sys.stderr)
        print(f"\n   Install: {backend['install_hint']}", file=sys.stderr)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Wideband Sweep
# ---------------------------------------------------------------------------
def run_sweep_rtl(args, temp_csv):
    """Run RTL-SDR wideband power sweep using rtl_power."""
    print(f"🔍 Scanning {args.start} → {args.stop} for {args.scan_sec}s using rtl_power...")
    scan_cmd = [
        "rtl_power",
        "-f", f"{args.start}:{args.stop}:{args.step}",
        "-i", "1s",
        "-e", f"{args.scan_sec}s",
        temp_csv
    ]
    subprocess.run(scan_cmd, check=True)

def run_sweep_hackrf(args, temp_csv):
    """Run HackRF wideband power sweep using hackrf_sweep."""
    start_hz = int(parse_freq_string(args.start))
    stop_hz = int(parse_freq_string(args.stop))
    # hackrf_sweep expects frequencies in MHz
    start_mhz = start_hz // 1000000
    stop_mhz = stop_hz // 1000000 + 1

    print(f"🔍 Scanning {start_mhz} MHz → {stop_mhz} MHz for {args.scan_sec}s using hackrf_sweep...")
    scan_cmd = [
        "hackrf_sweep",
        "-f", f"{start_mhz}:{stop_mhz}",
        "-w", str(args.bin_width),
        "-l", str(args.lna_gain),
        "-g", str(int(args.gain) if args.gain != "0" else 20),
    ]
    if args.amp:
        scan_cmd += ["-a", "1"]

    with open(temp_csv, "w") as f:
        proc = subprocess.Popen(scan_cmd, stdout=f, stderr=subprocess.PIPE)
        try:
            proc.wait(timeout=args.scan_sec)
        except subprocess.TimeoutExpired:
            proc.terminate()
            proc.wait()

def run_sweep_usrp(args, temp_csv):
    """Run USRP wideband power sweep using Python UHD bindings."""
    try:
        import uhd
    except ImportError:
        return
        
    start_hz = parse_freq_string(args.start)
    stop_hz = parse_freq_string(args.stop)
    
    step_hz = args.rate
    num_steps = int(np.ceil((stop_hz - start_hz) / step_hz))
    if num_steps == 0:
        num_steps = 1
        
    print(f"🔍 Scanning {start_hz/1e6:.2f} MHz → {stop_hz/1e6:.2f} MHz using USRP (Python FFTs)...")
    
    usrp = uhd.usrp.MultiUSRP("")
    usrp.set_rx_rate(args.rate)
    try:
        usrp.set_rx_gain(float(args.gain) if args.gain != "0" else 40)
    except ValueError:
        usrp.set_rx_gain(40)
        
    st_args = uhd.usrp.StreamArgs("fc32", "sc16")
    st_args.channels = [0]
    streamer = usrp.get_rx_stream(st_args)
    recv_buffer = np.zeros((1, 10000), dtype=np.complex64)
    metadata = uhd.types.RXMetadata()
    
    with open(temp_csv, "w") as f:
        writer = csv.writer(f)
        for i in range(num_steps):
            center = start_hz + (i * step_hz)
            usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(center))
            
            import time
            time.sleep(0.05) # Allow tuning to settle
            
            num_samps = 10000
            stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.num_done)
            stream_cmd.num_samps = num_samps
            stream_cmd.stream_now = True
            streamer.issue_stream_cmd(stream_cmd)
            
            samples = np.zeros(num_samps, dtype=np.complex64)
            recv_idx = 0
            while recv_idx < num_samps:
                num_rx = streamer.recv(recv_buffer, metadata)
                samples[recv_idx:recv_idx+num_rx] = recv_buffer[0, :num_rx]
                recv_idx += num_rx
                
            fft_size = 1024
            window = np.blackman(fft_size)
            pxx = []
            for j in range(0, len(samples)-fft_size, fft_size):
                chunk = samples[j:j+fft_size] * window
                pxx.append(10 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(chunk)))**2 + 1e-12))
            
            import datetime
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H:%M:%S")
            row = [date_str, time_str, hz_low, hz_high, bin_hz, num_samps] + [str(round(db, 2)) for db in avg_pxx]
            writer.writerow(row)

# ---------------------------------------------------------------------------
# Peak Frequency Detection
# ---------------------------------------------------------------------------
def find_peak_frequency(csv_path):
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        print(f"Error: Wideband scan output {csv_path} is empty or missing.", file=sys.stderr)
        return None
        
    print("📈 Parsing wideband scan results...")
    max_db = -999.0
    peak_freq = None
    
    with open(csv_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 6:
                continue
            try:
                hz_low = float(row[2])
                hz_high = float(row[3])
                hz_step = float(row[4])
                db_vals = [float(x) for x in row[6:] if x.strip()]
                for idx, db in enumerate(db_vals):
                    freq = hz_low + idx * hz_step
                    if db > max_db:
                        max_db = db
                        peak_freq = freq
            except ValueError:
                continue
                
    if peak_freq is None:
        return None
    return peak_freq, max_db

# ---------------------------------------------------------------------------
# IQ Capture
# ---------------------------------------------------------------------------
def run_capture_rtl(args, peak_freq, temp_bin):
    num_samples = int(args.rate * args.cap_sec)
    print(f"🔴 Capturing {args.cap_sec:.2f}s at {peak_freq / 1e6:.4f} MHz ({args.rate/1e6:.1f} MSPS) via rtl_sdr...")
    cap_cmd = [
        "rtl_sdr",
        "-f", str(int(peak_freq)),
        "-s", str(int(args.rate)),
        "-g", args.gain,
        "-n", str(num_samples),
        temp_bin
    ]
    subprocess.run(cap_cmd, check=True)

def run_capture_hackrf(args, peak_freq, temp_bin):
    num_bytes = int(args.rate * args.cap_sec * 2)
    print(f"🔴 Capturing {args.cap_sec:.2f}s at {peak_freq / 1e6:.4f} MHz ({args.rate/1e6:.1f} MSPS) via hackrf_transfer...")
    cap_cmd = [
        "hackrf_transfer",
        "-r", temp_bin,
        "-f", str(int(peak_freq)),
        "-s", str(int(args.rate)),
        "-l", str(args.lna_gain),
        "-g", str(int(args.gain) if args.gain != "0" else 20),
        "-n", str(num_bytes),
    ]
    if args.amp:
        cap_cmd += ["-a", "1"]
    subprocess.run(cap_cmd, check=True)

def run_capture_usrp(args, peak_freq, temp_bin):
    try:
        import uhd
    except ImportError:
        return
        
    num_samples = int(args.rate * args.cap_sec)
    print(f"🔴 Capturing {args.cap_sec:.2f}s at {peak_freq / 1e6:.4f} MHz ({args.rate/1e6:.1f} MSPS) via USRP...")
    
    usrp = uhd.usrp.MultiUSRP("")
    usrp.set_rx_rate(args.rate)
    usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(peak_freq))
    try:
        usrp.set_rx_gain(float(args.gain) if args.gain != "0" else 40)
    except ValueError:
        usrp.set_rx_gain(40)
        
    st_args = uhd.usrp.StreamArgs("fc32", "sc16")
    st_args.channels = [0]
    streamer = usrp.get_rx_stream(st_args)
    
    recv_buffer = np.zeros((1, 10000), dtype=np.complex64)
    metadata = uhd.types.RXMetadata()
    
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.num_done)
    stream_cmd.num_samps = num_samples
    stream_cmd.stream_now = True
    streamer.issue_stream_cmd(stream_cmd)
    
    samples = np.zeros(num_samples, dtype=np.complex64)
    recv_idx = 0
    while recv_idx < num_samples:
        num_rx = streamer.recv(recv_buffer, metadata)
        samples[recv_idx:recv_idx+num_rx] = recv_buffer[0, :num_rx]
        recv_idx += num_rx
        
    samples.tofile(temp_bin)

# ---------------------------------------------------------------------------
# Format Conversion
# ---------------------------------------------------------------------------
def convert_u8_to_cf32(input_path, output_path):
    print("🔧 Converting RTL-SDR cu8 (unsigned 8-bit) → cf32_le (float32 complex)...")
    if not os.path.exists(input_path):
        print(f"Error: Raw capture file {input_path} missing.", file=sys.stderr)
        return False
        
    raw_bytes = np.fromfile(input_path, dtype=np.uint8)
    if len(raw_bytes) % 2 != 0:
        raw_bytes = raw_bytes[:-1]
        
    samples = (raw_bytes.astype(np.float32) - 127.5) / 127.5
    iq = samples[0::2] + 1j * samples[1::2]
    
    iq.astype(np.complex64).tofile(output_path)
    print(f"   Saved {len(iq)} complex samples to: {output_path}")
    return True

def convert_s8_to_cf32(input_path, output_path):
    print("🔧 Converting HackRF cs8 (signed 8-bit) → cf32_le (float32 complex)...")
    if not os.path.exists(input_path):
        print(f"Error: Raw capture file {input_path} missing.", file=sys.stderr)
        return False
        
    raw_bytes = np.fromfile(input_path, dtype=np.int8)
    if len(raw_bytes) % 2 != 0:
        raw_bytes = raw_bytes[:-1]
        
    samples = raw_bytes.astype(np.float32) / 128.0
    iq = samples[0::2] + 1j * samples[1::2]
    
    iq.astype(np.complex64).tofile(output_path)
    print(f"   Saved {len(iq)} complex samples to: {output_path}")
    return True

# ---------------------------------------------------------------------------
# Main Pipeline
# ---------------------------------------------------------------------------
def main():
    args = parse_args()
    
    if args.sdr == "auto":
        backend_key = detect_sdr_backend()
        if backend_key is None:
            print("❌ No supported SDR tools found.", file=sys.stderr)
            print("   Supported backends:", file=sys.stderr)
            for key, info in SDR_BACKENDS.items():
                print(f"   - {info['label']}: {info['sweep_tool']}, {info['capture_tool']}", file=sys.stderr)
                print(f"     Install: {info['install_hint']}", file=sys.stderr)
            sys.exit(1)
    else:
        backend_key = args.sdr
        verify_sdr_tools(backend_key)
    
    backend = SDR_BACKENDS[backend_key]
    print(f"📡 Using SDR backend: {backend['label']}")
    
    temp_csv = "sweep.csv"
    temp_bin = "temp_capture.bin"
    
    if args.freq:
        peak_freq = parse_freq_string(args.freq)
        print(f"🎯 Bypassing wideband sweep. Targeting specified frequency: {peak_freq / 1e6:.4f} MHz")
    else:
        if backend_key == "rtl":
            run_sweep_rtl(args, temp_csv)
        elif backend_key == "hackrf":
            run_sweep_hackrf(args, temp_csv)
        elif backend_key == "usrp":
            run_sweep_usrp(args, temp_csv)
        
        res = find_peak_frequency(temp_csv)
        if not res:
            print("Error: Could not determine peak frequency from scan.", file=sys.stderr)
            sys.exit(1)
            
        peak_freq, max_db = res
        print(f"🎯 Found active signal peak at: {peak_freq / 1e6:.4f} MHz (Power: {max_db:.1f} dB)")
    
    if backend_key == "rtl":
        run_capture_rtl(args, peak_freq, temp_bin)
    elif backend_key == "hackrf":
        run_capture_hackrf(args, peak_freq, temp_bin)
    elif backend_key == "usrp":
        temp_bin = args.output
        run_capture_usrp(args, peak_freq, temp_bin)
    
    if backend["native_format"] == "cu8":
        success = convert_u8_to_cf32(temp_bin, args.output)
    elif backend["native_format"] == "cs8":
        success = convert_s8_to_cf32(temp_bin, args.output)
    elif backend["native_format"] == "cf32":
        success = True
        
    if success:
        print("📊 Running automated triage on the captured IQ signal...")
        triage_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "triage_iq.py")
        if os.path.exists(triage_script):
            triage_cmd = [
                "python3", triage_script,
                "--file", args.output,
                "--rate", str(args.rate),
                "--format", "cf32_le"
            ]
            subprocess.run(triage_cmd, check=True)
        else:
            print(f"Warning: Triage script not found at {triage_script}")
        
    for temp_file in [temp_csv, temp_bin]:
        if temp_file != args.output and os.path.exists(temp_file):
            os.remove(temp_file)
            
if __name__ == "__main__":
    main()
