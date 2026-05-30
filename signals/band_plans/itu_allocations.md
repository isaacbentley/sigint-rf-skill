# ITU Radio Frequency Allocations (Triage Reference) 🌍

Quick-lookup table of ITU worldwide radio service allocations relevant to SDR analysis. Organized by frequency range for fast cross-referencing during triage.

> **Usage**: When `triage_iq.py` reports a center frequency, look it up here to narrow the protocol search space immediately.

---

## VLF / LF / MF (3 kHz – 3 MHz)

| Frequency | Bandwidth | Service | Region | Notes |
|---|---|---|---|---|
| 9 – 14 kHz | — | Navigation | Global | Alpha (Russia), RSDN-20 |
| 14 – 19.95 kHz | — | Fixed / Maritime | Global | — |
| 19.95 – 20.05 kHz | — | Standard Frequency | Global | Time signals (WWV) |
| 60 kHz | — | Time Signal | EU/Japan | DCF77 (DE), MSF (UK), JJY (JP) |
| 77.5 kHz | — | Time Signal | EU | DCF77 |
| 153 – 279 kHz | 9 kHz ch. | LW Broadcast | Region 1 (EU) | AM longwave radio |
| 283.5 – 325 kHz | — | Maritime NDB | Global | Non-directional beacons |
| 325 – 405 kHz | — | Aeronautical NDB | Global | — |
| 525 – 1705 kHz | 9/10 kHz ch. | MW Broadcast (AM) | Global | AM radio (10 kHz ch. in Americas) |

---

## HF (3 – 30 MHz)

| Frequency | Bandwidth | Service | Region | Notes |
|---|---|---|---|---|
| 3.5 – 4.0 MHz | — | Amateur (80m) | Global | SSB/CW |
| 4.750 – 5.060 MHz | — | Tropical Broadcast | Regions 1&3 | SW broadcast |
| 5.330 – 5.406 MHz | 2.8 kHz | Amateur (60m) | Varies | Channelized in some countries |
| 5.9 – 6.2 MHz | — | SW Broadcast (49m) | Global | — |
| 7.0 – 7.3 MHz | — | Amateur (40m) | Global | SSB/CW/Digital |
| 7.2 – 7.45 MHz | — | SW Broadcast (41m) | Global | — |
| 9.4 – 9.9 MHz | — | SW Broadcast (31m) | Global | — |
| 10.1 – 10.15 MHz | — | Amateur (30m) | Global | CW/Digital only |
| 11.6 – 12.1 MHz | — | SW Broadcast (25m) | Global | — |
| 14.0 – 14.35 MHz | — | Amateur (20m) | Global | SSB/CW/Digital |
| 15.1 – 15.6 MHz | — | SW Broadcast (19m) | Global | — |
| 17.48 – 17.9 MHz | — | SW Broadcast (16m) | Global | — |
| 18.068 – 18.168 MHz | — | Amateur (17m) | Global | SSB/CW/Digital |
| 21.0 – 21.45 MHz | — | Amateur (15m) | Global | — |
| 24.89 – 24.99 MHz | — | Amateur (12m) | Global | — |
| 25.67 – 26.1 MHz | — | SW Broadcast (11m) | Global | — |
| 26.965 – 27.405 MHz | 10 kHz ch. | Citizens Band (CB) | Global | AM/SSB, 40 channels |
| 28.0 – 29.7 MHz | — | Amateur (10m) | Global | FM/SSB/CW |

---

## VHF (30 – 300 MHz)

| Frequency | Bandwidth | Service | Region | Notes |
|---|---|---|---|---|
| 30 – 50 MHz | 12.5–25 kHz | Land Mobile | Global | Business/public safety |
| 47 – 68 MHz | 6–8 MHz | TV Band I | Region 1 | Analog TV (mostly decommissioned) |
| 50 – 54 MHz | — | Amateur (6m) | Global | SSB/CW/FM |
| 54 – 88 MHz | 6 MHz ch. | TV (Ch 2–6) | Americas | NTSC/ATSC |
| 74.8 – 75.2 MHz | — | Aeronautical Marker | Global | Marker beacons |
| 87.5 – 108 MHz | 200 kHz ch. | FM Broadcast | Global | Wideband FM stereo |
| 108 – 117.975 MHz | 25/50 kHz | Aeronautical NAV | Global | VOR, ILS localizer |
| **118 – 137 MHz** | **8.33/25 kHz** | **Aeronautical COM** | **Global** | **Air band AM voice** |
| 137 – 138 MHz | — | Space → Earth | Global | NOAA APT weather satellites, Meteor-M |
| 144 – 148 MHz | — | Amateur (2m) | Global | FM/SSB/CW/APRS |
| 148 – 174 MHz | 12.5–25 kHz | Land Mobile | Global | VHF business band |
| 156 – 162 MHz | 25 kHz ch. | Maritime VHF | Global | Ch 16 (156.8 MHz) = distress/calling |
| **162.4 – 162.55 MHz** | **— ** | **NOAA Weather Radio** | **US/Canada** | **NWR, continuous broadcast** |
| 169.4 – 169.8 MHz | — | Paging / Telemetry | EU | Wireless M-Bus, smart metering |
| 174 – 216 MHz | 6 MHz ch. | TV (Ch 7–13) / DAB | Mixed | ATSC (Americas), DAB+ (EU) |
| 216 – 225 MHz | — | Fixed / Land Mobile | US | — |
| 225 – 400 MHz | 25 kHz | Military Air | Global | UHF SATCOM, mil air-to-air |

---

## UHF (300 MHz – 3 GHz)

| Frequency | Bandwidth | Service | Region | Notes |
|---|---|---|---|---|
| **315 MHz** | **— ** | **ISM (unlicensed)** | **US** | **Car key fobs, TPMS, garage remotes** |
| 320 – 335 MHz | 25 kHz | Military | Various | Mil SATCOM downlinks |
| **345 MHz** | **— ** | **Proprietary** | **US** | **Honeywell/2GIG security sensors** |
| 380 – 400 MHz | 25 kHz | TETRA / Public Safety | EU | Trunked radio |
| 400.15 – 406 MHz | — | Met Aids / Radiosonde | Global | Weather balloons |
| 406 – 406.1 MHz | — | COSPAS-SARSAT | Global | Emergency beacons (EPIRB, ELT, PLB) |
| 420 – 450 MHz | — | Amateur (70cm) / Mil | Global | Amateur + military radar |
| **433.05 – 434.79 MHz** | **— ** | **ISM (unlicensed)** | **EU/Asia/Global** | **Weather stations, TPMS, key fobs, doorbells, sensors** |
| 440 – 450 MHz | — | Amateur (70cm) | Region 2/3 | FM/SSB/CW |
| 450 – 470 MHz | 12.5 kHz | Land Mobile (UHF) | Global | Business radio, GMRS (US) |
| 462 – 467 MHz | 12.5 kHz | FRS / GMRS | US | Family Radio Service (22 ch) |
| 470 – 698 MHz | 6 MHz ch. | TV (Ch 14–51) | Americas | ATSC (some cleared for wireless) |
| 470 – 790 MHz | 8 MHz ch. | TV / DVB-T | EU | Digital terrestrial TV |
| 698 – 960 MHz | Various | Cellular (LTE) | Global | LTE Bands 12/13/14/17/28/71 etc. |
| **862 – 875 MHz** | **— ** | **ISM (unlicensed)** | **EU** | **LoRa, Sigfox, smart metering, SRD** |
| **902 – 928 MHz** | **— ** | **ISM (unlicensed)** | **US** | **LoRa, utility meters (AMR), Zigbee** |
| 928 – 960 MHz | Various | Cellular / Paging | US | — |
| 960 – 1215 MHz | — | Aeronautical NAV | Global | DME, TACAN, SSR |
| **1090 MHz** | **— ** | **Aeronautical** | **Global** | **ADS-B Mode S transponders** |
| 1164 – 1300 MHz | — | GNSS | Global | GPS L5, Galileo E5, GLONASS G3 |
| 1227.6 MHz | — | GNSS | Global | GPS L2 |
| 1260 – 1300 MHz | — | Amateur (23cm) | Global | — |
| 1525 – 1559 MHz | — | Mobile Satellite | Global | Inmarsat, Iridium (downlink) |
| **1575.42 MHz** | **2 MHz** | **GNSS** | **Global** | **GPS L1, Galileo E1, BeiDou B1** |
| 1616 – 1626.5 MHz | — | Iridium | Global | Iridium satellite phone |
| 1710 – 2200 MHz | Various | Cellular (LTE/5G) | Global | AWS, PCS bands |
| **2400 – 2500 MHz** | **— ** | **ISM (unlicensed)** | **Global** | **Wi-Fi, Bluetooth, Zigbee, DJI drones, LoRa 2.4G** |

---

## Microwave (3 – 30 GHz)

| Frequency | Bandwidth | Service | Region | Notes |
|---|---|---|---|---|
| 3.3 – 3.5 GHz | — | Amateur / Radiolocation | Varies | — |
| 3.4 – 3.8 GHz | Various | 5G NR (n77/n78) | Global | C-band 5G |
| 5.15 – 5.35 GHz | 20/40/80 MHz | Wi-Fi 5 GHz (UNII-1/2) | Global | 802.11a/n/ac/ax |
| 5.47 – 5.725 GHz | Various | Wi-Fi 5 GHz (UNII-2E) | Global | DFS required (radar avoidance) |
| **5.725 – 5.875 GHz** | **— ** | **ISM (unlicensed)** | **Global** | **FPV analog video, 5.8 GHz Wi-Fi** |
| 5.925 – 7.125 GHz | Various | Wi-Fi 6E (UNII-5/6/7/8) | US/EU | 802.11ax 6 GHz band |
| 9.0 – 9.5 GHz | — | Radiolocation | Global | Marine/weather radar |
| 10.0 – 10.5 GHz | — | Amateur (3cm) | Global | — |
| 24.0 – 24.25 GHz | — | ISM / Amateur | Global | Automotive radar |

---

## Quick-Lookup: "I see a signal at X MHz"

| If you see activity near… | First guess | Confirm with |
|---|---|---|
| 315 MHz | US car key fob / TPMS / garage remote | OOK burst pattern, check for rolling code |
| 345 MHz | Honeywell security sensor | FSK at 8 kBaud, 60–90 min supervisory |
| 433.92 MHz | EU/Asia ISM (weather, TPMS, key fob, doorbell) | Check modulation, baud rate, packet length |
| 868 MHz | EU ISM (LoRa, Sigfox, smart metering, Bresser) | Check for CSS chirps (LoRa) vs flat OOK/FSK |
| 915 MHz | US ISM (LoRa, AMR utility meters) | CSS = LoRa, Manchester 32k = AMR |
| 1090 MHz | ADS-B aircraft | PPM at 1 Mbps, 120 µs frames |
| 1575 MHz | GPS L1 | Spread spectrum, very weak (-130 dBm) |
| 2.4 GHz | Wi-Fi / Bluetooth / DJI / Zigbee | Check BW: 20 MHz = Wi-Fi, 1 MHz = BLE, 10 MHz = DJI |
| 5.8 GHz | FPV video / Wi-Fi | Wideband FM = FPV analog, OFDM = Wi-Fi |
