# Signal Specification Template: Motorola iDEN

Use this template to add a new RF signal type to the `signals/` registry. Fill out the fields with maximum detail to allow an LLM or developer to identify and write a decoder for the signal.

---

## 1. Physical Layer Parameters

* **Frequency Band**: 800 MHz, 900 MHz
* **Standard Bandwidth(s)**: 25 kHz
* **Modulation Schema**: M16QAM (often seen as complex 16-QAM in TDMA bursts)
* **Symbol/Chirp Rate**: ~64 kbps (Gross rate)
* **Spectral Characteristics**: 6-slot TDMA cellular trunking system.

---

## 2. Synchronization & Frame Geometry

### Preamble / Sync Pattern
Based heavily on TDMA frame structures. 

### Frame Format
Used by Nextel and SouthernLinc for cellular walkie-talkie operation. Voice encoding evolved from VSELP to AMBE.

---

## 3. Demodulation Pipeline (Step-by-Step)

iDEN is largely a defunct cellular standard and few open-source SDR decoders exist for it due to its complexity and proprietary nature.

---

## 4. LLM Triage Hints (Spectral and Temporal Heuristics)

Provide guidelines to help an LLM analyze metadata:
* **Audio Characteristics**: Rough buzz typical of TDMA bursts.
* **Spectral Shape**: Distinct flat top of 16-QAM within a 25 kHz channel, often accompanied by adjacent channels.
