#!/usr/bin/env python3
"""Regression tests for IQ reading: format coverage (cf32/ci16/cu8/ci8) and the
corrupt-capture guard (NaN/Inf scrub + magnitude clamp).

Both triage_iq.py and explainable_demod.py carry their own copy of
read_iq_samples (the tools are intentionally self-contained), so we exercise
both. Run directly: ``python3 tools/test_read.py`` — exits non-zero on failure.
"""
import os
import sys
import tempfile
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import triage_iq
import explainable_demod

READERS = [("triage_iq", triage_iq.read_iq_samples),
           ("explainable_demod", explainable_demod.read_iq_samples)]

failures = []


def check(cond, msg):
    print(("  ok  " if cond else "  FAIL") + f"  {msg}")
    if not cond:
        failures.append(msg)


def make_signal(n=4096):
    """A deterministic complex tone in ~[-1, 1] we can re-encode into any format."""
    rng = np.random.default_rng(0)
    t = np.arange(n)
    iq = 0.7 * np.exp(1j * 2 * np.pi * 0.03 * t) + 0.02 * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    return iq.astype(np.complex64)


def write_interleaved(path, iq, encode):
    inter = np.empty(iq.size * 2, dtype=np.float32)
    inter[0::2] = iq.real
    inter[1::2] = iq.imag
    encode(inter).tofile(path)


def main():
    iq = make_signal()
    with tempfile.TemporaryDirectory() as d:
        paths = {
            "cf32_le": os.path.join(d, "s.cf32"),
            "ci16_le": os.path.join(d, "s.ci16"),
            "cu8":     os.path.join(d, "s.cu8"),
            "ci8":     os.path.join(d, "s.ci8"),
        }
        write_interleaved(paths["cf32_le"], iq, lambda a: a.astype(np.float32))
        write_interleaved(paths["ci16_le"], iq, lambda a: np.clip(np.round(a * 32768.0), -32768, 32767).astype(np.int16))
        write_interleaved(paths["cu8"],     iq, lambda a: np.clip(np.round(a * 127.5 + 127.5), 0, 255).astype(np.uint8))
        write_interleaved(paths["ci8"],     iq, lambda a: np.clip(np.round(a * 127.5), -128, 127).astype(np.int8))

        for name, reader in READERS:
            print(f"\n[{name}] format round-trip")
            ref = reader(paths["cf32_le"], "cf32_le", iq.size)
            check(len(ref) == iq.size, f"cf32 sample count == {iq.size}")
            for fmt in ("ci16_le", "cu8", "ci8"):
                got = reader(paths[fmt], fmt, iq.size)
                check(len(got) == iq.size, f"{fmt} sample count == {iq.size}")
                check(np.all(np.isfinite(got)), f"{fmt} all finite")
                # 8-bit quantization tolerance is generous; we only assert the
                # decoded stream tracks the reference rather than being garbage.
                err = np.median(np.abs(got - ref))
                check(err < 0.05, f"{fmt} tracks cf32 (median |err| {err:.4f} < 0.05)")
            # Alias handling: the friendly name "uint8" must resolve to cu8.
            aliased = reader(paths["cu8"], "uint8", iq.size)
            check(np.all(np.isfinite(aliased)) and len(aliased) == iq.size, "alias 'uint8' -> cu8 reads correctly")

            print(f"[{name}] corrupt-capture guard")
            bad = np.empty(iq.size * 2, dtype=np.float32)
            bad[0::2] = iq.real
            bad[1::2] = iq.imag
            bad[10:24] = np.nan
            bad[30:34] = np.inf
            bad[50] = -np.inf
            bad[60] = 1e9  # absurd magnitude to exercise the clamp
            bad_path = os.path.join(d, "bad.cf32")
            bad.tofile(bad_path)
            out = reader(bad_path, "cf32_le", iq.size)
            check(np.all(np.isfinite(out)), "NaN/Inf scrubbed to finite values")
            check(np.max(np.abs(out.real)) <= 1000.0 and np.max(np.abs(out.imag)) <= 1000.0,
                  "magnitudes clamped to <= 1000")

    print()
    if failures:
        print(f"FAILED: {len(failures)} check(s)")
        sys.exit(1)
    print("All read/format/guard checks passed.")


if __name__ == "__main__":
    main()
