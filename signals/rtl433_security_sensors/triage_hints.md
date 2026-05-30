# Triage Hints: Home Security Sensors (rtl_433) 🏠🔒

## Spectral Indicators
* **Center Frequency**: **345 MHz** (Honeywell/2GIG — highly distinctive unique band), 315 MHz (US), 433.92 MHz (EU)
* **Occupied Bandwidth**: 10–50 kHz
* **SNR**: 15–30 dB

## Temporal Indicators
* **PAPR**: 3–6 dB (OOK), < 1.5 dB (Honeywell FSK at 345 MHz)
* **Duty Cycle**: < 0.1%
* **Burst Duration**: 10–40 ms
* **Transmission Pattern**: Mixed — event-triggered alarms + periodic supervisory heartbeats (60–90 min)

## Key Identification Heuristic
> **345 MHz is the smoking gun.** If the center frequency is 345 MHz, it is almost certainly a Honeywell/2GIG/Ademco security sensor. No other common consumer device uses this band.

## Autocorrelation Indicators
* **Honeywell FSK (8 kBaud)**: Peaks at 125 µs = 300 samples at 2.4 MSPS
* **OOK sensors (1–4 kBaud)**: Peaks at 250–1000 µs

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Car Key Fobs** | Key fobs have no periodic supervisory transmissions |
| **Weather Stations** | Weather stations have environmental data payloads (temp, humidity) |
| **TPMS** | TPMS uses specific sync word (0x542C) and has pressure/temp data |
