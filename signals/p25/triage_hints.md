# Triage Hints: APCO P25

## Visual Spectrum Signatures
* **Bandwidth**: Clean 12.5 kHz narrow channel.
* **Shape**: Standard single-carrier hump with steep roll-off.
* **Multiple Channels**: Often seen in trunking sites with 1 strong continuous control channel and multiple intermittent voice channels nearby.

## Expected Triage Metrics
* **P25 Phase I (Control/Voice)**:
  * **PAPR**: ~0-2 dB (Constant envelope for C4FM).
  * **Duty Cycle**: 100% (Continuous).
  * **Frequency Deviation**: ~1.8 kHz (Inner symbols at ±600 Hz, outer at ±1800 Hz).
  * **Amplitude Std/Mean**: Very low (<0.05).
* **P25 Phase II (Voice Only)**:
  * **PAPR**: ~3-5 dB (PSK modulation has amplitude variation).
  * **Duty Cycle**: ~50% for a single active slot (Bursty).
  * **Average Burst Duration**: Exactly 30 ms.

## Demodulation Approach
* Use `explainable_demod.py --mode fsk --symbol-rate 4800` for Phase 1.
* Use `explainable_demod.py --mode psk --symbol-rate 6000` for Phase 2 bursts.
* Use companion tools like `SDRTrunk`, `OP25`, or `DSD+` for actual voice decoding and trunking tracking.
