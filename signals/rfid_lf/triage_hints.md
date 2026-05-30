# Triage Hints: LF RFID (125–134 kHz) 🏷️

## Important: Not SDR-Receivable
> ⚠️ **125 kHz is below the tuning range of all common SDR receivers** (RTL-SDR: 24–1766 MHz, HackRF: 1–6000 MHz). LF RFID requires a dedicated reader (Proxmark3, Flipper Zero). If your SDR triage tool reports a signal near 125 kHz, it is NOT RFID — it is likely powerline interference, VLF navigation, or an artifact.

## When to Suspect LF RFID
* You're investigating an **access control system** (building entry, parking garage, hotel room)
* You have a **key fob, badge, or card** that works at very short range (~1–5 cm)
* The card/fob has **no visible markings** for a specific technology
* You see a reader with **no NFC/contactless symbol** (🔵 tap symbol = usually HF/NFC)

## Identification Workflow (with Proxmark3)

### Step 1: Auto-detect tag type
```bash
# Proxmark3 — automatic detection
pm3 -c "lf search"
# This cycles through all known LF modulation schemes and reports:
#   - EM4100 (Manchester), HID Prox (FSK), Indala (PSK), AWID (FSK),
#     FDX-B (Biphase), Paradox (FSK), Viking, Visa2000, etc.
```

### Step 2: Read specific tag type
```bash
# EM4100 (most common)
pm3 -c "lf em 410x reader"

# HID Prox
pm3 -c "lf hid reader"

# FDX-B animal tag (134.2 kHz)
pm3 -c "lf fdxb reader"

# T5577 (chameleon — detects config block)
pm3 -c "lf t55xx detect"
```

### Step 3: Analyze modulation
```bash
# Raw signal capture and plot
pm3 -c "lf read"      # Capture raw samples from antenna
pm3 -c "data plot"     # Plot the captured waveform
pm3 -c "data detect"   # Auto-detect clock rate and modulation
```

## Tag Type Identification
* **EM4100**: Manchester encoded, 64-bit continuous loop, no authentication challenge
* **HID Prox**: FSK with dual subcarriers (RF/50 + RF/64), 26-bit Wiegand format
* **FDX-B**: 134.2 kHz, biphase encoding, 128-bit loop — used for animal ID (ISO 11784/11785)
* **T5577**: Configurable — will respond as EM4100, HID, or Indala depending on configuration
* **Indala**: PSK modulation, 26 or 29 bit format, proprietary to HID Global

## Differentiation
| Confusable | Key Differentiator |
|---|---|
| **HF RFID / NFC (13.56 MHz)** | 100× higher frequency, visible on some SDRs, different protocols (ISO 14443/15693) |
| **UHF RFID (860–960 MHz)** | Radiated RF (not near-field), receivable by SDR, completely different protocol (EPC Gen2) |
| **Powerline noise at 125 kHz** | Broadband interference, not coherent modulated signal |
| **VLF navigation (LORAN-C)** | 100 kHz pulsed, very different signal structure |

## Confidence Checklist
- [ ] Card/fob works at very short range (< 5 cm)?
- [ ] Proxmark3 `lf search` returns a positive detection?
- [ ] Modulation matches known type (Manchester / FSK / PSK / Biphase)?
- [ ] Tag ID is consistent across multiple reads?
- [ ] Card is thick/clamshell style (not thin like a credit card → think HF)?

