# Triage Hints: Iridium Satellites 🛰️

## 🔍 Key Spectral Indicators
* **Center Frequencies**: 1616.0 – 1626.5 MHz (L-band)
  * The simplex (paging) channels are clustered near the top, around 1626.27 MHz.
* **Occupied Bandwidth**: ~31.5 kHz per burst.
* **Modulation**: QPSK.

## ⏱ Key Temporal Indicators
* **TDMA Bursts**: The signal consists of very short, sharp bursts (a few milliseconds long).
* **Doppler "Slant"**: On a slow waterfall, the frequency of the bursts will slowly drift downwards over the course of 10 minutes as the LEO satellite passes overhead.

## 💡 The Key Identification Heuristic
> **If you point an L-band patch antenna at the sky and tune to 1626 MHz, you will see a rapid "rain" of short, 31 kHz wide QPSK bursts popping up intermittently.** If you watch for several minutes, the center frequencies of these bursts will slowly drift downward in a curve due to the severe Doppler shift of the fast-moving LEO satellites.

## ❌ Common False Positives and Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Inmarsat** | Inmarsat (also L-band, ~1530-1545 MHz) is a GEO satellite system. Its signals are continuous, do not have Doppler drift, and do not pulse on and off rapidly like Iridium. |
| **GPS / GNSS** | GPS (1575 MHz) is wideband (2 MHz) and below the noise floor. You cannot see it as discrete bursts. |

## ✅ High-Confidence Identification Checklist
- [ ] Frequency is between 1616 and 1626.5 MHz?
- [ ] Signal consists of rapid, short time-domain bursts?
- [ ] Burst bandwidth is approximately 31.5 kHz?
- [ ] Over a period of minutes, does the center frequency of the bursts drift noticeably (Doppler shift)?
- [ ] `gr-iridium` successfully extracts symbols from the file?
