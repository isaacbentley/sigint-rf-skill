# Triage Hints: GSM 2G Cellular 📱

## 🔍 Key Spectral Indicators
* **Center Frequencies**: 850, 900, 1800, 1900 MHz cellular bands.
* **Occupied Bandwidth**: Exactly 200 kHz per channel (ARFCN).
* **Modulation**: GMSK — has a rounded, bell-like spectral shape typical of Gaussian filtering.

## ⏱ Key Temporal Indicators
* **TDMA Framing**: If you look at an amplitude envelope or waterfall, you will see rapid pulsing. Each pulse (time slot) is 0.577 ms long.
* **Duty Cycle**: A "beacon" channel (carrying BCCH) transmits continuously on all 8 time slots, so it looks like a continuous 200 kHz block. Traffic channels only transmit on active time slots, resulting in a dashed or dotted appearance on the waterfall.
* **FCCH Tone**: The Frequency Correction Channel appears as a sharp, pure CW (sine wave) tone offset exactly +67.7 kHz from the center frequency of the 200 kHz channel. It pulses periodically.

## 💡 The Key Identification Heuristic
> **If you see a 200 kHz wide, rounded signal in the 900 MHz or 1800 MHz band, and upon closer inspection of the waterfall you see a sharp, intermittent pure tone at +67.7 kHz offset (the FCCH), you have found a GSM base station beacon.** The TDMA framing (0.577 ms slots) is also a dead giveaway if viewed in a fast time-domain plot.

## ❌ Common False Positives and Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **LTE / 4G / 5G** | LTE signals are much wider (1.4, 3, 5, 10, 15, 20 MHz), use OFDM (perfectly flat top, sharp edges), and do not have the 200 kHz GMSK structure or FCCH tones. |
| **TETRA** | TETRA is much narrower (25 kHz), uses $\pi/4$-DQPSK, and is found in PMR bands (e.g., 380–430 MHz), not cellular bands. |
| **DMR / P25** | DMR is even narrower (12.5 kHz) and uses 4FSK. |

## ✅ High-Confidence Identification Checklist
- [ ] Frequency is in a known GSM band (e.g., 900/1800 MHz)?
- [ ] Signal bandwidth is 200 kHz?
- [ ] Modulation shape is rounded (GMSK)?
- [ ] Can you spot the intermittent FCCH tone at +67.7 kHz?
- [ ] Do `kalibrate-rtl` or `grgsm_livemon` successfully lock onto it?
