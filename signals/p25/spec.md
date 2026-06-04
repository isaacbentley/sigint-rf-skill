# Signal Specification: APCO P25 (Phase I & II)

Project 25 (P25) is the suite of standards for digital radio communications for use by federal, state/province, and local public safety agencies in North America to enable them to communicate with other agencies and mutual aid response teams in emergencies.

## 1. Physical Layer Parameters
* **Frequency Bands**: VHF (136-174 MHz), UHF (380-512 MHz), 700/800/900 MHz
* **Channel Bandwidth**: 12.5 kHz
* **Symbol Rate**: 4800 baud (9600 bps) for Phase I, 6000 baud (12000 bps) for Phase II

## 2. Phase 1 (Control & Voice)
* **Modulation**: C4FM (Continuous 4-Level FM) or CQPSK (Compatible QPSK).
* **Temporal Pattern**: Continuous while transmitting (FDMA). Control channels are 100% continuous.
* **Vocoder**: IMBE (Improved Multi-Band Excitation)

## 3. Phase 2 (Voice Only)
* **Modulation**: HDQPSK (Harmonized Differential Quadrature Phase Shift Keying) for Downlink, HCMP for Uplink.
* **Temporal Pattern**: 2-slot TDMA. Bursty (30 ms slots).
* **Vocoder**: AMBE+2 (Advanced Multi-Band Excitation)
* **Note**: Control channels in a Phase 2 trunking system *remain* Phase 1 C4FM for backwards compatibility.
