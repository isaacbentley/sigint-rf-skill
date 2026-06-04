# 📻 Agentic Demodulation Guide: Configuring explainable_demod.py

This guide explains how to configure [explainable_demod.py](../../tools/explainable_demod.py) for various signal modulation schemes.

---

## ⚙️ Core CLI Arguments

```bash
python3 tools/explainable_demod.py --file <path> --mode <mode> --rate <sample_rate_hz> [options]
```

| Argument | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--file` | String | *Required* | Path to the IQ file. Accepts a `.sigmf-meta` / `.sigmf-data` — sample rate, datatype, and center frequency are auto-loaded from the metadata. |
| `--mode` | Choice | *Required* | Demodulation mode: `fsk`, `ook`, `fm_audio`, `am_audio`, `analog_video`, `analog_fm`, `analog_am`, `psk`, `qam`, `lora`, `ofdm`, `sc-fdma`. |
| `--rate` | Float | `15.36e6` | Sample rate in Hz. Ignored when SigMF metadata supplies it. |
| `--format` | Choice | *auto* | IQ format: `cf32_le` or `ci16_le`. Auto-detected from SigMF / file extension if omitted. |
| `--duration` | Float | `0.0` | Seconds of data to read (`0` = use `--max-samples`). |
| `--max-samples` | Int | `20000000` | Cap on complex samples read when `--duration` is 0 — bounds RAM on large (multi-GB) captures. |
| `--offset-hz`| Float | `0.0` | Frequency shift in Hz to center the signal. Negative scientific notation works (e.g. `--offset-hz -25e6`). |
| `--channel-bw`| Float | `None` | Low-pass channel-isolation bandwidth in Hz (rejects adjacent signals). |
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
*   **Auto-detection**: Measures the line rate + lines-per-frame, prints the detected standard (NTSC vs PAL), and auto-derives the raster geometry. Also flags any FM audio subcarrier near 6.0/6.5 MHz while **rejecting line-rate harmonics** (on PAL those land exactly at 6.0/6.5 MHz).
*   **Optional Overrides**:
    *   `--line-samples`: Force samples per line (else auto-measured).
    *   `--video-lines`: Force active line count (else 525 NTSC / 625 PAL).
*   **Example** (geometry auto-detected):
    ```bash
    python3 tools/explainable_demod.py --file fpv.sigmf-meta --mode analog_video
    ```

---

## 🛠️ Troubleshooting for Agents

*   **Error: "Sample rate too low"**: This happens if the samples per symbol ($Sps = \frac{\text{Sample Rate}}{\text{Symbol Rate}}$) is $< 2.0$. Instruct the user to check their capture sample rate or verify if they entered the wrong symbol rate.
*   **DC Offset / Decentered Frequency**: If the signal's center is shifted relative to the capture center, the FM or PSK lock will fail. Calculate the peak frequency offset from the JSON metrics (`peak_freq`) and pass it as `--offset-hz <offset_value>`.
