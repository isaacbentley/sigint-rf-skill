# Recommended SDR Hardware 📡

This guide helps you choose a Software Defined Radio (SDR) receiver for use with the sigint-rf-skill tools. Devices are organized by experience level — pick the tier that matches your goals and budget.

---

## At a Glance

| Tier | Device | Price | Freq Range | RX / TX | ADC | Best For |
|---|---|---|---|---|---|---|
| 🟢 Entry | RTL-SDR | ~$30 | 24–1766 MHz | RX only | 8-bit | First SDR, learning, ADS-B, FM, ISM |
| 🟢 Entry | SDRplay RSP1B | ~$120 | 1 kHz – 2 GHz | RX only | 14-bit | Cleaner reception, built-in filtering |
| 🟡 Intermediate | HackRF One | ~$350 | 1 MHz – 6 GHz | RX + TX | 8-bit | Wide frequency range, transmit capability |
| 🔴 Advanced | Ettus USRP B210 | ~$1500+ | 70 MHz – 6 GHz | RX + TX | 12-bit | Research-grade, MIMO, high bandwidth |
| 🔵 Professional | Aaronia Spectran V6 | $$$$ | Up to 6+ GHz | RX | 16-bit | Real-time spectrum analysis, regulatory compliance |

---

## 🟢 Entry Tier

### RTL-SDR

The RTL-SDR is the most popular entry-level SDR in the world. Based on the Realtek RTL2832U DVB-T TV tuner chip, it was repurposed by the open-source community into a general-purpose wideband radio receiver.

**Why start here:**
- Extremely affordable (~$30)
- Massive community — thousands of tutorials, guides, and projects
- Natively supported by nearly every SDR tool (`rtl_sdr`, `rtl_power`, `rtl_433`, `dump1090`, GNU Radio, SDR#, SoapySDR)
- All tools in this repository work out of the box with RTL-SDR devices

**Specifications:**
- Frequency range: 24–1766 MHz (with R820T2 tuner)
- Sample rate: Up to 2.4 MSPS (stable), 3.2 MSPS (maximum)
- ADC resolution: 8-bit
- Interface: USB 2.0
- Bandwidth: ~2.4 MHz usable

**Limitations:**
- **No front-end filtering** — strong nearby transmitters (FM broadcast, cell towers) can overload the ADC and create false signals (intermodulation products, images). External bandpass filters help but add cost
- 8-bit ADC limits dynamic range (~48 dB) — weak signals next to strong ones may be lost in the noise floor
- No transmit capability

**Recommended accessories:**
- A basic dipole antenna kit (often included)
- An FM broadcast bandstop filter if you experience overload in the 88–108 MHz range
- A 1090 MHz bandpass filter for dedicated ADS-B aircraft tracking

**Quick capture command:**
```bash
rtl_sdr -f 433920000 -s 2048000 -g 30 capture.bin
```

---

### SDRplay RSP1B

The SDRplay RSP1B is an excellent step up from the RTL-SDR. Its standout feature is **built-in hardware preselection filter banks** that automatically engage based on your tuned frequency, dramatically reducing overload artifacts.

**Why choose this over an RTL-SDR:**
- **Hardware preselection filters** — automatically switches filter banks as you tune, preventing front-end overload without external filters
- **14-bit ADC** — significantly better dynamic range (~84 dB vs ~48 dB), meaning weak signals next to strong ones are still visible
- **10 MHz instantaneous bandwidth** — see more spectrum at once
- Covers HF frequencies down to 1 kHz — receive shortwave, amateur radio, and HF broadcasts that RTL-SDR cannot

**Specifications:**
- Frequency range: 1 kHz – 2 GHz
- Sample rate: Up to 10 MSPS
- ADC resolution: 14-bit
- Interface: USB 2.0
- Bandwidth: Up to 10 MHz usable

**Limitations:**
- Proprietary driver API (`libsdrplay_api`) — not as universally plug-and-play as RTL-SDR
- Smaller community compared to RTL-SDR, though still well-supported
- No transmit capability

**Software compatibility:**
- SDRuno or SDRconnect (SDRplay's official applications)
- GNU Radio (via `gr-soapy` or `gr-osmosdr` with SoapySDR plugin)
- SoapySDR (cross-platform abstraction layer)
- CubicSDR, SDR++, GQRX

**Using with this repository:**
To avoid the frustrating driver and plugin dependencies of SoapySDR on the command line, we recommend a simple "Bring Your Own Capture" approach for the SDRplay:
1. Open SDRplay's official, easy-to-install GUI (SDRconnect).
2. Tune to your target frequency and use the built-in "Record IQ" or "Baseband Recording" feature to save a `.wav` or `.raw` IQ file.
3. Feed that file directly into our triage pipeline:
```bash
# Triage the recorded file as usual
python3 tools/triage_iq.py --file capture.wav --rate 2048000
```

---

## 🟡 Intermediate Tier

### HackRF One

The HackRF One is a half-duplex transceiver covering an extremely wide frequency range. Designed by Great Scott Gadgets as an open-source hardware project, it is the go-to device for security research, protocol reverse engineering, and RF experimentation.

**Why choose this:**
- **Transmit and receive** — replay signals, test protocols, build custom transmitters
- **1 MHz to 6 GHz** frequency range — covers nearly everything from HF to WiFi/5 GHz
- **20 MHz instantaneous bandwidth** — wide enough for most protocols
- Fully open-source hardware and firmware
- Supported by virtually all SDR software

**Specifications:**
- Frequency range: 1 MHz – 6 GHz
- Sample rate: Up to 20 MSPS
- ADC/DAC resolution: 8-bit
- Interface: USB 2.0 (High Speed)
- Bandwidth: Up to 20 MHz usable
- Half-duplex (cannot TX and RX simultaneously)

**Limitations:**
- 8-bit ADC — same dynamic range limitation as the RTL-SDR
- No front-end filtering — susceptible to overload in dense RF environments
- Half-duplex only — for full-duplex (simultaneous TX/RX), you need two units or a different device
- More expensive than receive-only alternatives

**Quick capture command:**
```bash
hackrf_transfer -r capture.bin -f 915000000 -s 2000000 -l 24 -g 30
```

---

## 🔴 Advanced Tier

### Ettus USRP B210

The Ettus USRP (Universal Software Radio Peripheral) B210 is a research-grade SDR platform widely used in academia, government, and industry. It offers high bandwidth, MIMO capability, and tight integration with the UHD (USRP Hardware Driver) ecosystem.

**Why choose this:**
- **Full-duplex TX/RX** with 2x2 MIMO — two independent RF chains
- **56 MHz instantaneous bandwidth** — capture entire bands at once
- **12-bit ADC/DAC** with excellent phase noise and clock stability
- Tight integration with GNU Radio, MATLAB, LabVIEW, and custom C++/Python applications
- GPS-disciplined oscillator support for precision timing

**Specifications:**
- Frequency range: 70 MHz – 6 GHz
- Sample rate: Up to 61.44 MSPS
- ADC/DAC resolution: 12-bit
- Interface: USB 3.0
- Bandwidth: Up to 56 MHz usable
- Full-duplex, 2x2 MIMO

**Limitations:**
- Expensive (~$1500+)
- Requires USB 3.0 for full bandwidth
- Steeper learning curve — primarily driven through UHD API or GNU Radio
- Significant host CPU usage at high sample rates

---

## 🔵 Professional Tier

### Aaronia Spectran V6

The Aaronia Spectran V6 series represents the professional end of the spectrum. These are real-time spectrum analyzers with instantaneous bandwidths up to 245 MHz, used for regulatory compliance testing, interference hunting, and advanced SIGINT operations.

**Why choose this:**
- **Real-time bandwidth up to 245 MHz** — see entire bands without sweeping
- **16-bit ADC** with exceptional dynamic range
- **Real-time spectrum analysis** — no gaps in spectral coverage
- Integrated with Aaronia RTSA Suite Pro for visualization, recording, and analysis
- Remote operation capability via network API

**Specifications:**
- Frequency range: Up to 6 GHz+ (model dependent)
- Real-time bandwidth: Up to 245 MHz
- ADC resolution: 16-bit
- Interface: USB 3.0 / Network
- Professional-grade calibration and sensitivity

**Limitations:**
- Professional pricing (several thousand dollars and up)
- Proprietary software ecosystem (RTSA Suite)
- Overkill for casual hobbyist use
- A license is required for using the remote configuration API endpoint — see [Aaronia Software Licence](https://aaronia.com/en/software-licence-remote-config) for details

---

## Choosing Your First SDR

```
┌─────────────────────────────────┐
│   What's your budget?           │
└────────┬────────────────────────┘
         │
    ┌────▼─────┐    ┌──────────────────────────────────────┐
    │  < $50   ├───►│  RTL-SDR                             │
    └──────────┘    │  Best bang for buck, huge community   │
                    └──────────────────────────────────────┘
    ┌──────────┐    ┌──────────────────────────────────────┐
    │ $50-$150 ├───►│  SDRplay RSP1B                       │
    └──────────┘    │  Built-in filters, 14-bit, less noise│
                    └──────────────────────────────────────┘
    ┌──────────┐    ┌──────────────────────────────────────┐
    │ $150-$500├───►│  HackRF One                          │
    └──────────┘    │  Need to transmit? This is it.       │
                    └──────────────────────────────────────┘
    ┌──────────┐    ┌──────────────────────────────────────┐
    │  $1000+  ├───►│  USRP B210 / Aaronia Spectran        │
    └──────────┘    │  Research or professional use         │
                    └──────────────────────────────────────┘
```

### Our Recommendation

**If you're just getting started**, grab an **RTL-SDR** (~$30). It works with every tool in this repository out of the box, has the largest community for troubleshooting, and will let you receive ADS-B aircraft, FM radio, weather stations, tire pressure sensors, ISM devices, and much more.

**If you want a better experience** and are willing to spend a little more, the **SDRplay RSP1B** (~$120) is a significant upgrade. The built-in preselection filters and 14-bit ADC mean cleaner signals with less frustration — you'll spend more time analyzing real signals and less time chasing interference artifacts.

---

## Antenna Tips

The antenna is just as important as the SDR itself. A few quick tips:

- **Use the right antenna for the frequency** — a wideband discone or telescopic dipole works for general scanning, but a tuned antenna for a specific band (e.g., a 1090 MHz quarter-wave for ADS-B) will dramatically improve reception
- **Height matters** — getting the antenna higher (on a roof, out a window, on a mast) improves line-of-sight range significantly
- **Cable quality matters at higher frequencies** — use low-loss coax (e.g., LMR-400) for long cable runs, especially above 1 GHz
- **Start with what's included** — most SDR kits come with a basic antenna. Use it to get started, then upgrade as you learn what bands you care about
