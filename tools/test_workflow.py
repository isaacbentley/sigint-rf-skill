#!/usr/bin/env python3
import os
import sys
import numpy as np
import subprocess

def run_cmd(cmd, description):
    print(f"\n🚀 Running: {' '.join(cmd)}")
    print(f"   Purpose: {description}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error: Command failed with code {res.returncode}", file=sys.stderr)
        print(res.stderr, file=sys.stderr)
        sys.exit(1)
    print("   Output Summary:")
    lines = res.stdout.strip().split("\n")
    for line in lines[:20]: # Print first 20 lines
        print(f"     {line}")
    if len(lines) > 20:
        print(f"     ... ({len(lines) - 20} more lines)")
    return res.stdout

def main():
    print("=== Start SigInt RF Skill Workflow Verification ===")
    
    # 1. Synthesize FSK Baseband Signal
    # Params
    sample_rate = 2.0e6  # 2 MSPS
    symbol_rate = 250e3   # 250 kbaud (8 samples per symbol)
    freq_offset = 15e3   # +15 kHz tuning error
    f_dev = 50e3         # 50 kHz deviation
    num_symbols = 500
    
    print(f"\n1. Synthesizing FSK Signal...")
    print(f"   Rate: {sample_rate/1e6} MSPS | Symbols: {num_symbols} | Baud: {symbol_rate/1e3}k | Offset: {freq_offset/1e3} kHz")
    
    # Generate random bits
    np.random.seed(42)
    bits = np.random.randint(0, 2, num_symbols)
    
    # Repeat bits to create sample-level pulse train
    sps = int(sample_rate / symbol_rate)
    pulse_train = np.repeat(bits * 2 - 1, sps) # map 0/1 to -1/+1
    
    # Integrate to get phase (continuous phase FSK)
    phase = 2 * np.pi * f_dev * np.cumsum(pulse_train) / sample_rate
    
    # Add manual frequency offset
    t = np.arange(len(phase)) / sample_rate
    phase += 2 * np.pi * freq_offset * t
    
    # Generate complex IQ
    iq = np.exp(1j * phase)
    
    # Add minor AWGN noise
    noise = (np.random.randn(len(iq)) + 1j * np.random.randn(len(iq))) * 0.05
    iq += noise
    
    # Save raw IQ file (.cf32)
    iq_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthetic_fsk.cf32")
    iq.astype(np.complex64).tofile(iq_filepath)
    print(f"   Synthetic FSK IQ file saved to: {iq_filepath} ({os.path.getsize(iq_filepath)} bytes)")
    
    # 2. Run Triage Script
    triage_report = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_triage_report.md")
    triage_plot = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_triage_plot.png")
    
    cmd_triage = [
        sys.executable,
        "tools/triage_iq.py",
        "--file", iq_filepath,
        "--rate", str(sample_rate),
        "--format", "cf32_le",
        "--output", triage_report,
        "--plot", triage_plot
    ]
    run_cmd(cmd_triage, "Perform triage spectral/temporal analysis and generate plots.")
    
    # Verify outputs exist
    if os.path.exists(triage_report) and os.path.getsize(triage_report) > 0:
        print(f"   ✅ Triage report generated successfully: {triage_report}")
    else:
        print("   ❌ Triage report was not created or is empty.")
        sys.exit(1)
        
    if os.path.exists(triage_plot) and os.path.getsize(triage_plot) > 0:
        print(f"   ✅ Triage plot generated successfully: {triage_plot}")
    else:
        print("   ❌ Triage plot was not created or is empty.")
        sys.exit(1)
        
    # 3. Run Explainable Demodulator with target parameters
    demod_plot = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_demod_diagnostics.png")
    cmd_demod = [
        sys.executable,
        "tools/explainable_demod.py",
        "--file", iq_filepath,
        "--rate", str(sample_rate),
        "--mode", "fsk",
        "--symbol-rate", "250000",
        "--offset-hz", "15000",
        "--plot-path", demod_plot,
        "--verbose"
    ]
    stdout_demod = run_cmd(cmd_demod, "Demodulate the FSK signal using step-by-step explainable DSP.")
    
    # Check if bits match original
    # We parse the output line that contains "First 128 Bits:"
    lines = stdout_demod.split("\n")
    demod_bits_str = None
    for idx, line in enumerate(lines):
        if "First 128 Bits:" in line and idx + 1 < len(lines):
            demod_bits_str = lines[idx+1].strip().strip("[] ")
            break
            
    if demod_bits_str:
        orig_bits_str = "".join(map(str, bits[:128]))
        print(f"\n🔍 Comparing Demodulated Bits with Original:")
        print(f"   Original:  {orig_bits_str}")
        print(f"   Demodulated:{demod_bits_str}")
        
        # Calculate bit error rate
        errs = sum(c1 != c2 for c1, c2 in zip(orig_bits_str, demod_bits_str))
        print(f"   Bit Errors in first 128 symbols: {errs} / 128 (BER: {errs/128:.2%})")
        if errs == 0:
            print("   ✅ Perfect demodulation achieved!")
        else:
            print("   ⚠️ Some bit errors occurred. Check noise level or clock sampling phase.")
            
    if os.path.exists(demod_plot) and os.path.getsize(demod_plot) > 0:
        print(f"   ✅ Demodulator diagnostics plot created: {demod_plot}")
    else:
        print("   ❌ Demodulator diagnostics plot is missing.")
        sys.exit(1)
        
    # Clean up FSK test files
    for filepath in [iq_filepath, triage_report, triage_plot, demod_plot]:
        if os.path.exists(filepath):
            os.remove(filepath)

    # =========================================================================
    # OOK Test Case
    # =========================================================================
    print("\n" + "=" * 60)
    print("=== OOK (On-Off Keying) Test Case ===")
    print("=" * 60)

    # 1. Synthesize OOK signal
    print(f"\n1. Synthesizing OOK Signal...")
    print(f"   Rate: 2.0 MSPS | Symbols: 200 | Baud: 1.0k | Carrier: 50 kHz")

    np.random.seed(99)
    bits_ook = np.random.randint(0, 2, 200)
    sps_ook = int(2e6 / 1000)  # 2000 samples per symbol
    pulse_ook = np.repeat(bits_ook.astype(np.float32), sps_ook)
    # OOK: carrier when bit=1, near-zero when bit=0
    carrier = np.exp(1j * 2 * np.pi * 50e3 * np.arange(len(pulse_ook)) / 2e6)  # 50 kHz carrier
    iq_ook = pulse_ook * carrier
    # Add noise
    noise_ook = (np.random.randn(len(iq_ook)) + 1j * np.random.randn(len(iq_ook))) * 0.02
    iq_ook += noise_ook

    # Save raw IQ file
    ook_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthetic_ook.cf32")
    iq_ook.astype(np.complex64).tofile(ook_filepath)
    print(f"   Synthetic OOK IQ file saved to: {ook_filepath} ({os.path.getsize(ook_filepath)} bytes)")

    # 2. Run Triage Script on OOK
    ook_triage_report = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_ook_triage_report.md")
    ook_triage_plot = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_ook_triage_plot.png")

    cmd_ook_triage = [
        sys.executable,
        "tools/triage_iq.py",
        "--file", ook_filepath,
        "--rate", str(2.0e6),
        "--format", "cf32_le",
        "--output", ook_triage_report,
        "--plot", ook_triage_plot
    ]
    run_cmd(cmd_ook_triage, "Triage OOK signal for spectral/temporal analysis.")

    if os.path.exists(ook_triage_report) and os.path.getsize(ook_triage_report) > 0:
        print(f"   ✅ OOK triage report generated successfully: {ook_triage_report}")
    else:
        print("   ❌ OOK triage report was not created or is empty.")
        sys.exit(1)

    if os.path.exists(ook_triage_plot) and os.path.getsize(ook_triage_plot) > 0:
        print(f"   ✅ OOK triage plot generated successfully: {ook_triage_plot}")
    else:
        print("   ❌ OOK triage plot was not created or is empty.")
        sys.exit(1)

    # 3. Run Explainable Demodulator with OOK mode
    ook_demod_plot = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_ook_demod_diagnostics.png")
    cmd_ook_demod = [
        sys.executable,
        "tools/explainable_demod.py",
        "--file", ook_filepath,
        "--rate", str(2.0e6),
        "--mode", "ook",
        "--plot-path", ook_demod_plot,
        "--verbose"
    ]
    run_cmd(cmd_ook_demod, "Demodulate the OOK signal using amplitude envelope detection.")

    if os.path.exists(ook_demod_plot) and os.path.getsize(ook_demod_plot) > 0:
        print(f"   ✅ OOK demodulator diagnostics plot created: {ook_demod_plot}")
    else:
        print("   ❌ OOK demodulator diagnostics plot is missing.")
        sys.exit(1)

    # Clean up OOK test files
    for filepath in [ook_filepath, ook_triage_report, ook_triage_plot, ook_demod_plot]:
        if os.path.exists(filepath):
            os.remove(filepath)

    # =========================================================================
    # TPMS (Bursty FSK) Test Case
    # =========================================================================
    print("\n" + "=" * 60)
    print("=== TPMS (Bursty FSK) Test Case ===")
    print("=" * 60)

    # 1. Synthesize TPMS bursty FSK signal (inline, matching generate_tpms_signal.py)
    tpms_sample_rate = 2.4e6   # 2.4 MSPS
    tpms_symbol_rate = 10e3    # 10 kBaud
    tpms_freq_offset = 50e3    # +50 kHz offset
    tpms_f_dev = 35e3          # 35 kHz FSK deviation

    print(f"\n1. Synthesizing TPMS Bursty FSK Signal...")
    print(f"   Rate: {tpms_sample_rate/1e6} MSPS | Baud: {tpms_symbol_rate/1e3}k | Offset: {tpms_freq_offset/1e3} kHz | Dev: {tpms_f_dev/1e3} kHz")

    # Standard TPMS packet: Preamble + Sync Word (0x542C) + Payload
    preamble = [0, 1] * 20
    sync = [0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0]
    # Payload bytes: ID=0x8C3F1A, Press=0x20, Temp=0x14, CRC=0x9A
    payload_bits = []
    for byte_val in [0x8C, 0x3F, 0x1A, 0x20, 0x14, 0x9A]:
        payload_bits.extend([int(x) for x in f"{byte_val:08b}"])

    tpms_bits = np.array(preamble + sync + payload_bits)
    print(f"   Packet: {len(preamble)} preamble + {len(sync)} sync + {len(payload_bits)} payload = {len(tpms_bits)} symbols")

    # Generate pulse train
    tpms_sps = int(tpms_sample_rate / tpms_symbol_rate)
    tpms_pulse = np.repeat(tpms_bits * 2 - 1, tpms_sps)

    # Zero-pad before and after the burst to simulate real bursty packet
    # Use generous padding so burst is ~20% of total capture, ensuring bursty detection
    pad_len = 25000
    tpms_pulse_padded = np.concatenate([np.zeros(pad_len), tpms_pulse, np.zeros(pad_len)])

    # Create burst envelope (1 during signal, 0 during padding)
    burst_envelope = np.concatenate([np.zeros(pad_len), np.ones(len(tpms_pulse)), np.zeros(pad_len)])

    # Phase integration for FSK
    tpms_phase = 2 * np.pi * tpms_f_dev * np.cumsum(tpms_pulse_padded) / tpms_sample_rate

    # Frequency offset modulation
    tpms_t = np.arange(len(tpms_phase)) / tpms_sample_rate
    tpms_phase += 2 * np.pi * tpms_freq_offset * tpms_t

    # Generate complex IQ and apply burst envelope so padding regions are noise-only
    iq_tpms = burst_envelope * np.exp(1j * tpms_phase)

    # Add noise
    np.random.seed(77)
    noise_tpms = (np.random.randn(len(iq_tpms)) + 1j * np.random.randn(len(iq_tpms))) * 0.05
    iq_tpms += noise_tpms

    # Save raw IQ file
    tpms_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthetic_tpms.cf32")
    iq_tpms.astype(np.complex64).tofile(tpms_filepath)
    print(f"   Synthetic TPMS IQ file saved to: {tpms_filepath} ({os.path.getsize(tpms_filepath)} bytes)")

    # 2. Run Triage Script on TPMS
    tpms_triage_report = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_tpms_triage_report.md")
    tpms_triage_plot = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_tpms_triage_plot.png")

    cmd_tpms_triage = [
        sys.executable,
        "tools/triage_iq.py",
        "--file", tpms_filepath,
        "--rate", str(tpms_sample_rate),
        "--format", "cf32_le",
        "--output", tpms_triage_report,
        "--plot", tpms_triage_plot
    ]
    run_cmd(cmd_tpms_triage, "Triage TPMS bursty FSK signal for spectral/temporal analysis.")

    if os.path.exists(tpms_triage_report) and os.path.getsize(tpms_triage_report) > 0:
        print(f"   ✅ TPMS triage report generated successfully: {tpms_triage_report}")
    else:
        print("   ❌ TPMS triage report was not created or is empty.")
        sys.exit(1)

    # Verify that BURSTY classification appears in the triage report
    with open(tpms_triage_report, "r") as f:
        tpms_report_content = f.read()
    if "BURSTY" in tpms_report_content:
        print(f"   ✅ TPMS triage report correctly identifies signal as BURSTY")
    else:
        print("   ❌ TPMS triage report did not classify signal as BURSTY — expected bursty detection.")
        sys.exit(1)

    if os.path.exists(tpms_triage_plot) and os.path.getsize(tpms_triage_plot) > 0:
        print(f"   ✅ TPMS triage plot generated successfully: {tpms_triage_plot}")
    else:
        print("   ❌ TPMS triage plot was not created or is empty.")
        sys.exit(1)

    # 3. Run Explainable Demodulator with FSK mode and TPMS parameters
    tpms_demod_plot = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_tpms_demod_diagnostics.png")
    cmd_tpms_demod = [
        sys.executable,
        "tools/explainable_demod.py",
        "--file", tpms_filepath,
        "--rate", str(tpms_sample_rate),
        "--mode", "fsk",
        "--symbol-rate", "10000",
        "--offset-hz", "50000",
        "--plot-path", tpms_demod_plot,
        "--verbose"
    ]
    run_cmd(cmd_tpms_demod, "Demodulate the TPMS bursty FSK signal.")

    if os.path.exists(tpms_demod_plot) and os.path.getsize(tpms_demod_plot) > 0:
        print(f"   ✅ TPMS demodulator diagnostics plot created: {tpms_demod_plot}")
    else:
        print("   ❌ TPMS demodulator diagnostics plot is missing.")
        sys.exit(1)

    # Clean up TPMS test files
    for filepath in [tpms_filepath, tpms_triage_report, tpms_triage_plot, tpms_demod_plot]:
        if os.path.exists(filepath):
            os.remove(filepath)

    print("\n=== All workflow tests (FSK + OOK + TPMS) passed successfully! ===")

if __name__ == "__main__":
    main()
