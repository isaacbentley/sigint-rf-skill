# EU / CEPT / ETSI Frequency Allocations (Triage Reference) 🇪🇺

European-specific allocations with CEPT ERC/ECC Decisions and ETSI EN references. Covers EU, EEA, and UK post-Brexit (largely harmonized).

> **Usage**: When analyzing signals captured in Europe, use this table to identify the regulatory framework and narrow your protocol search.

---

## Sub-1 GHz Allocations

### Licensed Services

| Frequency Range | Regulation | Service | Ch. BW | Notes |
|---|---|---|---|---|
| 148.5 – 283.5 kHz | — | LW Broadcast | 9 kHz | AM longwave (Europe 1, RTL, etc.) |
| 283.5 – 526.5 kHz | — | Maritime / NDB | — | Non-directional beacons |
| 526.5 – 1606.5 kHz | — | MW Broadcast (AM) | 9 kHz | AM mediumwave |
| 3.5 – 3.8 MHz | CEPT T/R 61-01 | Amateur (80m) | — | SSB/CW |
| 7.0 – 7.2 MHz | CEPT T/R 61-01 | Amateur (40m) | — | SSB/CW/Digital |
| 14.0 – 14.35 MHz | CEPT T/R 61-01 | Amateur (20m) | — | — |
| 26.960 – 27.410 MHz | ECC/DEC/(11)03 | Citizens Band (CB) | 10 kHz | 40 ch, 4W FM (EU), AM in some countries |
| 28.0 – 29.7 MHz | CEPT T/R 61-01 | Amateur (10m) | — | — |
| 29.7 – 47 MHz | — | Land Mobile | 12.5 kHz | — |
| 47 – 68 MHz | — | TV Band I | 7/8 MHz | Legacy analog (decommissioned) |
| 50 – 52 MHz | CEPT T/R 61-01 | Amateur (6m) | — | Limited in some EU countries |
| 68 – 87.5 MHz | — | Land Mobile / PMR | 12.5 kHz | — |
| 87.5 – 108 MHz | — | FM Broadcast | 200 kHz | FM stereo radio |
| 108 – 117.975 MHz | ICAO | Aeronautical NAV | 25/50 kHz | VOR, ILS localizer |
| **118 – 137 MHz** | **ICAO** | **Aeronautical COM** | **8.33 kHz** | **Air band AM voice (8.33 kHz spacing mandatory in EU)** |
| 137 – 138 MHz | — | Space → Earth | — | NOAA/Meteor-M weather satellites |
| 144 – 146 MHz | CEPT T/R 61-01 | Amateur (2m) | — | FM simplex/repeater, APRS |
| 146 – 174 MHz | — | Land Mobile | 12.5 kHz | — |
| **156 – 162 MHz** | **ITU RR** | **Maritime VHF** | **25 kHz** | **Ch 16 = 156.800 MHz (distress)** |
| 169.4 – 169.8125 MHz | ECC/DEC/(05)02 | Paging / M2M | 12.5/50 kHz | Wireless M-Bus smart metering |
| 174 – 230 MHz | — | **DAB+ / DVB-T** | 1.536 MHz | DAB+ digital radio (Band III) |
| 230 – 380 MHz | — | Military / Government | — | NATO UHF SATCOM |
| 380 – 400 MHz | ECC/DEC/(08)05 | **TETRA** | 25 kHz | Emergency services trunked radio (PPDR) |
| 400.15 – 406 MHz | — | Met Aids / Radiosonde | — | Weather balloon telemetry |
| 406 – 406.1 MHz | — | COSPAS-SARSAT | — | Emergency PLB/EPIRB beacons |
| 430 – 440 MHz | CEPT T/R 61-01 | Amateur (70cm) | — | FM/SSB, shared with radiolocation |

### ISM / SRD (Short Range Device) Bands

| Frequency Range | ETSI Standard | Max Power (ERP) | Duty Cycle | Common Devices |
|---|---|---|---|---|
| **169.4 – 169.475 MHz** | EN 300 220 | 500 mW | 1–10% | Wireless M-Bus, smart metering |
| **315 MHz** | — | **Not allocated in EU** | — | **US-only ISM — not legal in Europe** |
| **433.05 – 434.79 MHz** | **EN 300 220** | **10 mW** (25 mW sub-bands) | **< 10%** | **Weather stations, TPMS, key fobs, doorbells, sensors** |
| **433.92 MHz** | **EN 300 220** | **10 mW** | **< 10%** | **Primary EU ISM frequency for Sub-GHz devices** |
| 434.04 – 434.79 MHz | EN 300 220 | 10 mW | 100% (some sub-bands) | Voice/data, wideband |
| **863 – 870 MHz** | **EN 300 220** | **25 mW** | **< 1% (most)** | **Sub-band allocations below ↓** |

#### 863–870 MHz Sub-band Plan (ERC/REC 70-03, Annex 1)

This is the primary EU SRD band, heavily subdivided:

| Sub-band | Max Power | Duty Cycle | Primary Use |
|---|---|---|---|
| 863.0 – 865.0 MHz | 25 mW | 0.1% | General SRD, alarms |
| **865.0 – 868.0 MHz** | **25 mW** | **1%** | **General SRD, weather stations (Bresser), IoT** |
| **868.0 – 868.6 MHz** | **25 mW** | **1%** | **LoRa EU868 default channels (868.1, 868.3, 868.5 MHz)** |
| 868.7 – 869.2 MHz | 25 mW | 0.1% | Alarms |
| 869.3 – 869.4 MHz | 25 mW | 1% | SRD |
| 869.4 – 869.65 MHz | 500 mW | 10% | **High-power SRD, social alarms** |
| 869.65 – 869.7 MHz | 25 mW | 10% | SRD |
| **869.7 – 870.0 MHz** | **5 mW** | **100%** | **LoRa downlink RX2, Sigfox downlink** |

| **870 – 876 MHz** | EN 300 220-2 | 25–500 mW | Varies | Extended SRD band (newer allocation) |
|---|---|---|---|---|
| **915 MHz** | — | **Not allocated in EU** | — | **US-only ISM — LoRa US, AMR meters** |

---

## 1 – 6 GHz Allocations

| Frequency Range | Regulation | Service | Ch. BW | Notes |
|---|---|---|---|---|
| **1090 MHz** | ICAO | Aeronautical | — | **ADS-B Mode S transponders** |
| 1164 – 1300 MHz | — | GNSS | — | Galileo E5a/E5b, GPS L2/L5 |
| 1240 – 1300 MHz | CEPT | Amateur (23cm) | — | — |
| **1575.42 MHz** | — | GNSS | 2 MHz | **GPS L1, Galileo E1** |
| 1710 – 1785 MHz | — | Cellular (uplink) | Various | LTE Band 3 |
| 1805 – 1880 MHz | — | Cellular (downlink) | Various | LTE Band 3 |
| 1920 – 1980 MHz | — | Cellular (uplink) | Various | UMTS/LTE Band 1 |
| 2110 – 2170 MHz | — | Cellular (downlink) | Various | UMTS/LTE Band 1 |
| **2400 – 2483.5 MHz** | **EN 300 328** | **ISM (unlicensed)** | **— ** | **Wi-Fi, Bluetooth, Zigbee, DJI, LoRa 2.4G** |
| 2500 – 2690 MHz | — | Cellular (LTE TDD) | Various | LTE Band 38/41 |
| 3.4 – 3.8 GHz | ECC/DEC/(11)06 | **5G NR** | Various | 5G n78 (primary EU 5G band) |
| 5150 – 5350 MHz | EN 301 893 | RLAN (Wi-Fi) | 20–160 MHz | Indoor only (5150–5250), DFS (5250–5350) |
| 5470 – 5725 MHz | EN 301 893 | RLAN (Wi-Fi) | 20–160 MHz | DFS required |
| **5725 – 5875 MHz** | **EN 300 440** | **ISM / SRD** | **— ** | **FPV analog video, 5.8 GHz Wi-Fi** |
| 5875 – 5905 MHz | EN 302 571 | ITS (V2X) | 10 MHz | Intelligent Transport Systems (C-ITS) |
| 5925 – 6425 MHz | EN 303 687 | RLAN (Wi-Fi 6E) | 20–160 MHz | Lower 6 GHz band (EU Wi-Fi 6E) |

---

## PMR446 (EU Licence-Free Radio)

| Frequency | Ch. BW | Service | Max Power | Notes |
|---|---|---|---|---|
| **446.00625 – 446.09375 MHz** | 12.5 kHz | PMR446 Analog | 500 mW ERP | 16 channels, FM voice, licence-free |
| **446.10625 – 446.19375 MHz** | 6.25 kHz | PMR446 Digital (dPMR) | 500 mW ERP | 16 channels, digital voice |

---

## EU vs US ISM Band Comparison

| Band | EU | US | Key Difference |
|---|---|---|---|
| **315 MHz** | ❌ Not available | ✅ Part 15.231 | EU uses 433 MHz instead |
| **345 MHz** | ❌ Not allocated | ✅ Part 15 (Honeywell) | No equivalent EU band |
| **433 MHz** | ✅ EN 300 220, 10 mW, < 10% DC | ✅ Part 15.231 (limited) | EU primary Sub-GHz ISM; US secondary |
| **868 MHz** | ✅ EN 300 220, 25 mW, 1% DC | ❌ Not available | EU-only (LoRa EU, Bresser, SRD) |
| **915 MHz** | ❌ Not available | ✅ Part 15.247, 1W | US-only (LoRa US, AMR meters) |
| **2.4 GHz** | ✅ EN 300 328, 100 mW EIRP | ✅ Part 15.247, 1W | EU lower power limit |
| **5.8 GHz** | ✅ EN 300 440, 25 mW | ✅ Part 15.247, 1W | EU lower power for ISM |

---

## Quick-Lookup: "I captured a signal in Europe at X MHz"

| If you see activity near… | First guess | Confirm with |
|---|---|---|
| 169.4 MHz | Wireless M-Bus smart metering | Narrow-band, low duty cycle |
| 433.92 MHz | Weather station, TPMS, key fob, doorbell | Check modulation & baud rate |
| 446 MHz | PMR446 walkie-talkie | FM voice, 12.5 kHz channels |
| 868 MHz | LoRa, Bresser weather, SRD sensors | CSS chirps = LoRa; flat FSK = Bresser/SRD |
| 1090 MHz | ADS-B aircraft | PPM at 1 Mbps |
| 1575 MHz | GPS L1 / Galileo E1 | Spread spectrum, very weak |
| 2.4 GHz | Wi-Fi / Bluetooth / DJI / Zigbee | Check BW: 20 MHz = Wi-Fi, 1 MHz = BLE |
| 5.8 GHz | FPV video / Wi-Fi | WFM = FPV analog, OFDM = Wi-Fi |

---

## Key ETSI Standards Reference

| Standard | Covers |
|---|---|
| **EN 300 220** | Sub-GHz SRD (433 MHz, 868 MHz) — the rtl_433 standard |
| **EN 300 328** | 2.4 GHz ISM (Wi-Fi, BLE, Zigbee) |
| **EN 300 440** | 5.8 GHz ISM, wideband SRD |
| **EN 301 893** | 5 GHz RLAN (Wi-Fi) |
| **EN 302 571** | ITS (V2X) at 5.9 GHz |
| **EN 303 687** | 6 GHz RLAN (Wi-Fi 6E) |
| **ERC/REC 70-03** | Master SRD recommendation (all bands, duty cycles, power limits) |
| **ECC/DEC/(05)02** | 169.4 MHz metering band |
| **ECC/DEC/(08)05** | TETRA public safety (380–400 MHz) |
