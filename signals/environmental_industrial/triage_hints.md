# Triage Hints: Environmental & Industrial Monitoring 🔥🏭

## GOES DCP (Wildfire / Weather Stations)
* **401.701 MHz**: International DCP uplink — short BPSK bursts every 1–4 hours
* **468.750–468.950 MHz**: Domestic US DCP channels
* Very narrow bandwidth (750 Hz at 100 bps) — looks like a thin carrier with slow data
* Timed transmissions — appears at predictable intervals
* **Not commonly targeted by SDR hobbyists** — easier to get RAWS data from MesoWest website

## NOAA Weather Radio (NWR)
* **162.400–162.550 MHz**: 7 fixed channels, strong continuous NBFM broadcast
* **SAME alert encoding**: 520.83 baud FSK preamble before warnings — very distinctive rapid chirp
* **1050 Hz attention tone**: 8–25 second pure tone = unmistakable
* **Tools**: `multimon-ng -a EAS`, `rtl_fm`

## SCADA / Industrial
* **150–174 / 450–470 MHz**: Licensed business band — narrowband FM with Modbus/DNP3 data
* **902–928 MHz FHSS**: FreeWave / MDS radios — looks like spread-spectrum noise hopping across ISM band
* **2.4 GHz WirelessHART**: Same PHY as Zigbee (802.15.4) — differentiate by protocol layer

## Differentiation
| Signal | Key Differentiator |
|---|---|
| **NWR vs FM broadcast** | NWR is NBFM at 162 MHz (not 88–108 MHz FM broadcast) |
| **GOES DCP vs radiosonde** | DCP is at 401.7 / 468 MHz with short timed bursts; radiosonde is continuous 1 Hz at 400–406 MHz |
| **SCADA vs DMR** | SCADA uses continuous polling (Modbus query/response); DMR has TDMA slot structure |
| **WirelessHART vs Zigbee** | Same PHY, different network layer — WirelessHART uses TDMA scheduling, Zigbee uses CSMA/CA |
