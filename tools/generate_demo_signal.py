#!/usr/bin/env python3
import os
import numpy as np

def generate():
    sample_rate = 2.4e6  # 2.4 MSPS
    symbol_rate = 250e3  # 250 kbaud
    freq_offset = 20e3   # +20 kHz offset
    f_dev = 50e3         # 50 kHz deviation
    num_symbols = 20000  # Longer capture for stable waterfall representation
    
    # Generate bits
    np.random.seed(123)
    bits = np.random.randint(0, 2, num_symbols)
    
    # Generate pulse train
    sps = int(sample_rate / symbol_rate)
    pulse_train = np.repeat(bits * 2 - 1, sps)
    
    # Phase integration
    phase = 2 * np.pi * f_dev * np.cumsum(pulse_train) / sample_rate
    
    # Offset
    t = np.arange(len(phase)) / sample_rate
    phase += 2 * np.pi * freq_offset * t
    
    # IQ
    iq = np.exp(1j * phase)
    
    # Noise
    noise = (np.random.randn(len(iq)) + 1j * np.random.randn(len(iq))) * 0.03
    iq += noise
    
    # Save
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "demo_capture.cf32")
    iq.astype(np.complex64).tofile(out_path)
    print(f"Generated original FSK signal at: {out_path} ({len(iq)} samples)")

if __name__ == "__main__":
    generate()
