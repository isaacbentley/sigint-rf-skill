# Triage Hints: LTE (Downlink)

## Visual Spectrum Signatures
* **Bandwidth**: Look for strict bandwidth steps: 1.4, 3, 5, 10, 15, or 20 MHz.
* **Shape**: A highly rectangular, flat-top spectrum. 
* **DC Subcarrier**: In LTE Downlink, the DC subcarrier (center frequency) is explicitly left blank (null) to avoid local oscillator leakage issues at the receiver. This is a very strong visual indicator!

## Expected Triage Metrics
* **OFDM Flatness Score**: High (>0.80).
* **PAPR**: ~7-10 dB for Downlink (OFDMA), ~5-7 dB for Uplink (SC-FDMA).
* **Duty Cycle**: Usually continuous (100%) for downlink control channels, even if no user data is present. Uplink is bursty.

## Demodulation Approach
* Use `explainable_demod.py --mode ofdm --ofdm-profile lte` to extract the subcarriers and visualize the scattered Cell Reference Signals (CRS).
* To fully decode LTE system information, specialized tools like `srsLTE` or `OpenLTE` should be recommended to the operator.
