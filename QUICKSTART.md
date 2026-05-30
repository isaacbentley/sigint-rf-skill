# Quick Start Guide 🚀

This guide walks you through setting up and running the triage and demodulation tools included in this repository.

---

## 1. Install Dependencies
Make sure you have Python 3 installed. Install the minimal requirements in [tools/requirements.txt](tools/requirements.txt):
```bash
pip install -r tools/requirements.txt
```

---

## 2. Discover & Capture (Automated)
If you don't know the exact transmitter frequency, use the automated wideband discovery pipeline to scan, find the strongest signal, capture, and triage in one step:
```bash
python tools/discover_and_capture.py --start 433M --stop 435M --scan-sec 5 -o capture.cf32
```
This runs a wideband `rtl_power` scan, finds the highest-power peak, captures raw IQ using `rtl_sdr`, converts to complex float32 (`.cf32`), and automatically launches [tools/triage_iq.py](tools/triage_iq.py).

---

## 3. Run the Triage Tool on an IQ File
Provide a raw IQ binary file (`.bin`, `.cf32`, `.iq`) or a SigMF recording (`.sigmf-meta` / `.sigmf-data`):
```bash
python tools/triage_iq.py --file capture.cf32 --rate 2400000
```
This will:
1. Compute the FFT, power spectral density (PSD), and signal bandwidth.
2. Search for bursts and compute temporal characteristics.
3. Check for specific cyclic prefixes or synchronization signals.
4. Output a file `triage_report.md` and a diagnostic plot `triage_plot.png`.

---

## 4. Explainable Demodulation
Once you or your AI agent identifies the signal type from the triage report, run the explainable demodulator to extract bits or media:
```bash
python tools/explainable_demod.py --file capture.cf32 --rate 2400000 --mode fsk --symbol-rate 10000
```
This runs each DSP block step-by-step with verbose logging and generates `demod_diagnostics.png` with eye diagrams and clock recovery plots.

---

## 5. Agentic Triage & Explain
Copy the contents of `triage_report.md` (or read it with your agentic framework) and feed it to the AI agent loaded with the instructions from [SKILL.md](SKILL.md). The agent will:
1. Identify the most likely protocol or signal type.
2. Outline the exact demodulation blocks (e.g., Python SciPy code, GNU Radio flowgraphs, or C/Rust libraries).
3. Walk you through extracting telemetry or user data from the payload.
