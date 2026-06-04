# Signal Specification: Wildlife Tracking & Telemetry 🦌📡

VHF telemetry collars, Argos satellite tags, Motus nanotags, and ICARUS. Radio-based systems for tracking animals from songbirds to whales.

---

## 1. VHF Telemetry Collars (Traditional)

The oldest and most widespread wildlife tracking method. Simple VHF beacons on animal collars, ear tags, or backpack transmitters.

### Physical Layer
* **Frequency**: 148–152 MHz (US, most common), 164–166 MHz, 216–220 MHz (some older systems)
* **Modulation**: CW beacon (carrier on/off) — just a pulsed carrier, no data
* **Pulse Rate**: 30–80 pulses/minute (varies by manufacturer, encodes activity level)
* **Pulse Width**: 15–30 ms
* **TX Power**: 2–50 mW (very low — battery life is critical)
* **Battery Life**: 6 months to 3+ years
* **Range**: 1–20 km (ground-level with Yagi antenna), 50+ km (aerial tracking from aircraft)

### How Tracking Works
* **No data telemetry** — just a pulsed carrier ("beep... beep... beep...")
* Researcher uses **directional Yagi antenna** to find bearing
* Multiple bearings from different positions = triangulated location
* **Mortality sensor**: Pulse rate doubles when collar hasn't moved for 4–8 hours
* **Activity sensor**: Mercury tip switch modulates pulse rate based on animal movement

### SDR Reception
```bash
# Receive VHF wildlife collar beacon
rtl_fm -f 150123000 -M fm -s 22050 -g 40 | aplay -r 22050 -f S16_LE
# Listen for periodic "beep" pulses — use headphones with Yagi antenna for direction-finding
```

---

## 2. Argos Satellite System

Satellite-based tracking using the Argos system — transmitters uplink to polar-orbiting satellites (NOAA POES, MetOp, SARAL). Used for marine mammals, sea turtles, large birds, polar bears.

### Physical Layer
* **Uplink Frequency**: 401.650 MHz (±30 kHz)
* **Modulation**: Phase modulation (PM) — actually bi-phase-L modulated data on carrier
* **Data Rate**: 400 bps (Argos-2/3), up to 4800 bps (Argos-4)
* **TX Power**: 250 mW–1.5 W
* **Message Length**: 256 bits (Argos-2), variable (Argos-3/4)
* **Repetition**: Transmits every 45–200 seconds
* **Burst Duration**: ~1 second

### Argos Location Methods
| Method | Accuracy | How |
|---|---|---|
| **Doppler (traditional)** | 150–1500 m | Satellite measures Doppler shift of 401.65 MHz carrier during pass |
| **GPS + Argos** | 5–10 m | Tag has GPS receiver, uploads positions via Argos |
| **Argos-4 (Kinéis)** | GPS-quality | Nanosatellite constellation, bidirectional link |

### Data Contents
* **PTT ID**: Platform Transmitter Terminal identifier (unique per tag)
* **Sensor Data**: Up to 32 bytes — typically temperature, depth (marine), activity, battery voltage
* **GPS positions**: If GPS-equipped tag

---

## 3. Motus Wildlife Tracking System

Automated VHF telemetry network — a grid of receiving stations that detect coded nanotags on small birds, bats, and insects. Operated by Birds Canada.

### Physical Layer
* **Frequency**: **166.380 MHz** (fixed, worldwide Motus frequency)
* **Modulation**: OOK — coded pulse train
* **Tag Type**: Lotek Nanotag (NTQB-series) or CTT LifeTag/PowerTag
* **Pulse Coding**: Unique burst interval pattern encodes tag ID (4 pulses, specific inter-pulse timing)
* **Burst Interval**: ~5–30 seconds between burst groups
* **Tag Weight**: 0.15–2.6 g (light enough for warblers and dragonflies!)
* **Battery Life**: 10 days to 3+ years (depends on size and burst rate)
* **TX Power**: ~1 mW

### Motus Network
* **1,600+ receiving stations** worldwide
* Each station: RTL-SDR or FUNcube Dongle + omni/Yagi antennas + Raspberry Pi/SensorGnome
* **Detection range**: 15–20 km per station
* **Data**: Tag detections uploaded to motus.org — free, open-access dataset
* **Key insight**: Many Motus stations **use RTL-SDR** as the receiver — this is an SDR-native wildlife tracking system

```bash
# Motus SensorGnome receiver stack
# RTL-SDR → vamp-alsa-host → Lotek pulse finder → tag database lookup
# All running on Raspberry Pi
# See: https://docs.motus.org/sensorgnome
```

---

## 4. ICARUS (International Cooperation for Animal Research Using Space)

An ISS-based animal tracking system developed by the Max Planck Institute.

### Physical Layer
* **Uplink**: 402.0 MHz (tag → ISS receiver, when ISS overhead)
* **Downlink**: ISS relays data to ground
* **Tag Weight**: 5 g (with GPS + accelerometer + magnetometer)
* **TX Power**: Very low — ISS in LEO provides short-range link
* **GPS**: On-tag GPS for position
* **Data**: GPS position, acceleration, magnetometer, temperature
* **Duty Cycle**: Tag transmits only during ISS passes (~4 min window)

---

## 5. Other Wildlife RF Systems

| System | Frequency | Method | Target Animals |
|---|---|---|---|
| **GPS-GSM collars** | Cellular (850/900/1800/1900 MHz) | SMS/GPRS data upload | Large mammals (elephants, wolves, bears) |
| **GPS-Iridium collars** | 1616–1626 MHz (Iridium L-band) | Satellite data upload | Polar/oceanic animals |
| **PIT tags (passive RFID)** | 125–134 kHz (LF RFID) | Inductive read at feeder/nest box | Birds at feeders, fish in streams |
| **Acoustic tags (marine)** | 69 kHz (ultrasonic, not RF) | Underwater acoustic receivers | Fish, sharks, rays |
| **Geolocation loggers** | None (light-level) | Store-and-retrieve, no transmission | Seabirds, shorebirds |
