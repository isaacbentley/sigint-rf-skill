# Triage Hints: Marine VHF Radio 🚢

## 🔍 Key Spectral Indicators
* **Center Frequencies**: 156.000 to 162.025 MHz.
  * Channel 16: 156.800 MHz (Voice)
  * Channel 70: 156.525 MHz (DSC Data)
* **Occupied Bandwidth**: ~12–15 kHz.
* **Modulation**: Narrowband FM (Voice) or AFSK (DSC).

## ⏱ Key Temporal Indicators
* **Burst Duration**: Variable for voice (seconds to minutes). For DSC on Channel 70, the bursts are very short and sharp (~0.5 to 1 second).

## 💡 The Key Identification Heuristic
> **If you are near a coast, lake, or major river, and you see NBFM signals popping up periodically exactly at 156.800 MHz, you have found Marine Channel 16.** To confirm, you will hear a harbor master or coast guard repeating vessel names. If you see short, digital-sounding "braap" bursts on 156.525 MHz, that is the automated DSC system paging radios.

## ❌ Common False Positives and Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Public Safety / Police (NBFM)** | Identical modulation, but public safety is rarely found inside the strict 156.0-162.0 MHz maritime allocation. |
| **Amateur Radio 2m** | Identical modulation, but amateurs are restricted to 144–148 MHz. |
| **AIS (Automatic Identification System)** | Also maritime, but AIS sits strictly at the very top of the band (161.975 and 162.025 MHz) and uses GMSK, not AFSK. |

## ✅ High-Confidence Identification Checklist
- [ ] Frequency falls on a standard ITU marine VHF channel (e.g., 156.800)?
- [ ] Are you near a navigable body of water?
- [ ] Demodulating with NBFM yields human voice discussing maritime topics (bridge, locks, port)?
- [ ] (If on 156.525 MHz) Does the signal sound like a harsh data burst, and does `multimon-ng` decode it as a DSC packet?
