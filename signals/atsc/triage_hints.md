# Triage Hints: ATSC 3.0

## Visual Spectrum Signatures
* **Bandwidth**: Will occupy nearly the entire 6 MHz channel cleanly.
* **Shape**: Extremely flat top with very sharp, vertical roll-off edges, characteristic of modern high-density OFDM.
* **No Center Spike**: Unlike older analog TV or 8VSB, there is no distinct carrier spike.

## Expected Triage Metrics
* **OFDM Flatness Score**: High (>0.85).
* **PAPR**: ~8-12 dB (Standard for high-density OFDM without aggressive clipping).
* **Duty Cycle**: 100% (Continuous broadcast).
* **Amplitude Std/Mean**: Usually 0.4 - 0.6 due to the Gaussian-like amplitude distribution of OFDM.

## Demodulation Approach
* Use `explainable_demod.py --mode ofdm --ofdm-profile atsc` to synchronize and visualize the subcarrier constellation and pilot extraction.
