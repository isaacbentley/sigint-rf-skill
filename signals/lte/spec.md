# Signal Specification: LTE (4G Cellular)

Long-Term Evolution (LTE) is the global standard for 4G wireless broadband. It utilizes a highly structured, scheduled radio frame and relies on OFDM for the downlink.

## 1. Physical Layer Parameters
* **Frequency Bands**: Vast range of FDD and TDD bands from 700 MHz up to 3.5 GHz.
* **Channel Bandwidth**: 1.4 MHz, 3 MHz, 5 MHz, 10 MHz, 15 MHz, 20 MHz
* **Modulation (Downlink)**: OFDMA (Orthogonal Frequency-Division Multiple Access)
* **Modulation (Uplink)**: SC-FDMA (Single-Carrier FDMA) to reduce PAPR for mobile devices.
* **Subcarrier Modulation**: QPSK, 16-QAM, 64-QAM, 256-QAM
* **Subcarrier Spacing**: 15 kHz

## 2. Synchronization & Pilots
* **Radio Frame**: 10 ms long, divided into 10 subframes (1 ms each).
* **Primary Synchronization Signal (PSS)**: Transmitted in the center 62 subcarriers. Uses a Zadoff-Chu sequence to allow the device to gain subframe timing and determine the physical layer identity (0-2).
* **Secondary Synchronization Signal (SSS)**: Transmitted adjacent to the PSS. Uses interleaved m-sequences to determine the physical layer cell identity group (0-167).
* **Cell-Specific Reference Signals (CRS)**: Scattered pilots used for channel estimation and equalization.
