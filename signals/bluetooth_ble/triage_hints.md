# Triage Hints: Bluetooth Classic & BLE (2.4 GHz) 📶

## Spectral Indicators
* **Center Frequency**: 2.402–2.480 GHz (ISM band — shared with Wi-Fi, Zigbee, DJI)
* **Channel Bandwidth**: 1 MHz (Classic) or 2 MHz (BLE) — **much narrower than Wi-Fi (20 MHz)**
* **BLE Advertising Channels**: Fixed at 2402, 2426, 2480 MHz (channels 37, 38, 39)

## Key Identification Heuristic
> **At 2.4 GHz, the bandwidth tells you what it is:**
> - **1–2 MHz** = Bluetooth / BLE
> - **2 MHz** = Zigbee (802.15.4)
> - **10 MHz** = DJI OcuSync
> - **20 MHz** = Wi-Fi

## Temporal Indicators
* **BLE Advertising**: Short bursts (200–400 µs) on 3 fixed channels, repeated every 20 ms–10.24 s
* **Classic**: 625 µs time slots, rapid frequency hopping (1600 hops/sec) — appears as wideband noise on SDR
* **PAPR**: < 2 dB (GFSK is constant-envelope)

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Wi-Fi** | Wi-Fi is OFDM with 20+ MHz bandwidth, BLE is GFSK with 1–2 MHz |
| **Zigbee** | Zigbee is O-QPSK with DSSS, BLE is GFSK. Both ~2 MHz but different modulation shape |
| **DJI OcuSync** | DJI is 10–40 MHz wide OFDM with Zadoff-Chu preamble |
| **Microwave oven** | Broadband wideband interference, not coherent modulation |
