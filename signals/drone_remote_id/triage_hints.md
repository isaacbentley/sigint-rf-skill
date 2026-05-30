# Triage Hints: Drone Remote ID (Wi-Fi & Bluetooth) 🛩️📡

## How to Detect Remote ID

### BLE Method (Easiest)
1. Open **nRF Connect** (Android) or **OpenDroneID** app
2. Look for BLE advertising with **Service UUID 0xFFFA**
3. Non-connectable advertising (`ADV_NONCONN_IND`)
4. Payload contains 25-byte Open Drone ID messages
5. Update rate ≥ 1 Hz

### Wi-Fi Method
1. Put Wi-Fi adapter in **monitor mode** on **channel 6** (2.437 GHz for NAN)
2. Look for **Action frames** with OUI `FA:0B:BC`
3. Or Beacon frames with Vendor Specific IE containing same OUI
4. Filter in Wireshark: `wlan.action.vendor_specific.oui == fa:0b:bc`

### DJI Legacy
1. Monitor DJI's Wi-Fi link (2.4 / 5.8 GHz)
2. Look for Vendor Specific IE with OUI `26:37:12`
3. Use `gr-droneid` to decode from IQ capture

---

## Identification from SDR IQ Capture

> **Remote ID is NOT a distinct SDR signal** — it rides on top of standard Wi-Fi or BLE. You won't see a unique spectral signature. Instead:
> - **BLE RID**: Looks like any other BLE advertising — 1 MHz GFSK burst at 2402/2426/2480 MHz
> - **Wi-Fi RID**: Looks like standard 802.11 — 20 MHz OFDM at 2.437 GHz
>
> **The identification happens at the protocol layer, not the PHY layer.** You need to decode the frames and inspect OUI/UUID fields.

---

## Differentiation

| Confusable | Key Differentiator |
|---|---|
| **DJI OcuSync video link** | OcuSync is wideband (10-40 MHz) OFDM with Zadoff-Chu preamble; RID is standard 802.11 or BLE |
| **Regular BLE advertising** | RID uses UUID `0xFFFA` and `ADV_NONCONN_IND`; regular BLE uses other UUIDs |
| **Regular Wi-Fi beacons** | RID uses OUI `FA:0B:BC` in Action frames or Vendor IE |
| **ADS-B** | ADS-B is 1090 MHz PPM — completely different frequency and modulation |

---

## When to Check for Remote ID

You should scan for Remote ID whenever you:
- See a drone visually and want to identify it
- Detect DJI OcuSync or FPV signals and want the drone's registration info
- Are conducting RF CTF reconnaissance near a drone operating area
- Want to locate the **operator** (System message includes operator GPS position)

---

## Confidence Checklist

- [ ] BLE: Service UUID = `0xFFFA` in advertising data?
- [ ] Wi-Fi: OUI = `FA:0B:BC` in Action/Beacon Vendor IE?
- [ ] Message payload is 25 bytes (single) or multiple of 25 (pack)?
- [ ] Message Type field (bits 7-4) is 0x0–0x5 or 0xF?
- [ ] Location message contains valid lat/lon (not 0.0/0.0)?
- [ ] Update rate ≥ 1 Hz?
- [ ] Basic ID contains 20-character serial number or CAA registration?
