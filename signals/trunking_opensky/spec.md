# Signal Specification Template: Harris OpenSky

Use this template to add a new RF signal type to the `signals/` registry. Fill out the fields with maximum detail to allow an LLM or developer to identify and write a decoder for the signal.

---

## 1. Physical Layer Parameters

* **Frequency Band**: 800 MHz, 900 MHz
* **Standard Bandwidth(s)**: 25 kHz
* **Modulation Schema**: FSK/GMSK (TDMA)
* **Symbol/Chirp Rate**: 19.2 kbps
* **Spectral Characteristics**: 4-slot or 2-slot TDMA. Uses AMBE vocoder.

---

## 2. Synchronization & Frame Geometry

### Preamble / Sync Pattern
Continuous TDMA data stream. OpenSky sends voice and control traffic over the same stream (IP network-based trunking).

---

## 3. Demodulation Pipeline (Step-by-Step)

OpenSky is heavily encrypted and uses a proprietary format. No open source SDR software is currently capable of decrypting or monitoring OpenSky.

---

## 4. LLM Triage Hints (Spectral and Temporal Heuristics)

Provide guidelines to help an LLM analyze metadata:
* **Audio Characteristics**: A harsh buzz, typical of 4-slot TDMA formats.
* **Temporal duration**: Continuous data stream.
* **Important Note**: Phased out in many states (like PA) in favor of P25 Phase II.
