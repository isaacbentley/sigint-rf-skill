# Signal Specification Template: [Signal Name]

Use this template to add a new RF signal type to the `signals/` registry. Fill out the fields with maximum detail to allow an LLM or developer to identify and write a decoder for the signal.

---

## 1. Physical Layer Parameters

* **Frequency Band**: (e.g., 2400 MHz to 2483.5 MHz)
* **Standard Bandwidth(s)**: (e.g., 125 kHz, 250 kHz)
* **Modulation Schema**: (e.g., QPSK, GFSK, CSS)
* **Symbol/Chirp Rate**: (e.g., 1 MSym/s)
* **Spectral Characteristics**: (e.g., flat top, dual-sideband, sync carriers)

---

## 2. Synchronization & Frame Geometry

### Preamble / Sync Pattern
Describe the synchronization sequence (e.g., Barker sequence, Gold code, Zadoff-Chu root, or FM line pulse). Provide the mathematical formula or exact bit pattern:
$$r[n] = e^{-j \frac{\pi u n (n+1)}{N}}$$

### Frame Format
Describe the block layout of the frame (e.g., header length, payload length, trailing CRC size):
```
| Preamble (8 bytes) | SFD (2 bytes) | Length (1 byte) | Payload (N bytes) | CRC16 (2 bytes) |
```

---

## 3. Demodulation Pipeline (Step-by-Step)

Explain the DSP pipeline needed to decode this signal from raw IQ:
1. **DC Blocking & HPF**: (e.g., Suppress LO leakage at DC)
2. **Frequency Shift**: (e.g., Mix down to baseband if center frequency offset exists)
3. **Low-Pass Filtering**: (e.g., Decimate or match-filter using a Root-Raised Cosine filter)
4. **Timing Recovery**: (e.g., Mueller and Müller or Early-Late Gate sync)
5. **Phase Recovery**: (e.g., Costas Loop)
6. **Symbol Decision & Framing**: (e.g., Gray code mapping, descrambling)

---

## 4. LLM Triage Hints (Spectral and Temporal Heuristics)

Provide guidelines to help an LLM analyze metadata:
* **Autocorrelation peaks at**: (e.g., $N$ samples, corresponding to the cyclic prefix duration)
* **PSD profile**: (e.g., Sharp edges with 64 subcarriers spaced at 312.5 kHz)
* **Temporal duration**: (e.g., Bursty packets with a duration of exactly $120\ \mu\text{s}$)
* **Common False Positives**: (e.g., Mistaking Bluetooth frequency hoppers for this protocol due to narrow bandwidth)
