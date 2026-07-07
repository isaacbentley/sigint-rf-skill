# Signal Identification Reference Matrix

This matrix provides approximate physical layer parameters, occupied bandwidths, temporal patterns, and key identifiers for common wireless protocols.

Use this matrix to cross-reference extracted metrics with candidate protocols:

| Center Freq (Approx) | Bandwidth | Signal Type | Temporal Pattern | Key Identifier | Protocol |
|---|---|---|---|---|---|
| 125 kHz | — | ASK / FSK | Continuous loop | EM4100/HID Prox (Proxmark3 only) | **LF RFID (125 kHz)** |
| 13.56 MHz | ~1.5 MHz | ASK (load mod) | Reader-initiated | ISO 14443A/B, MIFARE, NFC-A/B/F | **HF RFID / NFC** |
| 144.39 / 14.074 MHz | 12 kHz / 50 Hz | AFSK / 8-GFSK | Bursty / 15s cycles | Bell 202 tones (APRS), FT8 tone blocks | **Amateur Digital (APRS/FT8/SSTV)** |
| 27 MHz | 8 kHz / 3 kHz | AM / SSB | Bursty (voice) | 10 kHz channel spacing | **CB Radio** |
| 88 - 108 MHz | ~200 kHz | WBFM | Continuous | 19 kHz stereo pilot, audio | **FM Broadcast (WBFM)** |
| 129 - 137 MHz | 6 - 8 kHz | AM + MSK | Bursty (50-200 ms), event-triggered | 2400 baud MSK on AM carrier, ASCII text | **ACARS (Aviation Data)** |
| VHF / UHF / 700 / 800 MHz | 12.5 kHz | 4FSK | Continuous / Bursty | 4800 sym/s, 30 ms / 2-slot TDMA | **DMR (MotoTRBO)** |
| VHF / UHF / 700 / 800 MHz | 12.5 kHz | C4FM / HDQPSK | Continuous (CC) / Bursty (VC) | 4800 sym/s (Ph 1), 6000 sym/s 30 ms TDMA (Ph 2) | **APCO P25 (Phase I/II)** |
| VHF / UHF | 25 kHz | π/4-DQPSK | Continuous / trunked | 18000 sym/s, 14.17 ms / 4-slot TDMA | **TETRA** |
| 137 MHz | 34 kHz / 140 kHz | WFM / QPSK | Continuous (8-15 min pass) | 2400 Hz APT tone / 72 kBaud LRPT | **NOAA APT / Meteor LRPT** |
| 144 / 440 MHz | 12.5 - 25 kHz | NBFM | Bursty (seconds/mins) | CTCSS tone, repeater tail/ID | **Amateur FM Repeater** |
| 148 - 152 / 166.38 MHz | ~1 kHz / coded OOK | CW beacon / OOK | Pulsed 30-80/min / coded bursts | Simple pulsed carrier (VHF collar) / Motus nanotag | **Wildlife Tracking** |
| 152 / 929 MHz | 12 - 25 kHz | FSK | Continuous preamble + batches | Sync 0x7CD215D8, 512/1200/2400 baud | **Pager (POCSAG / FLEX)** |
| 156 - 162 MHz | 15 kHz | NBFM / AFSK | Bursty / AFSK bursts | Ch 16 voice, Ch 70 DSC braap | **Marine VHF** |
| 161.975 / 162.025 MHz | 25 kHz | GMSK | TDMA (26.7 ms slots) | 9600 baud, HDLC framing, dual-channel | **AIS (Ship Tracking)** |
| 162.4 - 162.55 MHz | 10 kHz (NBFM) | FM / FSK | Continuous broadcast | 7 fixed channels, SAME alert header | **NOAA Weather Radio (NWR)** |
| 174 - 240 MHz | 1.536 MHz | OFDM (DQPSK) | Continuous, 96 ms frame | Flat-top, 1.29 ms Null Symbol gap | **DAB / DAB+** |
| 315 / 433 MHz | 60 - 100 kHz | FSK (or OOK) | Bursty (3-10 ms) | Preamble 0101... + Sync 0x542C | **TPMS (Tire Pressure)** |
| 315 / 433 / 868 MHz | 10 - 60 kHz | OOK / FSK | Bursty (20-80 ms), periodic 30-60s | Manchester / PWM preamble | **Weather Station (rtl_433)** |
| 315 / 433 MHz | 10 - 30 kHz | OOK | Bursty (5-30 ms), event-triggered | Fixed / rolling code (PT2262, KeeLoq) | **RKE / Garage Remote** |
| 315 / 345 / 433 MHz | 10 - 50 kHz | OOK / FSK | Bursty + 60-90 min supervisory | Device ID + status flags (alarm/tamper) | **Home Security Sensor** |
| 315 / 433 MHz | 5 - 20 kHz | OOK | Bursty (5-15 ms), event-triggered | Tri-state / PWM, 12-24 bits total | **Doorbell / RF Remote** |
| 400 - 406 MHz | 6 - 12 kHz | GFSK | Continuous 1 Hz, 90+ min | 4800 baud, RS FEC, RS41/DFM frame | **Radiosonde (Weather Balloon)** |
| 401.65 / 401.7 MHz | 750 Hz - 1.5 kHz | BPSK / PM | Short bursts, 45-200s interval | Argos PTT / GOES DCP timed uplinks | **Environmental / Wildfire (Argos/GOES)** |
| 433 / 868 / 915 MHz / 2.4 GHz | 125, 250, 500 kHz | CSS (Chirp Spread) | Bursty / Dwell sweeps | Preamble of up-chirps & down-chirps | **LoRa** |
| 433 MHz | 10 - 40 kHz | OOK | Bursty (10-40 ms), periodic 30-120s | Short payload, temp only | **Temperature Probe (rtl_433)** |
| 868 / 908 MHz | 200 kHz | FSK | Bursty, event-triggered | 9.6-100 kbps, Z-Wave home automation | **Z-Wave** |
| 902 - 928 MHz | 50 - 200 kHz | OOK / FSK | Periodic (5-30s) | SCM / IDM Manchester, sync 0x16A3 | **AMR Smart Meter** |
| 902 - 928 MHz | 200 - 500 kHz | ASK (PIE) | Reader CW + tag backscatter | EPC Gen2, strong/weak power asymmetry | **UHF RFID (EPC Gen2)** |
| 1090 MHz | 2 MHz | PPM (Pulse Position) | Bursty (120 µs) | 8 µs preamble (4 pulses) | **ADS-B Mode S** |
| 1575.42 MHz | 2.046 MHz | BPSK/CDMA | Continuous (below noise) | Invisible wideband noise hump | **GPS/GNSS L1** |
| 1616 - 1626 MHz | 31.5 kHz | QPSK | TDMA bursts (90 ms frame)| Fast Doppler drift, 31 kHz bursts | **Iridium** |
| 1880 - 1930 MHz | 1.728 MHz | GFSK | TDMA (10 ms frame) | 100 Hz pulsing beacon | **DECT Cordless Phone** |
| 2.4 / 5.8 GHz | 10, 20, 40 MHz | OFDM (601+ subcarriers) | Bursty (1.4 - 15 ms) | Dual ZC lock (root 600 & 147) | **DJI OcuSync (O1-O4)** |
| 2.4 / 5 / 6 GHz | 20, 40, 80, 160 MHz | OFDM (64+ subcarriers) | Bursty (variable) | L-LTF / L-STF preambles | **Wi-Fi (802.11a/g/n/ac/ax)** |
| 2.4 GHz / 868 / 915 MHz | 2 MHz / 600 kHz | O-QPSK (DSSS) | Bursty, beacons | 802.15.4, 250 kbps, 16 channels | **Zigbee / Thread / Matter** |
| 2.4 GHz | 1 - 2 MHz | GFSK | Bursty, freq-hopping / advertising | BLE adv on 2402/2426/2480 MHz | **Bluetooth / BLE** |
| 2.437 GHz / BLE adv ch | 20 MHz / 2 MHz | OFDM / GFSK | ≥ 1 Hz periodic | OUI FA:0B:BC (Wi-Fi) / UUID 0xFFFA (BLE) | **Drone Remote ID (ASTM F3411)** |
| 5.8 GHz | ~20 - 30 MHz | Analog (Wideband FM) | Continuous / Steady | Line sync horizontal pulses (PAL/NTSC) | **FPV Analog Video** |
| 470 - 698 MHz | 6 MHz | OFDM / 8VSB | Continuous broadcast | 8K/16K/32K FFT modes, scattered pilots | **ATSC (3.0 / 1.0)** |
| 470 - 862 MHz | 8 MHz | OFDM | Continuous broadcast | 2K/8K FFT modes, scattered pilots | **DVB-T / DVB-T2** |
| 700 MHz - 2.6 GHz | 1.4 - 20 MHz | OFDM / SC-FDMA | Continuous downlink | Zadoff-Chu PSS/SSS, Cell RS | **LTE / 4G Cellular** |

> 🕰️ **Note on Legacy Signals**: The table above focuses on protocols actively and commonly deployed today. For legacy or phased-out systems (e.g., Motorola SmartNet, EDACS, LTR, OpenSky, iDEN, MPT-1327, TETRAPOL, GSM 2G), you will automatically cross-reference the local `signals/` library or conduct web research.

> 📁 **Matrix-only rows**: most rows map to a dedicated folder under [signals/](.) (`spec.md` + `triage_hints.md`). A couple of actively-deployed rows — **TETRA** and **NOAA Weather Radio (NWR)** — are matrix-only for now: triage them from the row plus web research, then offer to add a library entry.

> 📡 **Band Plan References**: Cross-reference frequencies against regulatory allocations in [band_plans/](band_plans/) — [ITU](band_plans/itu_allocations.md), [FCC US](band_plans/fcc_us_allocations.md), [EU CEPT](band_plans/eu_cept_allocations.md)
