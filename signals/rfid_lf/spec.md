# Signal Specification: LF RFID (125–134 kHz) 🏷️

Low-Frequency RFID — access cards, animal tags, key fobs. The oldest and simplest RFID technology. Near-contact read range (1–10 cm).

---

## 1. Physical Layer Parameters

* **Frequency Bands**: 125 kHz (most common), 134.2 kHz (animal tags / FDX-B)
* **Coupling**: Inductive (magnetic near-field) — NOT radiated RF
* **Read Range**: 1–10 cm (passive tags), up to 1 m (active/battery-assisted)
* **Modulation (tag → reader)**:
  - **ASK / OOK** (EM4100, HID Prox): Carrier on/off keying
  - **FSK** (HID iCLASS, T5577 in FSK mode): Frequency shift between subcarriers
  - **PSK** (Indala): Phase shift keying
* **Data Rates**: 2–8 kbps (very slow — limited by carrier frequency)
* **Encoding**: Manchester, Biphase, Miller, NRZ

---

## 2. Common Tag Types

| Tag Type | Frequency | Bits | Encoding | Security | Use Case |
|---|---|---|---|---|---|
| **EM4100 / EM4102** | 125 kHz | 64 bits (40 data) | Manchester | **None** — read-only, trivially cloneable | Budget access cards, parking |
| **HID ProxCard II (H10301)** | 125 kHz | 26 bits (Wiegand format) | FSK | **None** — trivially cloneable | Building access (most common corporate card) |
| **HID iCLASS SE** | 125 kHz | Variable | FSK | AES encryption, mutual auth | Secure access control |
| **T5577** | 125 kHz | 330 bits | Configurable (Manchester/FSK/PSK/NRZ) | None — writable emulator | "Swiss army knife" — can emulate EM4100, HID, Indala |
| **Indala FlexCard** | 125 kHz | 26/40 bits | PSK | None | Access control (Motorola/HID) |
| **AWID** | 125 kHz | 26/34/50 bits | FSK | None | Access control |
| **FDX-B (ISO 11784/85)** | 134.2 kHz | 128 bits | Biphase (DBP) | None — read-only | Animal identification (pet microchips, livestock) |
| **EM4305 / EM4469** | 125 kHz | 512 bits | Manchester | Optional password protect | Rewritable general purpose |

---

## 3. Protocol Details

### EM4100 (most common LF tag)
```
| Header (9× '1') | Version/MFR (8 bits) | Row Parity | ID (32 bits) | Row Parity | Column Parity (4 bits) | Stop (1 bit) |
```
* 64 bits total, transmitted continuously on a loop
* Manchester encoded at RF/64 clock division (125 kHz / 64 = ~1.95 kHz data rate)
* **No authentication** — tag dumps its ID whenever powered by reader field

### HID Prox (26-bit Wiegand H10301)
```
| Even Parity | Facility Code (8 bits) | Card Number (16 bits) | Odd Parity |
```
* FSK modulated: subcarriers at RF/50 and RF/64
* 26-bit format is most common; 34/37-bit formats exist
* **No authentication** — trivially cloneable with Proxmark3

### FDX-B (ISO 11784/85 — animal tags)
```
| Header (11 bits) | Country Code (10 bits) | National ID (38 bits) | Reserved | CRC-16 |
```
* 134.2 kHz carrier
* Biphase (differential bi-phase) encoding
* 128 bits total, continuously transmitted

---

## 4. Reader Communication

* **Energy harvesting**: Passive tags have no battery — they harvest energy from the reader's 125 kHz magnetic field via inductive coupling
* **Backscatter modulation**: Tag modulates the reader's carrier by switching its load (antenna coil impedance), creating amplitude or frequency variations detectable by the reader
* **Sequence**: Reader field ON → tag powers up → tag transmits ID on loop → reader demodulates

---

## 5. Tools

| Tool | Capability |
|---|---|
| **Proxmark3** | Read/write/emulate/clone all LF tags. The gold standard. |
| **Flipper Zero** | Read/emulate EM4100, HID Prox, Indala, FDX-B |
| **T5577 card** | Writable blank that can emulate most LF tag formats |
| **iCopy-XS** | Standalone LF card copier |

```bash
# Proxmark3 commands
pm3 --> lf search           # Auto-detect LF tag type
pm3 --> lf em 4100 reader   # Read EM4100 tag
pm3 --> lf hid reader       # Read HID Prox card
pm3 --> lf t55xx detect     # Detect T5577 writable tag
pm3 --> lf em 4100 clone    # Clone EM4100 to T5577
```

> ⚠️ **Note**: LF RFID operates via magnetic coupling, NOT radiated RF. It cannot be received by RTL-SDR or HackRF. A Proxmark3 or dedicated LF reader is required.

---

## 6. SDR Relevance

**LF RFID is NOT receivable by standard SDR hardware** (RTL-SDR tunes 24–1766 MHz, HackRF tunes 1–6000 MHz). The 125 kHz carrier is far below these ranges.

However, LF RFID is included in this library because:
1. It's a core topic in RF security research (DEF CON, RF Hackers)
2. The Proxmark3 (a specialized SDR for RFID frequencies) uses similar DSP concepts
3. Understanding LF RFID helps distinguish it from HF/UHF RFID which IS sometimes SDR-accessible
