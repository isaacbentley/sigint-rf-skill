# Signal Specification: Amateur Radio Digital & Legacy Modes 📻

APRS (packet radio), SSTV (slow-scan TV), Morse/CW, RTTY, FT8/WSPR. Common RF CTF challenge signals and amateur radio staples.

---

## 1. APRS — Automatic Packet Reporting System

* **Frequency**: **144.390 MHz** (US), 144.800 MHz (EU), 145.175 MHz (AU)
* **Modulation**: AFSK (Audio FSK) on FM carrier — Bell 202 modem tones
* **Data Rate**: 1200 baud
* **Mark/Space**: 1200 Hz / 2200 Hz
* **Protocol**: AX.25 packet radio
* **Packet**: Source call → Dest call → Digipeater path → Information (position, message, telemetry)
* **Burst**: 200–500 ms packets, event-triggered or periodic (1–30 min beacons)
* **Use**: Real-time position reporting, weather stations, messaging, balloon tracking
* **Tools**: Direwolf (software TNC), YAAC, APRSdroid, multimon-ng

```bash
# Decode APRS from RTL-SDR
rtl_fm -f 144390000 -s 22050 - | direwolf -r 22050 -
```

---

## 2. SSTV — Slow-Scan Television

* **Frequency**: 14.230 MHz (20m SSB), 145.500 MHz (2m FM), various
* **Modulation**: FM subcarrier tones encoding image lines (1200–2300 Hz)
* **Modes**: Martin M1/M2 (most common), Scottie S1/S2, Robot 36/72, PD-120/180
* **Image**: 320×256 (Martin M1), 240×120 (Robot 36)
* **Transmission Time**: 36 seconds (Robot 36) to 3+ minutes (PD-180)
* **Sync**: 1200 Hz sync pulse at start of each line, 1900 Hz black level
* **Protocol**: VIS (Vertical Interval Signaling) header identifies mode — 8-bit code sent as 30ms FSK tones
* **Tools**: MMSSTV, QSSTV, Robot36 (Android), CQ SSTV

```bash
# Decode SSTV from audio
sox capture.wav -r 11025 -c 1 -t raw - | qsstv
```

---

## 3. Morse Code / CW (Continuous Wave)

* **Frequency**: Any HF amateur band (most common: 7.000–7.040, 14.000–14.070 MHz)
* **Modulation**: CW (carrier on/off keying — the original OOK)
* **Speed**: 5–40 WPM (words per minute), typically 12–20 WPM
* **Timing**: Dot = 1 unit, Dash = 3 units, inter-element gap = 1 unit, inter-letter gap = 3 units, inter-word gap = 7 units
* **Bandwidth**: ~100–500 Hz (extremely narrow)
* **Tools**: CW Decoder, fldigi, Morse Expert, Koch trainer
* **RF CTF Note**: Very common challenge type — often hidden in IQ captures as narrow CW signal

---

## 4. RTTY — Radioteletype

* **Frequency**: HF amateur bands (14.080–14.100 MHz, 7.040–7.050 MHz)
* **Modulation**: FSK (170 Hz shift typical)
* **Data Rate**: 45.45 baud (Baudot), 50 baud (amateur)
* **Encoding**: 5-bit Baudot/ITA2 (letters + figures shifts)
* **Bandwidth**: ~250 Hz
* **Tools**: fldigi, MMTTY, MixW

---

## 5. FT8 / FT4 / WSPR — Weak Signal Digital Modes

* **Frequency**: Dedicated subbands on every HF band (e.g., 14.074 MHz for FT8 20m)
* **FT8 Modulation**: 8-GFSK, 6.25 baud, 8 tones spaced 6.25 Hz
* **FT8 Bandwidth**: 50 Hz per signal
* **FT8 Message**: 77 bits (callsign, grid, signal report) + LDPC FEC
* **FT8 Timing**: 15-second transmit/receive cycles, GPS-synchronized
* **WSPR Modulation**: 4-FSK, 1.46 baud, ~6 Hz bandwidth
* **WSPR Timing**: 2-minute transmit cycles
* **Tools**: WSJT-X, JTDX, wsjtx
* **Note**: FT8 is now the most popular HF digital mode worldwide — extremely common on SDR waterfalls

---

## 6. Triage Quick Reference

| Mode | Bandwidth | Key Audio/Visual Signature | RF CTF Frequency |
|---|---|---|---|
| **APRS** | ~12 kHz (FM) | Rapid chirpy modem burst on 2m | 144.39 MHz |
| **SSTV** | 2–3 kHz (SSB) | Slow warbling tones, visible line-by-line on spectrogram | 14.230 MHz |
| **Morse/CW** | 100–500 Hz | Dots and dashes, extremely narrow carrier | Any HF CW subband |
| **RTTY** | ~250 Hz | Two alternating tones (170 Hz apart), distinctive "diddle" | 14.085 MHz |
| **FT8** | 50 Hz/signal | Repeated 15-second tone patterns, many parallel signals | 14.074 MHz |
| **WSPR** | 6 Hz | Ultra-slow 2-minute tones, extremely weak | 14.0956 MHz |
