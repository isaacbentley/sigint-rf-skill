# Signal Specification: Temperature & Humidity Probes (rtl_433) 🌡️

Specialized single-purpose sensors: pool/spa thermometers, BBQ/meat probes, freezer alarms, soil moisture sensors. Simpler and shorter packets than full weather stations.

---

## 1. Physical Layer Parameters

* **Frequency Band**: 433.92 MHz (primary), 915 MHz (US)
* **Modulation**: OOK/ASK (dominant), some FSK
* **Symbol Rates**: 1–4 kBaud
* **Encoding**: PWM (most common), Manchester (some)
* **Occupied Bandwidth**: 10–40 kHz

---

## 2. Device Types & Models

| Category | Example Models | Payload Fields |
|---|---|---|
| Pool/Spa Thermometers | Ambient Weather WH31E, Inkbird IBS-P01R | ID, Water Temp, Battery |
| BBQ/Meat Probes | Maverick ET-732/733, Inkbird IBT-4XS | ID, Probe 1 Temp, Probe 2 Temp |
| Freezer/Fridge Alarms | Govee H5074, Thermopro TX-2 | ID, Temp, Humidity, Battery |
| Soil Moisture | Ecowitt WH51 | ID, Moisture %, Battery |

---

## 3. Frame Geometry

```
| Preamble (8-16 bits) | Sync (8 bits) | Sensor ID (8-16 bits) | Temp (12 bits) | Hum (8 bits) | Battery (1 bit) | CRC-8 |
```

* **Total payload**: 8–16 bytes (shorter than weather stations)
* **Temperature resolution**: 0.1°C typical
* **CRC**: CRC-8 or simple byte-sum checksum

---

## 4. Burst Characteristics

* **Burst Duration**: 10–40 ms (shorter than weather stations)
* **Repetitions**: 2–4 packets per event
* **Reporting Interval**: 30–120 seconds
* **Duty Cycle**: < 0.5%

---

## 5. Demodulation Pipeline

```mermaid
graph LR
    A["Raw IQ"] --> B["BPF ±30 kHz"]
    B --> C["Envelope Detection"]
    C --> D["Threshold Slicer"]
    D --> E["PWM/Manchester Decode"]
    E --> F["Packet Assembly"]
    F --> G["CRC Verify"]
    G --> H["Temp/Humidity Extract"]
```

---

## 6. Companion Tool

```bash
# Auto-detect all temperature probes
rtl_433 -f 433920000 -s 250000 -F json
```
