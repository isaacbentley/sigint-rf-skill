# Triage Hints: GPS & GNSS — Satellite Navigation Signals 🛰️📍

These hints help identify GNSS signals from spectral observations, waterfall displays, and statistical reports.

---

## 🔍 Spectral Indicators

### 1. Frequency Bands
GNSS signals occupy well-defined L-band allocations:

| Signal | Center Frequency | What You'll See |
|---|---|---|
| **GPS L1 / Galileo E1 / BeiDou B1C** | 1575.42 MHz | All three constellations overlap here — primary detection target |
| **BeiDou B1I** | 1561.098 MHz | ~14 MHz below GPS L1, 4 MHz wide |
| **GLONASS L1** | 1598.0625–1605.375 MHz | FDMA "comb" of 14 carriers spaced 562.5 kHz — distinctive! |
| **GPS L2** | 1227.60 MHz | Secondary GPS frequency |
| **GPS L5 / Galileo E5a** | 1176.45 MHz | Wideband (20 MHz) modern signals |
| **Galileo E5b** | 1207.14 MHz | |

### 2. Bandwidth
* **GPS L1 C/A**: 2.046 MHz null-to-null (main lobe), but ~20 MHz to capture side lobes
* **Galileo E1 BOC(1,1)**: 4.092 MHz — split spectrum with **notch at center** (BOC signature)
* **GLONASS L1**: Each channel is 1.022 MHz wide, but the full constellation spans ~8 MHz
* **GPS L5 / E5a**: 20.46 MHz — very wideband

### 3. Power Spectral Density
* **GPS L1 C/A**: DSSS — appears as a **subtle ~1–2 dB hump** across 2 MHz, barely distinguishable from noise
* **Galileo E1 BOC(1,1)**: Distinctive **double-humped** spectrum with a null at 1575.42 MHz (the BOC subcarrier splits the main lobe)
* **GLONASS L1 FDMA**: Multiple discrete carriers spaced 562.5 kHz apart — looks like a "picket fence" or comb

### 4. Special Hardware Requirement: Bias-Tee
Most SDRs (RTL-SDR v3/v4, HackRF) cannot receive GPS effectively with a passive antenna. You must use an **active GPS patch antenna** requiring 3.3V or 5V DC via bias-tee.
* RTL-SDR blog v3/v4: Enable bias-tee in software before capturing
* HackRF: Enable antenna port power (`hackrf_transfer -p 1`)

---

## ⏱ Temporal Indicators

### 1. Signal Persistence
* GNSS signals are **continuous** — transmitted 24/7/365. There is no burst or duty cycle structure visible.
* If you see a "GNSS-like" signal that turns on and off, it's likely a **pseudolite**, **jammer**, or **spoofer**, not a real satellite.

### 2. Code Periodicity
* GPS L1 C/A: PRN code repeats every **1 ms** (1023 chips at 1.023 Mcps)
* After correlation, you can detect 1 kHz periodicity in the despread signal
* Navigation data bit boundaries every **20 ms** (50 bps)

### 3. Doppler Characteristics
* GPS (MEO, ~20,200 km altitude): Doppler ≤ ±5 kHz, changes slowly (minutes)
* GLONASS (MEO, ~19,100 km): Similar Doppler range
* All GNSS Doppler is slow and predictable — unlike LEO satellites (Iridium) which have rapid Doppler

---

## 🎯 Key Identification Heuristic

> **GNSS signals are invisible on a normal spectrum analyzer.** If you see a very subtle (~1–2 dB) broadband hump centered at exactly 1575.42 MHz that is present 24/7 and doesn't change with time, you're looking at the combined GPS/Galileo/BeiDou L1 signal. The definitive proof is **correlation gain**: feed the IQ data into GNSS-SDR and if it acquires satellites, it's GNSS. No other signal at 1575 MHz behaves this way — everything else (DME, TACAN, Iridium) is pulsed, narrowband, or at different frequencies.

> **GLONASS is the easiest to visually identify** because its FDMA structure creates a visible comb of ~14 discrete carriers between 1598–1606 MHz, each ~1 MHz wide and spaced 562.5 kHz apart.

> **If you can plainly *see* a GPS signal on a spectrum analyzer without averaging or correlation processing, something is wrong** — it's either a spoofer, a simulator, local RFI, or not GPS.

---

## 🔄 Differentiation

| Confusable Signal | Key Differentiator |
|---|---|
| **DME/TACAN (960–1215 MHz)** | DME is pulsed (3.5 µs pulse pairs), lower frequency. TACAN at 1025–1150 MHz. Neither overlaps GPS L1 at 1575 MHz. |
| **Iridium (1616–1626.5 MHz)** | Iridium is 40+ MHz above GPS L1. Visible TDMA bursts with rapid LEO Doppler. Easy to distinguish. |
| **Inmarsat / L-band SATCOM (~1530–1545 MHz)** | Inmarsat signals are narrow, continuous, and clearly visible above the noise floor. ~30 MHz below GPS L1. |
| **ATC radar / SSR (1030/1090 MHz)** | Much lower frequency, pulsed, high power. Not in GNSS bands. |
| **Galileo E1 vs GPS L1** | Same center frequency (1575.42 MHz). BOC(1,1) has split spectrum; GPS BPSK(1) has single main lobe. Need correlation to distinguish. |
| **GPS spoofing / meaconing** | Spoofed signals are typically **much stronger** than real GPS (−130 dBm). If GNSS signal is visible above noise floor on spectrum analyzer without correlation → suspicious. |
| **GLONASS FDMA vs narrowband interference** | GLONASS shows a regular comb with exact 562.5 kHz spacing. Random RFI won't have this precise periodicity. |
| **Wideband noise floor rise** | GPS can look like a noise floor increase. Key: the hump is exactly 2 MHz wide, centered on 1575.42 MHz, and persistent. Broadband interference is usually wider or asymmetric. |
| **Local RFI (USB 3.0, laptop chargers)** | Cheap electronics radiating near 1.5 GHz produce visible spikes at 1575 MHz. These are tall, narrow spikes — not a smooth 2 MHz hump. |

---

## ✅ Confidence Checklist

Use this checklist to assess confidence that an observed signal is GNSS:

- [ ] **Center frequency** matches a known GNSS band (1575.42, 1227.60, 1176.45, 1561.098, or 1602+k×0.5625 MHz)
- [ ] **Bandwidth** consistent with GNSS (2 MHz for L1 C/A, 4 MHz for BOC, 20 MHz for L5/E5)
- [ ] **Signal is at or below noise floor** — no clear spectral peak visible without averaging
- [ ] **Signal is continuous** (24/7) — no burst structure, no on/off keying
- [ ] **Active GPS antenna with bias-tee** is in use (required for meaningful reception)
- [ ] **GLONASS FDMA comb** visible at 1598–1606 MHz (if L1 band is captured with sufficient bandwidth)
- [ ] **Correlation test**: GNSS-SDR or SoftGNSS successfully acquires ≥1 satellite PRN from the IQ capture
- [ ] **Doppler** is slow (< ±5 kHz) and consistent with MEO satellite geometry
- [ ] **No anomalous signal strength** — real GNSS is always weak (~−130 dBm). If signal is strong enough to clearly see on waterfall, suspect spoofing/pseudolite
