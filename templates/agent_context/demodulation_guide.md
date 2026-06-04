# 📻 Agentic Demodulation Guide: Configuring explainable_demod.py

This guide explains how to configure [explainable_demod.py](../../tools/explainable_demod.py) for various signal modulation schemes.

---

## ⚙️ Core CLI Arguments

```bash
python3 tools/explainable_demod.py --file <path> --mode <mode> --rate <sample_rate_hz> [options]
```

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--file` | String | *Required* | Path to the raw IQ sample file. |
| `--mode` | Choice | *Required* | Demodulation mode: `fsk`, `ook`, `fm_audio`, `am_audio`, `analog_video`, `psk`, `qam`, `lora`, `ofdm`, `sc-fdma`. |
| `--rate` | Float | `15.36e6` | Sample rate of the capture in Hz. |
| `--format` | Choice | `cf32_le` | IQ format: `cf32_le` (float32 complex) or `ci16_le` (int16 complex). |
| `--offset-hz`| Float | `0.0` | Manual frequency offset shift in Hz (use this to center the signal if it is off-center). |
| `--plot-path`| String | `demod_diagnostics.png` | Destination path to save intermediate DSP graphs. |
| `--verbose` | Flag | `False` | Print detailed step-by-step DSP mathematical explanations. |

---

## 🗺️ Mode-Specific Configurations

### 1. Frequency Shift Keying (`fsk`)
*   **Use Case**: DMR, VHF/UHF digital radio, TPMS, weather stations.
*   **Required Options**:
    *   `--symbol-rate`: Expected baud rate of the signal (e.g. `250000`).
    *   `--output-bits`: Path to write the sliced bits as a text file.
*   **Example**:
    ```bash
    python3 tools/explainable_demod.py -f capture.cf32 --mode fsk --rate 2048000 --symbol-rate 250000 --output-bits bits.txt
    ```

### 2. On-Off Keying / Amplitude Shift Keying (`ook`)
*   **Use Case**: Garage door remotes, doorbells, home security sensors.
*   **Example**:
    ```bash
    python3 tools/explainable_demod.py -f capture.cf32 --mode ook --rate 2048000
    ```

### 3. Broadcast Audio (`fm_audio` / `am_audio`)
*   **Use Case**: Listening to commercial FM/AM stations or analog voice walkie-talkies.
*   **Required Options**:
    *   `--audio-rate`: Target output sample rate (default: `48000.0` for `.wav` file playback).
*   **Example**:
    ```bash
    python3 tools/explainable_demod.py -f fm_station.cf32 --mode fm_audio --rate 2048000 --audio-rate 48000
    ```

### 4. Phase Shift Keying (`psk`)
*   **Use Case**: BPSK/QPSK telemetry links, Zigbee.
*   **Required Options**:
    *   `--symbol-rate`: Expected baud rate (e.g., `1000000`).
    *   `--psk-order`: `2` for BPSK, `4` for QPSK, `8` for 8-PSK.
*   **Example**:
    ```bash
    python3 tools/explainable_demod.py -f telemetry.cf32 --mode psk --rate 4000000 --symbol-rate 1000000 --psk-order 4
    ```

### 5. Quadrature Amplitude Modulation (`qam`)
*   **Use Case**: Cable modems, higher-speed digital downlinks.
*   **Required Options**:
    *   `--symbol-rate`: Expected baud rate.
    *   `--qam-order`: `16`, `64`, or `256`.

### 6. Chirp Spread Spectrum (`lora`)
*   **Use Case**: LoRa / LoRaWAN IoT telemetry.
*   **Required Options**:
    *   `--lora-bw`: LoRa bandwidth in Hz (e.g., `125000`, `250000`, `500000`).
    *   `--lora-sf`: Spreading factor from `6` to `12` (default: `7`).

### 7. Orthogonal Frequency Division Multiplexing (`ofdm` / `sc-fdma`)
*   **Use Case**: Wi-Fi, LTE, DJI OcuSync drone downlinks.
*   **Required Options**:
    *   `--ofdm-profile`: Pre-configured profile (`wifi`, `lte`, `ocusync`, `atsc`, `dvb`) or `custom`.
    *   `--ofdm-fft`: FFT size / number of subcarriers (if profile is `custom`).
    *   `--ofdm-cp`: Cyclic prefix length in samples (if profile is `custom`).
    *   `--sc-fdma-alloc`: Subcarrier allocation size (for LTE uplink / SC-FDMA).

### 8. Analog Video (`analog_video`)
*   **Use Case**: FPV analog drone video feeds (PAL/NTSC).
*   **Required Options**:
    *   `--line-samples`: Number of samples per line raster (e.g. `1280` or `1560`).
    *   `--video-lines`: Active line count (e.g. `576` for PAL, `480` for NTSC).

---

## 🛠️ Troubleshooting for Agents

*   **Error: "Sample rate too low"**: This happens if the samples per symbol ($Sps = \frac{\text{Sample Rate}}{\text{Symbol Rate}}$) is $< 2.0$. Instruct the user to check their capture sample rate or verify if they entered the wrong symbol rate.
*   **DC Offset / Decentered Frequency**: If the signal's center is shifted relative to the capture center, the FM or PSK lock will fail. Calculate the peak frequency offset from the JSON metrics (`peak_freq`) and pass it as `--offset-hz <offset_value>`.
