# Triage Hints: HF RFID & NFC (13.56 MHz) 📱💳

## Important: Near-Field Only
> ⚠️ **13.56 MHz is within HackRF's tuning range** but NFC operates via magnetic near-field coupling. You must be within centimeters with a specialized loop antenna. Standard SDR whip/discone antennas will NOT receive NFC signals. Use a Proxmark3 or NFC reader instead.

## Identification (with Proxmark3 / NFC reader)

### From ATQA + SAK (ISO 14443A)
| ATQA | SAK | Tag Type |
|---|---|---|
| 0x0004 | 0x08 | MIFARE Classic 1K |
| 0x0002 | 0x18 | MIFARE Classic 4K |
| 0x0044 | 0x00 | MIFARE Ultralight / NTAG |
| 0x0344 | 0x20 | MIFARE DESFire |
| 0x0004 | 0x20 | JCOP / EMV bank card |
| 0x0044 | 0x04 | MIFARE Mini |

### From UID Length
* **4-byte UID**: MIFARE Classic, some legacy cards (NUID — not truly unique)
* **7-byte UID**: MIFARE Ultralight, NTAG, DESFire, most modern cards
* **10-byte UID**: Rare, triple-size UID cascade

## Differentiation
| Confusable | Key Differentiator |
|---|---|
| **LF RFID (125 kHz)** | Different frequency, different readers, different tools |
| **UHF RFID (860–960 MHz)** | Radiated RF, much longer range, EPC Gen2 protocol |
| **Bluetooth / BLE (2.4 GHz)** | Completely different frequency and protocol |
| **Contactless power transfer (Qi)** | ~100-200 kHz, power only, no data modulation |
