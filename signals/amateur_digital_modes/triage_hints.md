# Triage Hints: Amateur Radio Digital & Legacy Modes 📻

## Spectral Indicators
* **APRS**: FM carrier at 144.39 MHz with 1200/2200 Hz AFSK tones. ~12 kHz FM BW.
* **SSTV**: SSB audio at 14.230 MHz with slow-sweeping tones 1200–2300 Hz. ~2.5 kHz BW.
* **Morse/CW**: Ultra-narrow carrier (100–500 Hz) with on/off keying at HF CW subbands.
* **RTTY**: Two alternating FSK tones 170 Hz apart. ~250 Hz BW. Continuous "diddle" pattern.
* **FT8**: Dense cluster of parallel 50 Hz signals on waterfall. Exactly 15-second timing cycles.

## RF CTF Challenge Identification
> **If you have an IQ capture and see:** 
> - Very narrow on/off carrier → **Morse/CW** → decode with fldigi
> - Rapid modem burst at 144 MHz → **APRS** → decode with Direwolf
> - Slow warbling tones lasting 30s–3min → **SSTV** → decode with QSSTV
> - Dual alternating tones → **RTTY** → decode with fldigi
> - Dense 15-second tone blocks → **FT8** → decode with WSJT-X

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Weather Station OOK** | Weather stations are at 433 MHz, not VHF amateur bands |
| **Pager (POCSAG)** | POCSAG is FSK at 152/157/929 MHz, not amateur bands |
| **AIS** | AIS is GMSK at 161.975/162.025 MHz, exactly 9600 baud |
