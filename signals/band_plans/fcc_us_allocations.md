# FCC US Frequency Allocations (Triage Reference) 🇺🇸

US-specific allocations with FCC Part numbers and service rules. Complements the ITU global reference.

> **Usage**: When analyzing signals captured in the United States, use this table to identify the legal service allocation and narrow your protocol search.

---

## Sub-1 GHz Allocations

### Licensed Services

| Frequency Range | FCC Part | Service | Ch. BW | Notes |
|---|---|---|---|---|
| 525 – 1705 kHz | Part 73 | AM Broadcast | 10 kHz | Standard AM radio |
| 1.8 – 2.0 MHz | Part 97 | Amateur (160m) | — | — |
| 3.5 – 4.0 MHz | Part 97 | Amateur (80m) | — | — |
| 7.0 – 7.3 MHz | Part 97 | Amateur (40m) | — | — |
| 14.0 – 14.35 MHz | Part 97 | Amateur (20m) | — | — |
| 26.965 – 27.405 MHz | Part 95E | Citizens Band (CB) | 10 kHz | 40 channels, AM/SSB, 4W |
| 28.0 – 29.7 MHz | Part 97 | Amateur (10m) | — | — |
| 30 – 50 MHz | Part 90 | Land Mobile | 12.5–25 kHz | Public safety, business |
| 50 – 54 MHz | Part 97 | Amateur (6m) | — | — |
| 54 – 72 MHz | Part 73 | TV Ch 2–4 | 6 MHz | Mostly cleared |
| 76 – 88 MHz | Part 73 | TV Ch 5–6 | 6 MHz | Mostly cleared |
| 87.9 – 107.9 MHz | Part 73 | FM Broadcast | 200 kHz | FM stereo radio |
| 108 – 117.975 MHz | — | Aeronautical NAV | 25/50 kHz | VOR, ILS |
| **118 – 136.975 MHz** | **— ** | **Aeronautical COM** | **8.33/25 kHz** | **Air band AM voice** |
| **137 – 138 MHz** | **— ** | **Space → Earth** | **— ** | **NOAA APT satellites (137.1, 137.5, 137.9125)** |
| 144 – 148 MHz | Part 97 | Amateur (2m) | — | FM simplex/repeater, APRS |
| 150 – 174 MHz | Part 90 | Land Mobile VHF | 12.5–25 kHz | Business, public safety |
| 151.82 – 151.94 MHz | Part 95J | MURS | 11.25/20 kHz | Multi-Use Radio Service, 5 channels, 2W |
| **156 – 162 MHz** | **— ** | **Maritime VHF** | **25 kHz** | **Ch 16 = 156.800 MHz (distress)** |
| **162.400 – 162.550 MHz** | **— ** | **NOAA Weather Radio** | **— ** | **NWR, 7 channels, continuous** |
| 174 – 216 MHz | Part 73 | TV Ch 7–13 | 6 MHz | ATSC DTV |
| 216 – 220 MHz | Part 90 | Fixed / Land Mobile | — | — |
| 220 – 222 MHz | Part 97 | Amateur (1.25m) | — | — |
| 225 – 380 MHz | — | Military | — | UHF mil air, SATCOM |

### ISM / Unlicensed Bands

| Frequency Range | FCC Part | Service | Max Power | Common Devices |
|---|---|---|---|---|
| **260 – 470 MHz** | **Part 15** | **Low-power unlicensed** | **varies** | **Catch-all for Sub-GHz ISM** |
| **315 MHz** | Part 15.231 | Periodic transmitters | 12.5 mV/m @ 3m | **Car key fobs, garage door openers, TPMS** |
| **345 MHz** | Part 15 | Low-power | Varies | **Honeywell/2GIG security sensors** |
| **433.05 – 434.79 MHz** | Part 15.231 | Periodic transmitters | 12.5 mV/m @ 3m | **Weather stations, TPMS, key fobs, doorbells** |
| 462.5625 – 462.7375 MHz | Part 95A | FRS | 2W (Ch 1–7) | Family Radio Service |
| 462.550 – 462.725 MHz | Part 95A | GMRS | 5–50W | General Mobile Radio Service |
| **902 – 928 MHz** | **Part 15.247** | **ISM (spread spectrum)** | **1W** | **LoRa, AMR utility meters, Zigbee 900** |

---

## 1 – 6 GHz Allocations

| Frequency Range | FCC Part | Service | Ch. BW | Notes |
|---|---|---|---|---|
| **1090 MHz** | — | Aeronautical | — | **ADS-B Mode S transponders** |
| 1164 – 1300 MHz | — | GNSS | — | GPS L2/L5 |
| 1240 – 1300 MHz | Part 97 | Amateur (23cm) | — | — |
| **1575.42 MHz** | — | GNSS | 2 MHz | **GPS L1** |
| 1710 – 1755 MHz | — | Cellular (AWS uplink) | Various | LTE Band 4/66 |
| 1850 – 1910 MHz | — | Cellular (PCS uplink) | Various | LTE Band 2/25 |
| 1930 – 1990 MHz | — | Cellular (PCS downlink) | Various | LTE Band 2/25 |
| 2110 – 2155 MHz | — | Cellular (AWS downlink) | Various | LTE Band 4/66 |
| **2400 – 2483.5 MHz** | **Part 15.247** | **ISM (unlicensed)** | **— ** | **Wi-Fi 2.4G, Bluetooth, Zigbee, DJI, LoRa 2.4G** |
| 2500 – 2690 MHz | — | Cellular (BRS/EBS) | Various | LTE Band 41 (5G) |
| 3450 – 3550 MHz | — | Cellular (CBRS) | Various | 5G n77/n78 C-band |
| 3700 – 3980 MHz | — | Cellular (C-band) | Various | 5G n77 |
| 5150 – 5250 MHz | Part 15.401 | UNII-1 | 20–160 MHz | Wi-Fi indoor only |
| 5250 – 5350 MHz | Part 15.401 | UNII-2 | 20–160 MHz | Wi-Fi, DFS required |
| 5470 – 5725 MHz | Part 15.401 | UNII-2 Extended | 20–160 MHz | Wi-Fi, DFS required |
| **5725 – 5850 MHz** | **Part 15.247** | **ISM (unlicensed)** | **— ** | **FPV analog video, 5.8 GHz Wi-Fi** |
| 5850 – 5895 MHz | Part 15.401 | UNII-4 | — | C-V2X / Wi-Fi |
| 5925 – 7125 MHz | Part 15.407 | UNII-5/6/7/8 | 20–320 MHz | Wi-Fi 6E (6 GHz band) |

---

## Quick Reference: FCC Part Numbers

| FCC Part | Covers |
|---|---|
| **Part 15** | Unlicensed intentional/unintentional radiators (ISM devices, Wi-Fi, BLE, Sub-GHz) |
| Part 15.231 | Periodic operation devices (key fobs, garage openers, weather stations) |
| Part 15.247 | Spread spectrum / digital modulation ISM (Wi-Fi, LoRa, Zigbee) |
| Part 15.401–407 | UNII devices (5 GHz / 6 GHz Wi-Fi) |
| **Part 73** | Broadcast services (AM, FM, TV) |
| **Part 87** | Aviation services |
| **Part 90** | Private land mobile radio (business, public safety) |
| **Part 95** | Personal radio services (CB, FRS, GMRS, MURS) |
| **Part 97** | Amateur radio |

---

## ISM Band Summary (Most Relevant for rtl_433 / SDR)

| Band | Region | FCC Rule | Primary rtl_433 Signals |
|---|---|---|---|
| **315 MHz** | US | Part 15.231 | Car key fobs, TPMS, garage remotes |
| **345 MHz** | US | Part 15 | Honeywell/2GIG security sensors |
| **433.92 MHz** | EU/Asia (US limited) | Part 15.231 | Weather stations, TPMS, doorbells, key fobs |
| **868 MHz** | EU | — (not FCC) | LoRa EU, Bresser, Sigfox, SRD |
| **902–928 MHz** | US | Part 15.247 | LoRa US, AMR utility meters, Zigbee |
| **2.4 GHz** | Global | Part 15.247 | Wi-Fi, BLE, Zigbee, DJI OcuSync |
| **5.8 GHz** | Global | Part 15.247 | FPV analog video, Wi-Fi |
