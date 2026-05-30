# Signal Specification: Bluetooth Classic & BLE (2.4 GHz) 📶

Bluetooth Classic (BR/EDR) and Bluetooth Low Energy (BLE) — phones, headphones, keyboards, fitness trackers, beacons, IoT sensors.

---

## 1. Physical Layer Parameters

* **Frequency Band**: 2.402–2.480 GHz (ISM, 79 channels × 1 MHz for Classic, 40 channels × 2 MHz for BLE)
* **Modulation**:
  - **Bluetooth Classic (BR)**: GFSK, 1 Mbps, ±150–175 kHz deviation
  - **Bluetooth Classic (EDR 2 Mbps)**: π/4-DQPSK
  - **Bluetooth Classic (EDR 3 Mbps)**: 8DPSK
  - **BLE (1M PHY)**: GFSK, 1 Mbps, ±250 kHz deviation
  - **BLE (2M PHY)**: GFSK, 2 Mbps
  - **BLE (Coded PHY)**: GFSK, 500 kbps or 125 kbps (long range)
* **Channel Bandwidth**: 1 MHz (Classic), 2 MHz (BLE)
* **TX Power**: -20 to +20 dBm (Class 1–3)
* **Range**: 1–100 m (Class-dependent)

---

## 2. Frequency Hopping

### Bluetooth Classic
* **79 channels** (2402–2480 MHz, 1 MHz spacing)
* **1600 hops/second** (625 µs per slot)
* Adaptive Frequency Hopping (AFH) avoids Wi-Fi interference
* **Very hard to receive with SDR** — requires wideband capture or synchronized hopping

### BLE
* **40 channels** (2 MHz spacing)
* **3 advertising channels**: 37 (2402 MHz), 38 (2426 MHz), 39 (2480 MHz)
* **37 data channels**: 0–36 (remaining frequencies)
* Advertising on fixed channels = **easily capturable by SDR**

---

## 3. BLE Advertising (SDR-Accessible)

BLE advertising is the most practical Bluetooth signal to capture with SDR because it uses **fixed, known frequencies**.

### Advertising PDU (on channels 37/38/39)
```
| Preamble (1 byte) | Access Address (4 bytes = 0x8E89BED6) | PDU Header (2 bytes) | AdvA (6 bytes MAC) | AdvData (0-31 bytes) | CRC (3 bytes) |
```

### Advertising Types
| Type | Name | Description |
|---|---|---|
| ADV_IND | Connectable undirected | General advertisement (most common) |
| ADV_DIRECT_IND | Connectable directed | Targeted to specific device |
| ADV_NONCONN_IND | Non-connectable | Beacons (iBeacon, Eddystone) |
| ADV_SCAN_IND | Scannable | Responds to scan requests with extra data |

---

## 4. Tools

| Tool | Capability |
|---|---|
| **Ubertooth One** | Dedicated Bluetooth sniffer — captures Classic and BLE |
| **nRF52840 Dongle** | BLE sniffer with Wireshark integration (nRF Sniffer) |
| **HackRF + BTLE** | Receive BLE advertising on fixed channels |
| **RTL-SDR** | Can receive 2.4 GHz with modified direct sampling, but very limited |
| **btlejack** | BLE connection hijacking |
| **GATTacker** | BLE MITM attack tool |
| **Wireshark** | Full BLE/HCI protocol dissection |
| **hcitool / bluetoothctl** | Linux BT stack tools |

```bash
# Ubertooth BLE advertising capture
ubertooth-btle -f -c /tmp/ble.pcap

# nRF Sniffer for Wireshark
# Install nRF Sniffer firmware on nRF52840 dongle
# Open Wireshark → select nRF Sniffer interface → capture

# HackRF BLE (limited — single channel)
# https://github.com/JiaoXianjun/BTLE
btle_rx -c 37 -g 20
```

---

## 5. Security Notes

* **BLE Legacy Pairing**: Temporary Key (TK) = 0 for Just Works → trivially eavesdropped
* **BLE Secure Connections (4.2+)**: ECDH key exchange, resistant to passive eavesdropping
* **MAC Randomization**: Modern phones randomize BLE advertising MAC addresses (RPA)
* **Tracking**: Despite RPA, device fingerprinting via advertising payload timing and content is possible
