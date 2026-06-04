# Signal Specification Template: Logic Trunked Radio (LTR)

Use this template to add a new RF signal type to the `signals/` registry. Fill out the fields with maximum detail to allow an LLM or developer to identify and write a decoder for the signal.

---

## 1. Physical Layer Parameters

* **Frequency Band**: UHF, 800 MHz, 900 MHz
* **Standard Bandwidth(s)**: 12.5 kHz / 25 kHz
* **Modulation Schema**: Subaudible FSK alongside Analog FM Voice
* **Symbol/Chirp Rate**: 300 bps (Standard LTR)
* **Spectral Characteristics**: No dedicated control channel. Data is transmitted simultaneously with voice.

---

## 2. Synchronization & Frame Geometry

### Preamble / Sync Pattern
Idle data bursts (often every 10 seconds) on standard systems to let subscriber units know the system is active. Sounds like a short blip of static.

### Frame Format
Subaudible data stream contains Area, Home Repeater, Group, and Free Repeater info.

---

## 3. Demodulation Pipeline (Step-by-Step)

Explain the DSP pipeline needed to decode this signal from raw IQ:
1. **FM Demodulation**: Extract audio baseband.
2. **Low-Pass Filter**: Isolate the subaudible 300 baud FSK signaling from the voice audio.
3. **Symbol Slicing & Parsing**: Extract the LTR frames.

---

## 4. LLM Triage Hints (Spectral and Temporal Heuristics)

Provide guidelines to help an LLM analyze metadata:
* **Audio Characteristics**: Regular analog FM voice but with low-frequency rumble or short 10-second data bursts when idle.
* **Recommended Decoders**: SDRTrunk.
