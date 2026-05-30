# Signal Specification: Meshtastic & mesh-core Decryption Guide

This guide details the physical layer specifications, protocol details, and packet decryption methods for Meshtastic mesh network communications.

---

## 1. Physical Layer Parameters

* **Frequency Bands**:
  * North America: `915 MHz`
  * Europe: `868 MHz` or `433 MHz`
  * New Zealand/Australia: `915 MHz`
* **Bandwidths**: Standard LoRa bandwidths (typically `125 kHz`, `250 kHz`, or `500 kHz`).
* **Modulation**: LoRa CSS (Chirp Spread Spectrum).
* **Common Settings**:
  * **Short Range / Fast**: SF7, 250 kHz bandwidth.
  * **Long Range / Fast (Default)**: SF9, 125 kHz bandwidth.
  * **Long Range / Slow**: SF11, 125 kHz bandwidth.
  * **Very Long Range / Slow**: SF12, 31.25 kHz bandwidth.

---

## 2. Synchronization & Frame Geometry

Meshtastic packets follow the standard LoRa frame layout:
```
| Preamble (8 Up-Chirps) | Sync Word (0x2B) | SFD (2.25 Down-Chirps) | Header | Encrypted Payload | CRC |
```
* **Sync Word**: Standard Meshtastic LoRa sync word is **`0x2B`** (or `43` in decimal) to separate it from default Semtech sync words (`0x12` or `0x34`).

---

## 3. Symmetric Decryption (Default Public Channel)

When triaging or eavesdropping on a public Meshtastic mesh, the primary channel (e.g. `LongFast`) uses a hardcoded default key:

1. **Default Pre-Shared Key (PSK)**:
   * Base64: `"AQ=="`
   * Hex Shorthand: `0x01`
2. **Key Expansion**:
   * The single byte is expanded by the firmware into a full 16-byte AES-128 key:
     `d4 f1 bb 3a 20 29 07 59 f0 bc ff ab cf 4e 69 01`
3. **Decryption Recipe (AES-128-CTR)**:
   * **Cipher**: AES-128 in CTR (Counter) mode. No padding is required.
   * **Initialization Vector (IV/Nonce)**: A 16-byte block constructed from packet metadata headers:
     `Packet ID (4 bytes, little-endian) + Sender Node ID (4 bytes, little-endian) + 8 bytes of zero (0x00)`
   * **Protobuf Presentation**:
     Decrypted payload bytes match the Google Protocol Buffer structure defined by the `meshtastic` protobuf schema (such as `MeshPacket`).
