# Triage Hints: UHF RFID — EPC Gen2 (860–960 MHz) 🏷️📦

## Spectral Indicators
* **Center Frequency**: 902–928 MHz (US), 865–868 MHz (EU) — **same band as LoRa and AMR utility meters**
* **Occupied Bandwidth**: 200–500 kHz per channel
* **SNR**: Reader downlink is strong (15–30 dB); tag backscatter is very weak (0–10 dB)
* **Channel hopping**: Reader hops across 50 channels in 902–928 MHz every 400 ms (FCC FHSS requirement)

## Temporal Indicators
* **PAPR**: 3–6 dB (ASK modulation with PIE encoding)
* **Duty Cycle**: High — reader may transmit near-continuously during inventory
* **Burst Pattern**: Alternating reader commands (strong) and tag backscatter (weak) — asymmetric power levels are the smoking gun

## Key Identification Heuristic
> **If you see strong ASK bursts at 902–928 MHz followed immediately by very weak backscatter responses, it's UHF RFID.** The dramatic power asymmetry between reader and tag is unique. LoRa and AMR meters are symmetric (one transmitter).

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **LoRa** | LoRa uses CSS chirps (spectral sweeps), not ASK. No backscatter. |
| **AMR Utility Meters** | AMR uses Manchester-encoded OOK/FSK at fixed power. No backscatter. |
| **Wi-Fi** | Wi-Fi is OFDM at 2.4/5 GHz, completely different band and modulation |
| **EU SRD (868 MHz)** | SRD is typically lower power, simpler modulation, no reader-tag asymmetry |
