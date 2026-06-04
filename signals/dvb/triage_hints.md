# Triage Hints: DVB-T / DVB-T2

## Visual Spectrum Signatures
* **Bandwidth**: 8 MHz block (in most of the world).
* **Shape**: A highly rectangular, flat-top spectrum. 
* **Notches**: In DVB-T, the edge subcarriers are dropped to prevent adjacent channel interference, giving it slightly softer shoulders than DVB-T2.

## Expected Triage Metrics
* **OFDM Flatness Score**: High (>0.85).
* **PAPR**: ~9-11 dB.
* **Duty Cycle**: 100% (Continuous broadcast).
* **Amplitude Std/Mean**: Usually 0.4 - 0.6 due to the Gaussian-like amplitude distribution of OFDM.

## Demodulation Approach
* Use `explainable_demod.py --mode ofdm --ofdm-profile dvb` to extract the subcarriers and visualize the scattered pilots.
* Note: A 2K FFT actually uses 1705 active subcarriers, and an 8K FFT uses 6817 active subcarriers.
