# Signal Specification: DVB-T / DVB-T2

Digital Video Broadcasting - Terrestrial (DVB-T) is the European-based consortium standard for the broadcast transmission of digital terrestrial television. It was the first widely adopted OFDM-based TV broadcast standard.

## 1. Physical Layer Parameters
* **Frequency Bands**: UHF (470 - 862 MHz), VHF (174 - 230 MHz)
* **Channel Bandwidth**: 6 MHz, 7 MHz, or 8 MHz (most common in Europe)
* **Modulation**: COFDM
* **Subcarrier Modulation**: QPSK, 16-QAM, 64-QAM (DVB-T) up to 256-QAM (DVB-T2)
* **FFT Sizes**: 2K (2048), 8K (8192) in DVB-T. Extended to 1K, 4K, 16K, 32K in DVB-T2.

## 2. Synchronization & Pilots
* **Cyclic Prefix (Guard Interval)**: Variable lengths (1/4, 1/8, 1/16, 1/32 of the symbol duration) to combat multi-path.
* **Scattered Pilots**: Inserted every 12th subcarrier (in DVB-T) for channel estimation.
* **Continual Pilots**: For phase noise correction.
* **TPS (Transmission Parameter Signalling)**: Dedicated subcarriers carrying BPSK data about the modulation parameters.
