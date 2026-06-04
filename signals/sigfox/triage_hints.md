# Triage Hints: Sigfox (Ultra-Narrowband LPWAN) 📡

## Spectral Indicators
* **Center Frequency**: 868.034–868.226 MHz (EU) or 902–905 MHz (US)
* **Channel Bandwidth**: **100 Hz** — by far the narrowest digital signal you'll encounter
* **Macro-channel**: ~192 kHz (EU), ~2.7 MHz (US) — many 100 Hz channels scattered within
* **Modulation**: DBPSK — constant envelope, very slight spectral line

## The Key Identification Heuristic
> **If you see an absurdly narrow (~100 Hz) spectral line popping up randomly within the 868 MHz ISM band, lasting 1–2 seconds, then disappearing and reappearing on a different frequency — that's Sigfox.** Nothing else is this narrow. It looks like "almost nothing" on a wideband waterfall — easily mistaken for noise or a spurious carrier.

## Temporal Indicators
* **Burst Duration**: 0.86–2.08 seconds (at 100 bps)
* **Repetition**: Each message sent **3 times** on **3 different frequencies** (RFTDMA)
* **Inter-burst gap**: Random 0–30 seconds between repetitions
* **Pattern**: You'll see 3 thin spectral lines appear within ~60 seconds, each at a different frequency within the macro-channel

## How to Spot on a Waterfall / Spectrogram
1. Capture the full 868 MHz ISM band (~192 kHz BW) with high FFT resolution (≥2048 points)
2. Look for **extremely thin vertical lines** (100 Hz wide) lasting 1–2 seconds
3. They appear at random frequencies and random times
4. Groups of 3 (same message, 3 retransmissions) within ~60 seconds
5. Use Inspectrum or SigDigger for high-resolution narrowband analysis

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **LoRa** | LoRa is 125–500 kHz wide with chirp sweeps — 1000× wider than Sigfox |
| **Z-Wave** | Z-Wave is FSK at ~200 kHz BW on 868.42 MHz — much wider |
| **SRD devices (door sensors etc.)** | SRD are OOK/FSK at 10–60 kHz BW — 100× wider |
| **Noise / spurious carriers** | Noise doesn't repeat 3× with DBPSK modulation; spurious carriers are continuous |
| **Narrowband amateur (CW Morse)** | CW Morse is on amateur bands (not 868 MHz) and has keying pattern |

## Confidence Checklist
- [ ] Frequency within 868.034–868.226 MHz (EU) or 902–905 MHz (US)?
- [ ] Spectral width ≈ 100 Hz (EU) or ≈ 600 Hz (US)?
- [ ] Burst duration 0.8–2.1 seconds?
- [ ] Three transmissions within ~60 seconds at different frequencies?
- [ ] Constant envelope (DBPSK — no amplitude variation)?
- [ ] No response transmission immediately after (uplink-only is most common)?
