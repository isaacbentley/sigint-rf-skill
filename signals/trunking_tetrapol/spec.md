# Signal Specification Template: TETRAPOL

Use this template to add a new RF signal type to the `signals/` registry. Fill out the fields with maximum detail to allow an LLM or developer to identify and write a decoder for the signal.

---

## 1. Physical Layer Parameters

* **Frequency Band**: 370–400 MHz (typically in Europe)
* **Standard Bandwidth(s)**: 10 kHz or 12.5 kHz
* **Modulation Schema**: GMSK
* **Symbol/Chirp Rate**: 8000 Baud
* **Spectral Characteristics**: FDMA narrowband system (unlike TETRA which is TDMA).

---

## 2. Synchronization & Frame Geometry

### Preamble / Sync Pattern
Autocorrelation Function (ACF) peak typically seen at 20.069 ms.

### Frame Format
Raw data rate of 8000 bps. 

---

## 3. Demodulation Pipeline (Step-by-Step)

TETRAPOL uses undocumented voice codecs and strong end-to-end encryption. There are no known open-source decoders capable of providing clear voice output from TETRAPOL networks.

---

## 4. LLM Triage Hints (Spectral and Temporal Heuristics)

Provide guidelines to help an LLM analyze metadata:
* **Audio Characteristics**: Sounds like a continuous data stream or hiss, characteristic of FDMA GMSK (similar to a constant P25 or NXDN channel but at a different baud rate).
* **Common False Positives**: Can be confused with TETRA, but remember TETRAPOL is FDMA (narrow continuous channels) while TETRA is TDMA (wider channels with 4-slot buzz).
