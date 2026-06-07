# Worked Example: Triaging Analog FPV Video (NTSC vs PAL)

A reproducible, **hardware-free** walkthrough of identifying and decoding 5.8 GHz
analog FPV video, and telling NTSC from PAL by *measuring* the raster timing rather
than trusting a label. Every command below runs with the bundled tools and synthetic
generator — no SDR required.

## 1. Synthesize a practice signal (no SDR)

```bash
# NTSC with a real 6.5 MHz FM audio subcarrier
python3 tools/generate_demo_signal.py --type analog_video --standard ntsc \
  --audio_subcarrier --output_file /tmp/demo_ntsc.cf32

# PAL, video only
python3 tools/generate_demo_signal.py --type analog_video --standard pal \
  --output_file /tmp/demo_pal.cf32
```

Each writes a `cf32` capture **and** a matching `.sigmf-meta` (20 MSPS, 5.8 GHz center,
`fpv:fm_deviation` set), so the rest of the pipeline reads it like a real SigMF capture.

## 2. Triage

```bash
python3 tools/triage_iq.py --file /tmp/demo_ntsc.sigmf-meta --json-output /tmp/ntsc.json
```

FPV-analog fingerprint to look for (see [triage_hints.md](../signals/fpv_analog/triage_hints.md)):

* **Constant-envelope IQ ring** + **low PAPR** (~0.5–3 dB — *not* a hard <1.5 dB cutoff;
  filtering and sync-tip AM push it up). The gap to digital (Wi-Fi/OcuSync > 8 dB) is the tell.
* **Single-carrier** spectrum (flatness < 0.4), **100 % duty cycle** (continuous).
* **Occupied BW** scales with deviation (~12–30 MHz; ~15 MHz is normal after channel filtering).

## 3. Demodulate — automatic NTSC/PAL identification

```bash
python3 tools/explainable_demod.py --file /tmp/demo_ntsc.sigmf-meta --mode analog_video
python3 tools/explainable_demod.py --file /tmp/demo_pal.sigmf-meta  --mode analog_video
```

No `--rate`, `--format`, `--line-samples`, or `--video-lines` needed — they are resolved
from SigMF and **measured** from the signal. Expected output:

```
NTSC:  📺 Detected standard: NTSC (line 63.55 us / 15736 Hz, ~525 lines/frame)
       🔊 Audio subcarrier: PRESENT near 6.5 MHz (+36 dB above local floor)
PAL:   📺 Detected standard: PAL  (line 64.00 us / 15625 Hz, ~625 lines/frame)
       ⚠️ Audio subcarrier: energy near 6.5 MHz coincides with the 416x line-rate
          harmonic — cannot confirm a distinct subcarrier
```

A `*_frame.png` (reconstructed grayscale raster) and `*_dashboard.png` (baseband
diagnostics) are written next to the `--plot-path`.

## 4. Why these checks, not the label

* **NTSC vs PAL are physically identical FM video** — only the raster timing differs
  (NTSC 15734 Hz / 525 lines / ~60 Hz; PAL 15625 Hz / 625 lines / 50 Hz). The tool
  FM-demodulates, then autocorrelates for the **line period** and collapses each line to
  its mean to count **lines-per-frame**. Line rate is the primary discriminator; the
  frame count corroborates.
* **Audio-subcarrier vs line harmonic.** A naive "peak near 6.0/6.5 MHz" detector
  false-positives on PAL, because 6.0 MHz = 384× and 6.5 MHz = 416× the 15625 Hz line
  rate exactly — they *are* sync harmonics. The detector rejects integer-multiple
  coincidences (using the canonical line rate) and only confirms a subcarrier when it
  doesn't line up with a harmonic (cleanly visible on NTSC).

## 5. Security context

Analog FPV is unencrypted, unauthenticated, fixed-channel FM: passively viewable on any
5.8 GHz analog receiver, vulnerable to capture-effect video hijack by a stronger
co-channel transmitter, and trivially direction-found to the pilot.
