# Signal Specification: Environmental & Wildfire Monitoring 🔥🌲

GOES DCP (Data Collection Platforms), RAWS (Remote Automated Weather Stations), and NOAA Weather Radio. Telemetry from remote environmental sensors including wildfire monitoring stations.

---

## 1. GOES DCP — Satellite Data Collection Platforms

Remote environmental sensors that uplink telemetry to NOAA's GOES geostationary satellites. Used extensively by RAWS wildfire weather stations, USGS stream gauges, NOAA tide gauges, and seismic monitors.

### Physical Layer
* **Uplink Frequency**: 401.701 MHz (international), 468.750–468.950 MHz (domestic US channels)
* **GOES Relay**: 1694.1 MHz (GOES East), 1694.5 MHz (GOES West) — HRIT/LRIT downlink
* **Modulation**: BPSK (100 bps) or QPSK (300/1200 bps)
* **Channel Bandwidth**: 750 Hz (100 bps), 1.5 kHz (300 bps)
* **TX Power**: 5–20 W (high power for geostationary satellite link)
* **Transmission**: Timed self-timed or random self-timed, 10–180 second windows
* **Interval**: Every 1–4 hours depending on configuration

### Data Contents
| RAWS Sensor | Parameter | Update Rate |
|---|---|---|
| Temperature | Air temp (°C) | Hourly |
| Relative Humidity | RH (%) | Hourly |
| Wind Speed | 10-min average + gust (m/s) | Hourly |
| Wind Direction | 10-min average (°) | Hourly |
| Precipitation | Accumulated (mm) | Hourly |
| Solar Radiation | Watts/m² | Hourly |
| Fuel Moisture | Fuel stick weight (%) | Hourly |
| Battery Voltage | System health | Hourly |

### RAWS & Wildfire Context
* **~2,200 RAWS stations** across US (NIFC/BLM/USFS)
* Data feeds into **NFDRS** (National Fire Danger Rating System)
* Real-time data available at **MesoWest** and **WRCC** (Western Regional Climate Center)
* Critical for fire weather watches and red flag warnings

---

## 2. NOAA Weather Radio (NWR) — Continuous Broadcast

* **Frequencies**: 162.400, 162.425, 162.450, 162.475, 162.500, 162.525, 162.550 MHz (7 channels)
* **Modulation**: Narrowband FM (NBFM), ±5 kHz deviation
* **Content**: Continuous weather forecasts, warnings, watches
* **Special tones**:
  - **SAME (Specific Area Message Encoding)**: 520.83 baud FSK header before alerts
  - **1050 Hz attention tone**: 8–25 second tone before warnings
  - **NWR-SAME header**: 3× preamble (0xAB) + ZCZC- + originator + event code + location codes + timestamp
* **TX Power**: 100–1000 W (excellent coverage)
* **Coverage**: ~95% of US population

### SAME Alert Decode
```
Preamble: 0xABx16 (16 bytes)
Header:   ZCZC-ORG-EEE-PSSCCC-PSSCCC+TTTT-JJJHHMM-LLLLLLLL-
Where:
  ORG = Originator (WXR=NWS, CIV=Civil, EAS=EAS participant)
  EEE = Event code (TOR=Tornado Warning, SVR=Severe Thunderstorm)
  PSSCCC = State + County FIPS code
  TTTT = Purge time (duration)
  JJJHHMM = Julian day + time
  LLLLLLLL = Station callsign
```

```bash
# Decode NOAA Weather Radio + SAME alerts
rtl_fm -f 162400000 -M fm -s 22050 -g 30 | multimon-ng -t raw -a EAS /dev/stdin
```

---

## 3. Industrial SCADA / IIoT Telemetry 🏭

### Licensed SCADA Radio (VHF/UHF)
* **Frequencies**: 150–174 MHz (VHF), 450–470 MHz (UHF) — licensed business/industrial bands
* **Modulation**: Narrowband FM or 4FSK
* **Protocols**: Modbus RTU/TCP, DNP3 (Distributed Network Protocol)
* **Data Rate**: 1200–19200 baud
* **Use**: Oil/gas pipeline SCADA, water utility, power grid telemetry
* **Hardware**: FreeWave, MDS (GE), CalAmp, Digi

### 900 MHz Spread Spectrum
* **Frequency**: 902–928 MHz (ISM, unlicensed)
* **Modulation**: FHSS (Frequency Hopping Spread Spectrum)
* **Data Rate**: 9.6–115.2 kbps
* **Range**: 10–60 km (directional antennas)
* **Hardware**: FreeWave FGR3, MDS TransNET
* **Use**: Oil field telemetry, water district SCADA, ag irrigation

### WirelessHART / ISA100.11a (2.4 GHz)
* **Frequency**: 2.4 GHz (802.15.4-based, same as Zigbee)
* **Modulation**: O-QPSK with DSSS
* **Data Rate**: 250 kbps
* **Topology**: Mesh network
* **Protocol**: HART 7 over 802.15.4 (WirelessHART) or ISA100.11a
* **Use**: Process control sensors (temperature, pressure, flow, level, vibration)
* **Security**: AES-128 encryption, key rotation, join authentication

### LoRaWAN Industrial Sensors
* Already covered in [LoRa spec](../lora/spec.md)
* Many industrial IoT deployments use LoRaWAN for remote monitoring
* Vibration sensors, tank level, environmental monitoring
