# Signal Specification Template: Harris EDACS

Use this template to add a new RF signal type to the `signals/` registry. Fill out the fields with maximum detail to allow an LLM or developer to identify and write a decoder for the signal.

---

## 1. Physical Layer Parameters

* **Frequency Band**: VHF, UHF, 800 MHz, 900 MHz
* **Standard Bandwidth(s)**: 25 kHz (Wideband) / 12.5 kHz (Narrowband)
* **Modulation Schema**: FSK
* **Symbol/Chirp Rate**: 9600 bps (Wideband) / 4800 bps (Narrowband)
* **Spectral Characteristics**: FSK with dedicated continuous control channel.

---

## 2. Synchronization & Frame Geometry

### Preamble / Sync Pattern
EDACS operates in three primary modes: **Wideband**, **Narrowband**, and **Encrypted (ESK)**.

### Frame Format
- Uses Logical Channel Numbers (LCN) which must be programmed in the exact order.
- Voice channels can use analog FM or digital encoding (AEGIS or ProVoice).

---

## 3. Demodulation Pipeline (Step-by-Step)

Explain the DSP pipeline needed to decode this signal from raw IQ:
1. **FM Demodulation**: Baseband recovery of FSK.
2. **Bit Slicing**: Slice bits at 9600 or 4800 bps depending on wideband vs narrowband.
3. **Frame Parsing**: Extract LCN, Talkgroup, and Radio ID details.

---

## 4. LLM Triage Hints (Spectral and Temporal Heuristics)

Provide guidelines to help an LLM analyze metadata:
* **Autocorrelation peaks at**: The data rate rhythm is clearly audible and changes tempo when voice traffic is active on the system.
* **Common False Positives**: SmartNet. EDACS can be distinguished by its 9600 bps rate on wideband vs SmartNet's 3600 bps.
* **Recommended Decoders**: Unitrunker, SDRTrunk.
