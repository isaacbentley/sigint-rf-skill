# Signal Specification: ATSC 3.0

ATSC 3.0 is the next-generation terrestrial television broadcast standard. Unlike ATSC 1.0 (which used 8VSB single-carrier modulation), ATSC 3.0 is built on COFDM (Coded Orthogonal Frequency-Division Multiplexing) to provide robust mobile reception and higher data rates for 4K video.

## 1. Physical Layer Parameters
* **Frequency Bands**: UHF (470 - 698 MHz), VHF (54 - 216 MHz)
* **Channel Bandwidth**: 6 MHz (in North America)
* **Modulation**: OFDM
* **Subcarrier Modulation**: QPSK, 16-QAM, 64-QAM, 256-QAM, 1024-QAM, 4096-QAM (Non-Uniform QAM)
* **FFT Sizes**: 8K (8192), 16K (16384), 32K (32768)

## 2. Synchronization & Pilots
* **Bootstrap**: A robust, low-SNR preamble at the start of every frame using Zadoff-Chu sequences. It signals the FFT size, guard interval, and pilot pattern.
* **Scattered Pilots**: Inserted throughout the OFDM grid to estimate the channel response. 
* **Continual Pilots**: Specific subcarriers that always contain pilots for phase noise tracking.
