# Triage Hints: Weather Stations (rtl_433) 🌦️

## Spectral Indicators
* **Center Frequency**: 433.92 MHz (EU/Asia), 315 MHz (US Acurite), 868 MHz (EU Bresser/Fine Offset)
* **Occupied Bandwidth**: 10–60 kHz (OOK), 40–100 kHz (FSK)
* **SNR**: Typically 10–25 dB (lower than TPMS due to lower TX power)
* **OFDM Flatness**: < 0.3 (not multi-carrier)

## Temporal Indicators
* **PAPR**: 3–6 dB (OOK variants), < 1.5 dB (FSK variants)
* **Amplitude Std/Mean**: 0.3–0.6 (OOK), < 0.05 (FSK)
* **Duty Cycle**: < 1% — very sparse bursts
* **Burst Duration**: 20–80 ms per packet (longer than TPMS or key fobs)
* **Temporal Pattern**: BURSTY with periodic repetition every 30–60 seconds
* **Burst Clustering**: 2–5 identical packets spaced 1–2 seconds apart

## Autocorrelation Indicators
* **OOK Manchester (2 kBaud)**: Peaks at symbol period = 500 µs → 1200 samples at 2.4 MSPS
* **OOK PWM (1–4 kBaud)**: Peaks at PWM bit period = 250–1000 µs → 600–2400 samples at 2.4 MSPS
* **FSK NRZ (10–17 kBaud)**: Peaks at symbol period = 59–100 µs → 141–240 samples at 2.4 MSPS
* **Important**: For OOK, autocorrelation of amplitude envelope gives symbol clock. For FSK, autocorrelation of FM-demodulated signal gives symbol clock.

## Differentiation from Similar Signals
| Confusable Signal | Key Differentiator |
|---|---|
| **TPMS** | TPMS has higher baud rate (10 kBaud), shorter packets (3–10 ms), specific sync word 0x542C |
| **Car Key Fobs** | Key fobs are event-triggered (not periodic), much shorter packets (5–30 ms), no temperature payload |
| **Doorbells/Remotes** | Remotes have only 12–24 bit payloads, extremely short, no periodic reporting |
| **Garage Door Openers** | No periodic reporting, no environmental data fields |
