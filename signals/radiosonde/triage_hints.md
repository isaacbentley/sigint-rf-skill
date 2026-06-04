# Triage Hints: Radiosondes — Weather Balloon Telemetry 🎈🌡️

## Spectral Indicators
* **Center Frequency**: 400–406 MHz — narrow range, **very distinctive band** (between UHF amateur 70cm and NOAA weather satellite)
* **Occupied Bandwidth**: ~12 kHz (RS41), ~6 kHz (DFM)
* **Modulation**: GFSK — clean narrow FM with smooth Gaussian transitions
* **Signal Strength**: Strong (60 mW from 30+ km altitude = line-of-sight to ~500 km radius)

## Temporal Indicators
* **Frame Rate**: Exactly 1 Hz (1 frame/second) — very regular
* **Duration**: 90–120 minutes continuous (entire flight)
* **Launch Times**: ~11:15Z and ~23:15Z daily (US NWS)
* **Frequency Drift**: Slight downward drift as sonde cools at altitude (< 5 kHz over flight)

## Key Identification Heuristic
> **If you see a steady GFSK signal at 400–406 MHz transmitting at exactly 1 Hz for 90+ minutes, it's a radiosonde.** Nothing else lives in this narrow band with this behavior. The signal appears suddenly (launch), strengthens (ascent), then weakens and Doppler-shifts (descent away from you).

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **NOAA weather satellite (APT)** | NOAA is at 137 MHz, not 400 MHz. Different band entirely. |
| **Satellite downlinks (Argos)** | Argos uplink is 401.65 MHz but much shorter bursts (1s), not continuous |
| **P25 / LMR at UHF** | P25 is 450+ MHz and uses 4FSK with TDMA, not continuous 1 Hz telemetry |
| **GPS L1** | GPS is 1575.42 MHz — different band |
| **Meteor scatter** | Meteor scatter is HF/VHF, not UHF |
