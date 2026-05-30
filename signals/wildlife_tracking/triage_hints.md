# Triage Hints: Wildlife Tracking & Telemetry 🦌📡

## Spectral Indicators
* **148–152 MHz**: VHF telemetry collars — pulsed CW beacons (no data, just periodic "beeps")
* **166.380 MHz**: Motus nanotags — coded OOK pulse trains, extremely weak (~1 mW)
* **401.650 MHz**: Argos satellite uplink — 1-second bursts every 45–200 seconds
* **402.0 MHz**: ICARUS tags — uplink to ISS during passes

## Key Identification Heuristic

### VHF Collars (148–152 MHz)
> **If you hear periodic beeps (30–80/min) on a VHF frequency with no data modulation, it's likely a wildlife telemetry collar.** The signal is a simple pulsed carrier with no encoded information — just a beacon for direction-finding. If the pulse rate suddenly doubles, the animal may have died (mortality sensor triggered).

### Motus Nanotags (166.380 MHz)
> **If you detect extremely weak coded pulse bursts at exactly 166.380 MHz, it may be a Motus wildlife nanotag.** Tags transmit unique 4-pulse patterns with specific inter-pulse timing to encode the tag ID. You need to be within 15 km and have a good antenna.

### Argos (401.650 MHz)
> **A 1-second burst at 401.65 MHz repeating every ~90 seconds is an Argos PTT.** Don't confuse with radiosondes (400–406 MHz, continuous 1 Hz) — Argos is short bursts with long gaps.

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Radiosonde (400–406 MHz)** | Radiosonde is continuous 1 Hz GFSK for 90+ min; Argos is 1-sec bursts with 45–200 sec gaps |
| **Amateur radio 2m (144–148 MHz)** | Amateur is voice/data with modulation; VHF collars are simple pulsed CW beacons |
| **NOAA weather satellite (137 MHz)** | NOAA is continuous pass with FM subcarrier; Motus is coded pulses at 166 MHz |
| **Marine VHF (156–162 MHz)** | Marine is voice/DSC at different frequencies; wildlife is coded pulses at 166.38 MHz |
| **GOES DCP (401.7 MHz)** | DCP is BPSK with scheduled timed windows; Argos is PM with periodic ~90s repetition |
