# 🔍 Agentic Triage Guide: Running and Parsing Triage IQ

This guide helps you execute the [triage_iq.py](../../tools/triage_iq.py) tool and programmatically parse its outputs.

---

## 🚀 Running the Triage Script

Execute the triage tool with the following syntax:

```bash
python3 tools/triage_iq.py --file <path_to_iq_file> --rate <sample_rate_hz> [options]
```

### CLI Arguments Reference

| Argument | Short | Type | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `--file` | `-f` | String | *Required* | Path to the IQ file (`.bin`, `.cf32`, `.sigmf-data`, or `.sigmf-meta`). |
| `--rate` | `-r` | Float | `15.36e6` | Sample rate in Hz (ignored if SigMF metadata is found). |
| `--freq` | `-c` | Float | `None` | Center frequency in Hz (loaded from SigMF if found). |
| `--format` | — | Choice | `None` | Input format: `cf32_le` (float32 IQ) or `ci16_le` (int16 IQ). Autodetected if omitted. |
| `--duration`| — | Float | `0.150` | Seconds of data to analyze. Set to `0` to analyze up to `--max-samples`. |
| `--max-samples`| — | Int | `2000000` | Maximum samples to read if `--duration` is 0. |
| `--output` | `-o` | String | `triage_report.md`| Filename for the output markdown report. |
| `--plot` | `-p` | String | `triage_plot.png`| Filename to save the visual diagnostic dashboard. |
| `--json-output`| — | String | `None` | Path to save the extracted numeric metrics to a JSON file. |

*   **Best Practice**: Always specify `--json-output metrics.json` to allow you to programmatically parse the signal metrics in subsequent Python steps!

---

## 📊 Parsing the JSON Metrics

When you generate a JSON metrics file, it contains the following keys. Use this reference to write check scripts:

```json
{
  "peak_freq": 15000.0,
  "snr_db": 22.45,
  "obw_99": 250000.0,
  "obw_90": 200000.0,
  "flatness": 0.421,
  "papr_db": 1.25,
  "amp_std_to_mean": 0.012,
  "freq_std_hz": 125000.0,
  "freq_dev_hz": 125000.0,
  "freq_dist_shape": 1.0,
  "duty_cycle": 1.0,
  "is_bursty": false,
  "avg_burst_samples": 0.0,
  "max_burst_samples": 0.0,
  "peak_lags": [4, 8, 12],
  "peak_vals": [0.85, 0.71, 0.60]
}
```

### Key Metrics & Decision Rules for Agents

1.  **SNR Validation (`snr_db`)**:
    *   If `snr_db < 5.0`, declare the signal as `NOISY` / `No Signal Detected`. Do not try to demodulate noise.
2.  **Envelope Type (`amp_std_to_mean`)**:
    *   `amp_std_to_mean < 0.05`: Constant envelope (FSK, GFSK, MSK, GMSK, analog FM, or LoRa).
    *   `amp_std_to_mean > 0.45`: Variable envelope (OOK/ASK or high-order QAM).
3.  **Frequency Sweep Shape (`freq_dist_shape`)**:
    *   `freq_dist_shape` is computed as `freq_std_hz / freq_dev_hz`.
    *   If `~0.58` (uniform distribution): **CSS (Chirp / LoRa)**.
    *   If `~1.0` (bimodal distribution): **FSK / GFSK** (discrete tone values).
4.  **OFDM Detection (`flatness`)**:
    *   If `flatness > 0.70`, the signal exhibits a flat-top shape indicating a multi-carrier **OFDM** signal (e.g. Wi-Fi, LTE).
5.  **Periodicities / Autocorrelation (`peak_lags` & `peak_vals`)**:
    *   `peak_lags` are in samples. Divide by the sample rate to get the period in seconds:
        $$\text{Period (s)} = \frac{\text{Lag (samples)}}{\text{Sample Rate (Hz)}}$$
    *   A lag matching the cyclic prefix length confirms OFDM. A lag matching a bit period confirms PPM/AFSK/BPSK symbol clocking.
