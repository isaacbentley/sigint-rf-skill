# Contributing to SigInt RF Skill 📻🤝

First off, thank you for considering contributing to `sigint-rf-skill`! This repository aims to make RF triage and decoding knowledge accessible and structured for developers and LLMs alike.

---

## 🗺️ How Can I Contribute?

### 1. Requesting or Registering a New Signal Spec
If you've triaged a new wireless protocol or RF signal, we would love to add it to the `signals/` library!
1. Use our issue templates online to submit a **New Signal Request** containing center frequency, occupied bandwidth, modulation, and sync words.
2. If submitting a Pull Request, create a directory under `signals/` (e.g., `signals/my_new_protocol/`) and add:
   * **`spec.md`** (using the template at [templates/signal_template.md](templates/signal_template.md) as a guide).
   * **`triage_hints.md`** containing spectral and temporal indicators.

### 2. Improving Triage & Demodulator Tools
If you want to add new DSP blocks, carrier recovery loops, or fix a bug in the Python tools (`triage_iq.py`, `explainable_demod.py`, or `discover_and_capture.py`):
1. Fork the repository and create your branch from `main`.
2. Add your improvements, keeping the code clean, dependency-free (relying only on NumPy, SciPy, and Matplotlib), and well-commented.
3. Make sure to run the integration test suite to verify no regressions were introduced:
   ```bash
   python3 tools/test_workflow.py
   ```
4. Open a Pull Request with a clear description of the feature or fix.

### 3. Reporting Bugs or Requesting Features
If you run into issues, open an issue using the appropriate template:
* **Bug Report**: Include command log tracebacks, sample rates, format details, and your OS/SDR hardware.
* **Feature Request**: Explain the problem it solves and suggest a mathematical formula or algorithm.

---

## 📝 Code of Conduct & Style Guide
* Keep DSP logic "explainable". Use step-by-step logs and educational comments to detail mathematical calculations (e.g., why Costas Loops or clock recovery offsets are configured a certain way).
* Round operator-facing statistics to simple, easily readable bounds (e.g., convert `15.358 MSPS` to `15.4 MSPS` or `52.34 kHz` to `52 kHz` in summaries). High precision must be preserved in execution code but clean in text responses.
