# Triage Hints: Wi-Fi (IEEE 802.11a/g/n/ac/ax/be) 📶

## Spectral Indicators
* **Center Frequency**: 2.4 GHz (ch 1/6/11 centered at 2412/2437/2462 MHz), 5 GHz (U-NII), or 6 GHz (Wi-Fi 6E/7)
* **Occupied Bandwidth**: **20 MHz** base, bonded to 40 / 80 / 160 MHz (320 MHz in 802.11be) — the widest common ISM emitter
* **PSD shape**: **flat-topped OFDM block** with steep shoulders; high spectral flatness (`flatness > 0.70`)
* **Subcarrier spacing**: 312.5 kHz (a/g/n/ac) — a fine comb under high-res FFT

## Key Identification Heuristic
> **At 2.4 GHz, bandwidth tells you what it is:**
> - **1–2 MHz** = Bluetooth / BLE (GFSK)
> - **2 MHz** = Zigbee (O-QPSK/DSSS)
> - **10 MHz** = DJI OcuSync (OFDM + Zadoff-Chu)
> - **20 MHz+** = **Wi-Fi** (flat-top OFDM)
>
> A wide, flat-topped block that appears in **bursts** with a **beacon every ~102 ms** is Wi-Fi.

## Temporal Indicators
* **Bursty**: frames are short and variable; duty cycle depends on traffic (idle networks are mostly beacons)
* **Beacon periodicity**: ~**102.4 ms** (100 TU) broadcasts — a strong periodic marker on a waterfall
* **PAPR**: **high (6–12 dB)** — characteristic of multi-carrier OFDM (unlike constant-envelope BLE/Zigbee)
* **Autocorrelation**: L-STF peak at **0.8 µs**, L-LTF peak at **3.2 µs** (16 / 64 samples @ 20 MSPS)

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Bluetooth / BLE** | 1–2 MHz GFSK, constant-envelope (low PAPR); Wi-Fi is 20 MHz+ OFDM (high PAPR) |
| **Zigbee (802.15.4)** | 2 MHz O-QPSK/DSSS; far narrower than a 20 MHz Wi-Fi channel |
| **DJI OcuSync** | 10–40 MHz OFDM but carries a dual Zadoff-Chu preamble (roots 600 & 147); Wi-Fi uses L-STF/L-LTF |
| **LTE / 5G** | Also OFDM/flat-top, but licensed bands (700 MHz–2.6 GHz), continuous downlink with PSS/SSS — not ISM bursts |
| **Drone Remote ID (Wi-Fi variant)** | *Is* Wi-Fi PHY — identify via the OUI/beacon vendor IE (ASTM F3411), not the waveform |
| **Microwave oven** | Broadband incoherent interference sweeping across 2.45 GHz — no OFDM structure or beacons |
