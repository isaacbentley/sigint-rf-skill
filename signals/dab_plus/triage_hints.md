# Triage Hints: DAB/DAB+ Digital Radio 📻

## 🔍 Key Spectral Indicators
* **Center Frequencies**: VHF Band III (174–240 MHz). Specific blocks (e.g., 216.928 MHz, 222.064 MHz).
* **Occupied Bandwidth**: Exactly 1.536 MHz.
* **Modulation**: OFDM (DQPSK).

## ⏱ Key Temporal Indicators
* **Envelope**: Near continuous, but with a highly distinctive 1.29 ms "Null Symbol" gap every 96 ms.
* **PAPR**: OFDM has a high Peak-to-Average Power Ratio, so the time-domain signal looks "noisy" and lacks the constant envelope of FM.

## 💡 The Key Identification Heuristic
> **If you see a perfectly flat-topped, rectangular block of noise that is exactly 1.5 MHz wide sitting in the 174–240 MHz VHF band, it is almost certainly a DAB/DAB+ ensemble.** If you look at it in the time domain, you will see a tiny drop in power (the Null Symbol) occurring almost exactly 10 times per second (every 96 ms).

## ❌ Common False Positives and Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **DVB-T (Digital TV)** | DVB-T is also an OFDM block in the VHF/UHF bands, but it is much wider — 6 MHz, 7 MHz, or 8 MHz wide, compared to DAB's 1.5 MHz. |
| **LTE (4G) 1.4 MHz** | Some LTE deployments use 1.4 MHz bandwidths, which are similar in width to DAB. However, LTE is rarely found in the 174–240 MHz band, and LTE framing does not have a 96 ms Null Symbol pattern. |

## ✅ High-Confidence Identification Checklist
- [ ] Frequency is in VHF Band III (174–240 MHz)?
- [ ] Signal is an OFDM block with a flat top and sharp roll-off edges?
- [ ] Signal bandwidth is 1.536 MHz?
- [ ] (Optional) In a time-domain or high-resolution waterfall view, can you see the 1.29 ms Null Symbol gaps every 96 ms?
- [ ] Welle.io or qt-dab can lock onto the ensemble?
