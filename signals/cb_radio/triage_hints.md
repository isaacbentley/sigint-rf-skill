# Triage Hints: Citizens Band (CB) Radio 📻

## 🔍 Key Spectral Indicators
* **Center Frequencies**: 26.965–27.405 MHz (Channels 1 through 40).
* **Occupied Bandwidth**: ~8 kHz for AM.
* **Modulation**: AM. You will see a strong central carrier spike with symmetrical audio sidebands mirroring each other on the waterfall.
* **SSB Modulation**: On higher channels (36-40), you may see asymmetrical blobs of audio with *no* central carrier spike — this is SSB.

## ⏱ Key Temporal Indicators
* **Burst Duration**: Variable (length of a person speaking).
* **Fading (QSB)**: If the signal is arriving via ionospheric skip, its amplitude will slowly rise and fall over a few seconds.

## 💡 The Key Identification Heuristic
> **If you see a strong carrier spike with symmetrical sidebands exactly on 27.185 MHz (Channel 19), and demodulating it as AM reveals truckers discussing traffic, you have found CB radio.** The 10 kHz channel spacing starting at 26.965 MHz is unique to this service.

## ❌ Common False Positives and Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Shortwave Broadcast (AM)** | Shortwave broadcast stations use AM but are located in designated broadcast bands (e.g., 25 MHz, 31 MHz). They are continuous and high-power, whereas CB is sporadic two-way conversation. |
| **RC Toys (27 MHz)** | Cheap RC cars use 27 MHz. They are usually located *between* the CB channels (e.g., 27.145 MHz) and use simple OOK or FSK telemetry, not voice. |
| **Amateur 10-meter Band** | The Ham 10m band is adjacent (28.0–29.7 MHz), but hams strictly use SSB or FM for voice there, rarely AM. |

## ✅ High-Confidence Identification Checklist
- [ ] Frequency is exactly on a standard CB channel (e.g., 27.065, 27.185)?
- [ ] Demodulating with AM (or occasionally SSB/FM) yields human voice?
- [ ] Is the content informal two-way chatter (truckers, off-roaders)?
- [ ] (If RTL-SDR) Are you using Direct Sampling mode to access this low frequency?
