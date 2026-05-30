# Signal Specification: Doorbells & RF Remotes (rtl_433) 🔔

Wireless doorbells, RF outlet switches/plugs, ceiling fan remotes, light dimmer remotes, and generic RF relay controls. The simplest and shortest packets in the Sub-GHz world.

---

## 1. Physical Layer Parameters

* **Frequency Bands**: 315 MHz (US), 433.92 MHz (global), 868 MHz (EU)
* **Modulation**: OOK/ASK (almost exclusively)
* **Symbol Rates**: 1–3 kBaud (very slow, long pulse widths)
* **Encoding**: PWM or tri-state (PT2262 family)
* **Occupied Bandwidth**: 5–20 kHz (extremely narrow)

---

## 2. Device Types

| Category | Example Models | Typical Bits |
|---|---|---|
| Wireless Doorbells | Byron, Friedland, Heath Zenith, SadoTech | 12–24 bits |
| RF Outlet Switches | Etekcity, BN-LINK, remote power strips | 12–24 bits |
| Ceiling Fan Remotes | Hampton Bay, Hunter, Harbor Breeze | 12–16 bits |
| Light Dimmer Remotes | Various | 12–20 bits |
| RF Relay Controls | Generic 433 MHz relays | 12–24 bits |

---

## 3. Encoding Details

### Tri-state Encoding (PT2262)
Each logical bit is encoded as one of 3 states using pulse-width ratios:
* **Logic 0**: Short HIGH + Long LOW (1:3 ratio)
* **Logic 1**: Long HIGH + Short LOW (3:1 ratio)
* **Floating**: Short HIGH + Short LOW (1:1 ratio — used for DIP switch "middle" position)

12 tri-state bits = 24 actual pulse widths in the transmission.

### PWM Encoding
* **Logic 0**: Short HIGH / Long LOW duty cycle
* **Logic 1**: Long HIGH / Short LOW duty cycle

---

## 4. Frame Geometry

```
| Sync Pulse (1 long LOW) | Address/House Code (5-20 bits) | Channel (2-4 bits) | Button (2-4 bits) |
```

* **Total packet**: 12–24 bits (the shortest in Sub-GHz ISM)
* **No CRC**: Most simple remotes have no error detection
* **Fixed code**: Same transmission every press — trivially replayable

---

## 5. Burst Characteristics

* **Burst Duration**: 5–15 ms per packet (extremely short)
* **Repetitions**: 5–20 rapid-fire repeats on button press
* **Periodic Reporting**: **None** — event-triggered only
* **Duty Cycle**: ~0%

---

## 6. Demodulation Pipeline

```mermaid
graph LR
    A["Raw IQ"] --> B["BPF ±15 kHz"]
    B --> C["Envelope Detection"]
    C --> D["Threshold Slicer"]
    D --> E["Pulse Width Measurement"]
    E --> F["Tri-state / PWM Decode"]
    F --> G["Address + Button Extract"]
```

---

## 7. Companion Tool

```bash
# Auto-detect doorbells and remotes
rtl_433 -f 433920000 -s 250000

# US 315 MHz devices
rtl_433 -f 315000000 -s 250000
```
