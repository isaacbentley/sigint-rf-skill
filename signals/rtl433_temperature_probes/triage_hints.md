# Triage Hints: Temperature & Humidity Probes (rtl_433) 🌡️

## Spectral Indicators
* **Center Frequency**: 433.92 MHz (primary), some models on 915 MHz (US)
* **Occupied Bandwidth**: 10–40 kHz (OOK dominant)
* **Modulation**: Mostly OOK with Manchester or PWM encoding
* **SNR**: 8–20 dB (lower power than weather stations)

## Temporal Indicators
* **PAPR**: 3–6 dB (OOK)
* **Duty Cycle**: < 0.5% (very infrequent transmissions to save battery)
* **Burst Duration**: 10–40 ms (shorter packets than weather stations — fewer data fields)
* **Reporting Interval**: 30–120 seconds (varies by model; some power-saving models go up to 300s)
* **Packet Repetition**: Most models send 2–5 identical packets per burst for redundancy

## Key Identification Heuristic
> **If you see short OOK bursts at 433.92 MHz repeating every 30–120 seconds with only 2–4 data fields (temp, humidity, channel, battery), and the packet is notably shorter than a weather station, it's likely a temp probe.** The shorter payload (no wind/rain data) is the distinguishing feature vs. weather stations.

## Common Models (rtl_433 supported)
* **Inkbird IBS-TH1/TH2**: BLE + 433 MHz, OOK, temp + humidity
* **ThermoPro TX-2/TP-60**: OOK, 60-second interval, channel selector
* **Govee H5075/H5179**: 433 MHz + BLE, OOK/FSK
* **Ambient Weather WH31E**: 433 MHz, FSK, multi-channel
* **Acurite 06002M**: 433 MHz, OOK, 16-second interval (fast)

## Quick Decode
```bash
# Scan for temperature probes with rtl_433
rtl_433 -f 433920000 -R 40 -R 41 -R 42 -R 55 -R 91 -F json
# Or auto-detect all protocols
rtl_433 -f 433920000 -F json | grep -i "temperature"
```

## Differentiation
| Confusable Signal | Key Differentiator |
|---|---|
| **Weather Stations** | Weather stations have longer packets (40–80 ms), more fields (wind, rain, UV), multi-channel |
| **TPMS** | TPMS is FSK at higher baud rate with specific sync word, event + periodic timing |
| **Doorbells** | Doorbells are event-triggered only (no periodic reporting), only 12–24 bits |
| **Security Sensors** | Security sensors have supervisory check-in every 60–90 min, include alarm/tamper flags |
| **Pool Thermometers** | Same family — typically distinguished by sensor ID range and model-specific encoding |

## Confidence Checklist
- [ ] Frequency is 433.92 MHz (or 915 MHz US)?
- [ ] OOK modulation with low duty cycle?
- [ ] Burst duration 10–40 ms (shorter than weather station)?
- [ ] Periodic reporting at 30–120 second intervals?
- [ ] Payload contains only temp (and optionally humidity, channel, battery)?
- [ ] rtl_433 decodes with a known temperature sensor protocol?

