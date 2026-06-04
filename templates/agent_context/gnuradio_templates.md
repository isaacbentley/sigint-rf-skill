# 💻 Agentic GNU Radio Templates: Boilerplate & Code Guidelines

Use this guide as a reference when asked by the operator to write GNU Radio Python scripts (`.py`). These templates utilize standard libraries and promote portable, robust code.

---

## 🏗️ Basic top_block Class Skeleton

All GNU Radio flowgraphs in Python follow this class structure inheriting from `gr.top_block`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog
from gnuradio import filter
from gnuradio.filter import firdes
import sys

class rf_receiver(gr.top_block):
    def __init__(self, filepath, sample_rate, center_freq):
        gr.top_block.__init__(self, "RF Receiver Flowgraph")

        # 1. Parameters
        self.filepath = filepath
        self.sample_rate = sample_rate
        self.center_freq = center_freq

        # 2. Block Declarations
        self.src = blocks.file_source(gr.sizeof_gr_complex, self.filepath, repeat=False)
        self.throttle = blocks.throttle(gr.sizeof_gr_complex, self.sample_rate, True)
        
        # Sinks (e.g. File Sink or Null Sink)
        self.sink = blocks.null_sink(gr.sizeof_gr_complex)

        # 3. Connections
        self.connect((self.src, 0), (self.throttle, 0))
        self.connect((self.throttle, 0), (self.sink, 0))

def main():
    tb = rf_receiver("capture.cf32", 2048000, 433920000)
    tb.start()
    tb.wait()

if __name__ == '__main__':
    main()
```

---

## 📻 FSK Demodulator Flowgraph Template

For binary FSK signals (like GFSK/GMSK weather sensors or fobs), construct the receiver using these real blocks:

```python
from gnuradio import gr
from gnuradio import blocks
from gnuradio import analog
from gnuradio import digital
from gnuradio import filter

class fsk_demodulator(gr.top_block):
    def __init__(self, filepath, sample_rate, symbol_rate, deviation_hz):
        gr.top_block.__init__(self, "FSK Demodulator")

        # 1. Blocks
        # Source
        self.src = blocks.file_source(gr.sizeof_gr_complex, filepath, repeat=False)
        
        # Low-pass filter to reject out-of-band noise
        self.lpf = filter.fir_filter_ccf(
            1, # Decimation factor
            filter.firdes.low_pass(
                1.0,           # Gain
                sample_rate,   # Sample rate
                symbol_rate*2, # Cutoff frequency
                symbol_rate/2, # Transition width
                filter.firdes.WIN_HAMMING
            )
        )
        
        # Quadrature Demod (Discriminator): sensitivity = sample_rate / (2 * pi * deviation)
        sensitivity = sample_rate / (2.0 * 3.14159 * deviation_hz)
        self.quad_demod = analog.quadrature_demod_cf(sensitivity)
        
        # Symbol Sync: Clock recovery (decimates samples per symbol to 1)
        sps = sample_rate / symbol_rate
        # Simplest block: Symbol Sync
        self.sync = digital.symbol_sync_ff(
            digital.TED_GARDNER, 
            sps,          # Loop parameter: samples per symbol
            0.05,         # Loop bandwidth
            1.0,          # Damping factor
            1.0,          # Internal oscillator gain
            0.5,          # Maximum deviation
            0.0,          # Output phase
            1,            # Output samples per symbol
            []            # Taps
        )
        
        # Binary Slicer: Slices floats (positive -> 1, negative -> 0)
        self.slicer = digital.binary_slicer_fb()
        
        # File Sink (Saves raw bytes of sliced bits)
        self.sink = blocks.file_sink(gr.sizeof_char, "bits.bin")

        # 2. Connections
        self.connect((self.src, 0), (self.lpf, 0))
        self.connect((self.lpf, 0), (self.quad_demod, 0))
        self.connect((self.quad_demod, 0), (self.sync, 0))
        self.connect((self.sync, 0), (self.slicer, 0))
        self.connect((self.slicer, 0), (self.sink, 0))
```

---

## 🐍 Writing an Embedded Python Block for Custom Logic

If custom parsing, packet sync, or framing is required, write a custom `gr.sync_block` directly in the script. This avoids external compilation:

```python
import numpy as np
from gnuradio import gr

class packet_sync_block(gr.sync_block):
    def __init__(self, sync_word=0xD215D8):
        gr.sync_block.__init__(
            self,
            name="Packet Sync & Frame Extractor",
            in_sig=[np.uint8],  # Input format: byte stream
            out_sig=[np.uint8]  # Output format: framed packet bytes
        )
        self.sync_word = sync_word
        self.buffer = []

    def work(self, input_items, output_items):
        in_data = input_items[0]
        out_data = output_items[0]
        
        # Processing logic goes here:
        # 1. Read input bytes
        # 2. Search for the synchronization word in a sliding buffer
        # 3. Output framed packets when found
        
        # Copy to output
        n = min(len(in_data), len(out_data))
        out_data[:n] = in_data[:n]
        return n
```
