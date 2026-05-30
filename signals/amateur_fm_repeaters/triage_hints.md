# Triage Hints: Amateur Radio FM Repeaters 📻

## 🔍 Key Spectral Indicators
* **Center Frequencies**: 144–148 MHz (2m band) or 420–450 MHz (70cm band).
* **Occupied Bandwidth**: ~10 to 15 kHz.
* **Modulation**: Narrowband FM (NBFM).
* **SNR**: Often very high, as repeaters transmit at 50-100 Watts from high elevations.

## ⏱ Key Temporal Indicators
* **Burst Duration**: Variable (length of a person speaking). Usually 5 seconds to 2 minutes.
* **Repeater Tail**: When the human speaker unkeys their radio, the repeater continues transmitting an empty carrier for 1–3 seconds (the "tail").
* **Courtesy Beep**: Often, a short audio beep is heard at the beginning of the repeater tail.
* **Morse ID**: Every ~10 minutes, you will hear a rapid sequence of Morse code (CW) tones identifying the station (e.g., "W1AW").

## 💡 The Key Identification Heuristic
> **If you see a narrowband signal (~12.5 kHz wide) in the 144 MHz or 440 MHz band, and when demodulated as NBFM you hear a human voice followed by a distinct "beep" and a second or two of empty static before the signal drops, you are listening to an amateur radio repeater.** The presence of periodic Morse code IDs is the absolute confirmation.

## ❌ Common False Positives and Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Public Safety / Police (NBFM)** | Police/Fire dispatch also uses NBFM and repeaters. The only difference is the frequency band (e.g., 150-160 MHz, 450-470 MHz) and the content of the speech. Amateurs use callsigns; public safety uses 10-codes. |
| **Marine VHF** | Identical physical layer, but strictly constrained to 156–162 MHz and used for maritime traffic. |
| **Digital Voice (DMR/P25)** | In the waterfall, digital voice looks like a solid, flat-topped rectangle of noise rather than the spiky, undulating spectrum of an analog voice FM signal. |

## ✅ High-Confidence Identification Checklist
- [ ] Frequency is in an amateur band (144-148 MHz or 420-450 MHz)?
- [ ] Bandwidth is narrow (~12.5 kHz)?
- [ ] Demodulating with NBFM yields human voice?
- [ ] Do you hear a "courtesy beep" or a "tail" when the speaker finishes?
- [ ] Do you hear a Morse code identifier every 10 minutes?
- [ ] (Optional) Does an audio spectrum analyzer show a continuous subaudible tone below 300 Hz (CTCSS)?
