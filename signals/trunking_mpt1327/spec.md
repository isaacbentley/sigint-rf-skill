# Signal Specification Template: MPT-1327

Use this template to add a new RF signal type to the `signals/` registry. Fill out the fields with maximum detail to allow an LLM or developer to identify and write a decoder for the signal.

---

## 1. Physical Layer Parameters

* **Frequency Band**: VHF, UHF, 800 MHz
* **Standard Bandwidth(s)**: 12.5 kHz or 25 kHz
* **Modulation Schema**: Fast Frequency Shift Keying (FFSK) Subcarrier Modulation
* **Symbol/Chirp Rate**: 1200 bps
* **Spectral Characteristics**: Dedicated analog control channel. 

---

## 2. Synchronization & Frame Geometry

### Preamble / Sync Pattern
Control channel runs at 1200 bps over an analog FM carrier.

### Frame Format
Voice communication takes place over analog FM traffic channels. Uses various numbering schemes like MPT1343 to organize radios into fleets.

---

## 3. Demodulation Pipeline (Step-by-Step)

Explain the DSP pipeline needed to decode this signal from raw IQ:
1. **FM Demodulation**: Baseband recovery.
2. **Audio FSK Demodulation**: Decode the 1200 bps FFSK subcarrier audio.
3. **Symbol Decision**: Slice into bits to parse MPT-1327 packets.

---

## 4. LLM Triage Hints (Spectral and Temporal Heuristics)

Provide guidelines to help an LLM analyze metadata:
* **Audio Characteristics**: A continuous FSK hum over an analog FM carrier on the control channel, interspersed with analog voice on traffic channels.
* **Recommended Decoders**: SDRTrunk.
