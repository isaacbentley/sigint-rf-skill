# Triage Hints: Car Key Fobs & Garage Remotes (rtl_433) 🔑

## Spectral Indicators
* **Center Frequency**: 315 MHz (US) or 433.92 MHz (EU/Asia)
* **Occupied Bandwidth**: 10–30 kHz (narrow OOK)
* **SNR**: 15–35 dB (high TX power, short range)

## Temporal Indicators
* **PAPR**: 4–8 dB (strong OOK)
* **Amplitude Std/Mean**: > 0.4 (clear on-off keying)
* **Duty Cycle**: ~0% (event-triggered, not periodic)
* **Burst Duration**: 5–30 ms (shorter than weather stations)
* **Temporal Pattern**: NOT periodic — only transmits on button press
* **Repetitions**: 3–8 rapid-fire identical packets

## Autocorrelation Indicators
* **PWM encoding**: Peaks at PWM bit period (200–1000 µs = 480–2400 samples at 2.4 MSPS)
* **Strong harmonic peaks** from repetitive address bits (PT2262 sends the same code 3–8×)

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Weather Stations** | Weather stations are periodic (30–60s), longer packets, environmental payload |
| **TPMS** | TPMS is FSK (not OOK), periodic, has pressure/temp payload |
| **Doorbells** | Doorbells have only 12–24 bits total, even shorter |
| **Security Sensors** | Security sensors have periodic supervisory heartbeats (60–90 min) |
