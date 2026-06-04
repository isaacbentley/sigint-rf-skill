# Signal Specification Template: Motorola Type II SmartNet / SmartZone

Use this template to add a new RF signal type to the `signals/` registry. Fill out the fields with maximum detail to allow an LLM or developer to identify and write a decoder for the signal.

---

## 1. Physical Layer Parameters

* **Frequency Band**: 800 MHz, 900 MHz, VHF, UHF
* **Standard Bandwidth(s)**: 12.5 kHz or 25 kHz
* **Modulation Schema**: FSK
* **Symbol/Chirp Rate**: 3600 bps (Control Channel)
* **Spectral Characteristics**: FSK control channel with continuous data stream.

---

## 2. Synchronization & Frame Geometry

### Preamble / Sync Pattern
Control channels continuously broadcast data streams to manage talkgroups and radio affiliations.
The system uses Outbound Signaling Words (OSW) on the control channel.

### Frame Format
Motorola Type II systems eliminated the fleetmap dependencies found in Type I systems, allowing for greater flexibility and an increased number of radio IDs and talkgroups.
- **Radio IDs:** Capable of supporting up to 65,534 unique radio IDs.
- **Talkgroups:** Supports up to 4,095 talkgroups.
- **Status Bits:** Type II systems utilize status bits for special functions (e.g., Emergency, Patches, DES/DVP encryption, Multi-selects).

---

## 3. Demodulation Pipeline (Step-by-Step)

Explain the DSP pipeline needed to decode this signal from raw IQ:
1. **FM Demodulation**: Use a frequency discriminator to demodulate the FSK control channel.
2. **Clock Recovery**: Recover the 3600 baud clock from the baseband audio.
3. **Symbol Decision**: Slice the audio into bits.
4. **OSW Parsing**: Decode the Outbound Signaling Words.

---

## 4. LLM Triage Hints (Spectral and Temporal Heuristics)

Provide guidelines to help an LLM analyze metadata:
* **Audio Characteristics**: A continuous 3600 bps buzz.
* **Control vs Voice**: The control channel is always on; voice channels are intermittent and carry analog voice or encrypted audio.
* **Recommended Decoders**: Unitrunker, SDRTrunk.
