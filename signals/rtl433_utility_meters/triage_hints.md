# Triage Hints: AMR Utility Meters (rtl_433) ⚡💧🔥

## Spectral Indicators
* **Center Frequency**: **902–928 MHz** (highly distinctive — above typical 433/868 bands)
* **Occupied Bandwidth**: 50–200 kHz (wider than most Sub-GHz ISM devices)
* **SNR**: 15–35 dB

## Temporal Indicators
* **PAPR**: 3–6 dB (SCM OOK), < 1.5 dB (IDM FSK)
* **Duty Cycle**: 1–5% (higher than other ISM devices — meters transmit frequently)
* **Burst Duration**: 10–50 ms (SCM), 50–100 ms (IDM — very long packets)
* **Reporting Interval**: 5–30 seconds (very frequent)

## Key Identification Heuristic
> **900 MHz band + high baud rate + Manchester encoding = AMR utility meter.** This combination is highly distinctive and rarely confused with other protocols.

## Autocorrelation Indicators
* **32 kBaud Manchester**: Symbol period = 31.25 µs → 75 samples at 2.4 MSPS
* **Strong sync word correlation**: Look for 0x16A3 sync pattern

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **LoRa** | LoRa uses CSS (chirps), identifiable by spectral sweeps in spectrogram. AMR is flat OOK/FSK. |
| **Wi-Fi** | Wi-Fi is OFDM at 2.4/5 GHz, not Sub-GHz |
| **Weather Stations** | Weather stations are at 433/868 MHz with much lower baud rates (1–4 kBaud) |
