# Triage Hints: DECT Cordless Telephones 📞

## 🔍 Key Spectral Indicators
* **Center Frequencies**: 1880–1900 MHz (Europe) or 1920–1930 MHz (US "DECT 6.0").
* **Occupied Bandwidth**: ~1.728 MHz.
* **Modulation**: GFSK (rounded edges on the spectrum).

## ⏱ Key Temporal Indicators
* **TDMA Framing**: Distinctive rapid pulsing.
* **Frame Rate**: Exactly 100 Hz (10 ms frame duration).
* **Slot Duration**: Very short bursts, roughly 417 µs.

## 💡 The Key Identification Heuristic
> **If you see a 1.7 MHz wide signal pulsing exactly 100 times per second (10 ms gap) in the 1.9 GHz band, it is a DECT base station.** The base station will always be transmitting at least one "beacon" pulse (the dummy bearer) to keep handsets synchronized, so you will see this pulsing even when no one is on a call.

## ❌ Common False Positives and Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **GSM 1800 / 1900** | GSM is located in adjacent bands (e.g., 1805-1880 MHz downlink) but its channels are much narrower (200 kHz vs DECT's 1.7 MHz). |
| **LTE (4G) 1.4 MHz** | An LTE 1.4 MHz carrier is similar in width, but LTE is an OFDM signal (perfectly rectangular spectrum) and transmits continuously on the downlink, whereas DECT is a TDMA pulse. |
| **Wi-Fi / Bluetooth** | Wi-Fi and Bluetooth operate at 2.4 GHz or 5 GHz, not 1.9 GHz. |

## ✅ High-Confidence Identification Checklist
- [ ] Frequency is in the 1880–1900 MHz or 1920–1930 MHz range?
- [ ] Bandwidth is approximately 1.7 MHz?
- [ ] Signal consists of rapid TDMA pulses?
- [ ] Does the pulse repeat exactly every 10 ms (100 Hz)?
