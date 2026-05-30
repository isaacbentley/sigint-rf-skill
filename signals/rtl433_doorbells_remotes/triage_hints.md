# Triage Hints: Doorbells & RF Remotes (rtl_433) 🔔

## Spectral Indicators
* **Center Frequency**: 315 MHz (US) or 433.92 MHz (global)
* **Occupied Bandwidth**: 5–20 kHz (extremely narrow — the tightest in Sub-GHz ISM)
* **SNR**: 15–30 dB

## Temporal Indicators
* **PAPR**: 5–10 dB (strong OOK with long carrier pulses)
* **Amplitude Std/Mean**: > 0.5 (very clear on-off switching)
* **Duty Cycle**: ~0% (event-triggered, not periodic)
* **Burst Duration**: 5–15 ms (shortest bursts in Sub-GHz ISM)
* **Repetitions**: 5–20 rapid identical packets

## Key Identification Heuristic
> **If the OOK packet is only 12–24 bits total and the OBW is < 20 kHz, it's almost certainly a doorbell, outlet switch, or simple RF remote.** These are the simplest and shortest transmissions in the ISM ecosystem.

## Autocorrelation Indicators
* **Very slow symbol rate (1–3 kBaud)**: Long autocorrelation lag peaks at 333–1000 µs → 800–2400 samples at 2.4 MSPS
* **Strong self-similarity**: 5–20 identical packet repeats create very strong autocorrelation at packet-length lag

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Car Key Fobs** | Key fobs have longer packets (28+ bits), sometimes rolling code, more complex encoding |
| **Weather Stations** | Weather stations are periodic, have 40–80 bit payloads with environmental data |
| **TPMS** | TPMS is FSK, periodic, has pressure/temp fields |
| **Security Sensors** | Security sensors have supervisory heartbeats and status flags |
