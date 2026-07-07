# Signal Specification: Wi-Fi (IEEE 802.11a/g/n/ac/ax/be) 📶

The 802.11 family — laptops, phones, APs, IoT. Almost always demodulated with a
NIC in **monitor mode** (Wireshark/airodump) rather than from raw IQ; SDR IQ work
is reserved for PHY research, preamble detection, and interference hunting.

---

## 1. Physical Layer Parameters

* **Frequency Bands**: 2.4 GHz (ch 1–14), 5 GHz (U-NII 1–4), 6 GHz (Wi-Fi 6E/7, U-NII 5–8)
* **Modulation**: OFDM (data subcarriers BPSK → 16/64/256-QAM; 1024-QAM in ax; 4096-QAM in be)
* **Channel Bandwidth**: 20 MHz base, bonded to 40 / 80 / 160 MHz (320 MHz in 802.11be)
* **Subcarrier spacing**: 312.5 kHz (20 MHz / 64-pt FFT) for a/g/n/ac; 78.125 kHz (4× denser) for ax/be
* **Standards**:
  - **802.11a** — 5 GHz, 20 MHz OFDM, ≤54 Mbps (64-FFT: 48 data + 4 pilot subcarriers)
  - **802.11g** — 2.4 GHz, same OFDM PHY as 11a
  - **802.11n (HT)** — 2.4/5 GHz, 20/40 MHz, MIMO (≤4 streams)
  - **802.11ac (VHT)** — 5 GHz, up to 160 MHz, ≤8 streams, 256-QAM
  - **802.11ax (HE, Wi-Fi 6/6E)** — 2.4/5/6 GHz, OFDMA + RU allocation, 1024-QAM
  - **802.11be (EHT, Wi-Fi 7)** — adds 6 GHz 320 MHz, 4096-QAM, multi-link
* **TX Power**: ~15–30 dBm (region/band dependent)

---

## 2. Synchronization & Frame Geometry

Every 802.11 OFDM frame opens with a **legacy preamble** (backward compatible across
a/g/n/ac/ax), which is what makes Wi-Fi detectable and time-alignable from raw IQ:

```
| L-STF (8 µs) | L-LTF (8 µs) | L-SIG (4 µs) | [HT/VHT/HE-SIG…] | DATA symbols (4 µs each) |
```

* **L-STF (Short Training Field)** — 10 repetitions of a 0.8 µs pattern (used for packet
  detection / AGC / coarse CFO). Autocorrelation peaks at a **0.8 µs** lag (16 samples @ 20 MSPS).
* **L-LTF (Long Training Field)** — 1.6 µs guard + 2 × 3.2 µs symbols (channel estimation /
  fine sync). Autocorrelation peaks at a **3.2 µs** lag (64 samples @ 20 MSPS).
* **OFDM symbol**: 3.2 µs useful + 0.8 µs cyclic prefix = **4.0 µs** (long GI).
* **Beacons**: broadcast every **100 TU = 102.4 ms** by default — the most reliable
  periodic Wi-Fi fingerprint on a waterfall.

---

## 3. Demodulation Pipeline (Step-by-Step)

From raw IQ (research path — for actual traffic use a monitor-mode NIC):
1. **Packet detection**: L-STF auto-correlation (delay-and-correlate at 0.8 µs) → power/plateau flag.
2. **CFO estimation & correction**: phase slope across L-STF/L-LTF repetitions.
3. **Timing / symbol sync**: L-LTF cross-correlation locates the FFT window.
4. **Channel estimation**: from the two L-LTF symbols; equalize per subcarrier.
5. **FFT per symbol** (64-pt @ 20 MHz), pilot tracking on subcarriers ±7, ±21.
6. **Demap & decode**: QAM demap → deinterleave → Viterbi (BCC) or LDPC → descramble → MPDU.

`explainable_demod.py --mode ofdm --ofdm-profile wifi` sets FFT/CP for the 20 MHz legacy PHY.

---

## 4. Tools

| Tool | Capability |
|---|---|
| **Monitor-mode NIC + Wireshark / tcpdump** | The practical path — full 802.11 dissection from a card in monitor mode |
| **airodump-ng / aircrack-ng suite** | Survey, handshake capture, WEP/WPA cracking |
| **Kismet** | Wardriving, AP/client discovery, logging |
| **gr-ieee802-11 (bastibl)** | GNU Radio OOT — true IQ PHY demod of 802.11a/g/n (needs ≥20 MHz BW) |
| **nexmon** | Broadcom firmware patch for monitor mode + CSI extraction |
| **hcxdumptool / hashcat** | PMKID capture and offline WPA2 cracking |

```bash
# Monitor mode + capture (practical)
sudo airmon-ng start wlan0
sudo airodump-ng wlan0mon

# IQ PHY demod in GNU Radio (research) — needs HackRF/USRP @ 20 MHz
# https://github.com/bastibl/gr-ieee802-11
```

> **SDR note**: 20 MHz occupied bandwidth means RTL-SDR (≤2.4 MHz) **cannot** capture a
> full channel — use HackRF (20 MHz), USRP, or a monitor-mode NIC.

---

## 5. Security Notes

* **WEP**: broken (RC4 IV reuse) — recoverable in minutes.
* **WPA2-PSK**: capture the 4-way handshake (or a single **PMKID**) → offline dictionary/GPU
  attack with hashcat. Force a handshake with a deauth (pre-802.11w).
* **WPA3-SAE (Dragonfly)**: resistant to offline attack, but early implementations had
  **Dragonblood** side-channel/downgrade issues.
* **WPS**: PIN brute force (Reaver) and **Pixie Dust** offline attacks on weak nonces.
* **Management frames**: deauth/disassoc are unauthenticated unless **802.11w (PMF)** is on →
  enables deauth floods and **evil-twin / rogue-AP** attacks.
* **KRACK**: key-reinstallation against the WPA2 4-way handshake (patched in modern stacks).
