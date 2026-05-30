# SigInt RF Agentic Skill 📻🤖

Have you ever stared at a raw IQ signal capture or a software-defined radio (SDR) waterfall plot and wished your AI assistant could instantly tell you what protocol it is, how to demodulate it, or write the exact Python/GNU Radio script to decode it? 

`sigint-rf-skill` is built to do exactly that! It is a structured **AI Agentic Skill** and registry compiling RF signal specifications, triage guidelines, and demodulation instructions. By loading this repository as a Developer Agentic Skill, you instantly equip your favorite AI assistants (like Claude Code and Google Antigravity) with a comprehensive RF signal library, triage matrices, and digital signal processing heuristics. Instead of manually looking up channel frequencies, allocation tables, or struggling with demodulation mathematics, your AI assistant can guide you through the triage process, write clean decoding code, and run diagnostics automatically.

## 🌟 Key Features

* **LLM-First Design**: Includes detailed, structured prompts and heuristics ([SKILL.md](SKILL.md) and `triage_hints.md` files) to teach AI agents how to recognize and decode signals without manual calculation.
* **Automated IQ Triage**: A Python utility ([tools/triage_iq.py](tools/triage_iq.py)) that extracts key spectral parameters (Center Freq, Bandwidth, SNR, Burst vs. Continuous, Autocorrelation cyclic periods) and writes a markdown report optimized for LLM ingestion.
* **Signal Library**: Standardized specifications for common and complex drone, IoT, aviation, and telemetry signals.
* **FFI & GNU Radio Links**: Step-by-step guidance on how to decode raw bits or extract telemetry packets using custom SDR tools or python scripts.

---

## 🤖 Loading as an AI Agent Skill

This repository is designed from the ground up as an **Agentic Skill** (a tool and context bundle) for developer AI agents. By loading `sigint-rf-skill`, your AI assistant becomes a specialist in Software Defined Radio (SDR) and RF signals intelligence.

### 🚀 Global Installation (Claude Code & Google Antigravity)
If you are using an AI agent with terminal capabilities (such as Claude Code or Google Antigravity), you can simply copy and paste the prompt below. The agent will automatically clone the repository, set up the global skill registry directory, and load the skill context:

> **Prompt:** `"Please download the sigint-rf-skill repository from https://github.com/isaacbentley/sigint-rf-skill.git and install it globally as a skill on my machine."`

*Note: Depending on the agent you are using, this prompt will automatically register the skill under your personal global directory (e.g., `~/.claude/skills/sigint-rf-expert` for Claude Code or `~/.gemini/config/plugins/sigint-rf-plugin/` for Google Antigravity).*

### 💻 Programmatic SDK Integration (Google Antigravity SDK)
To load this skill programmatically for an autonomous agent:
* Define a new agent or add a skill capability referencing this repository.
* Include the contents of `SKILL.md` in the agent's system prompt configuration:
  ```python
  from antigravity import Agent, Skill
  
  # Register the SigInt RF Skill
  sigint_skill = Skill.from_markdown("path/to/sigint-rf-skill/SKILL.md")
  agent = Agent(
      name="RF-Expert",
      system_prompt="You are a SigInt analyst...",
      skills=[sigint_skill]
  )
  ```

---

## 📂 Directory Layout

```
sigint-rf-skill/
├── README.md                 # This file
├── SKILL.md                  # System instruction/prompt definition for LLM Agentic Skills
├── templates/
│   └── signal_template.md    # Template for documenting and adding new RF signal types
├── tools/
│   ├── discover_and_capture.py  # Automated wideband scan → capture → triage pipeline
│   ├── triage_iq.py             # Python IQ analysis and prompt generator
│   ├── explainable_demod.py     # Step-by-step explainable demodulator with diagnostics
│   ├── generate_demo_signal.py  # Generate synthetic demo IQ signals for testing
│   ├── test_workflow.py         # End-to-end workflow integration tests
│   └── requirements.txt        # Python dependencies
└── signals/
    ├── dji_ocusync/          # DJI OcuSync (O1-O4) 10-60 MHz OFDM signals
    │   ├── spec.md
    │   └── triage_hints.md
    ├── fpv_analog/           # FPV Analog video signals (PAL/NTSC FM)
    │   ├── spec.md
    │   └── triage_hints.md
    ├── lora/                 # LoRa Chirp Spread Spectrum (CSS) IoT signals
    │   ├── spec.md
    │   ├── triage_hints.md
    │   └── meshtastic.md     # Meshtastic LoRa mesh network protocol overlay
    ├── adsb/                 # ADS-B Mode S aviation transponders (1090 MHz PPM)
    │   ├── spec.md
    │   └── triage_hints.md
    ├── tpms/                 # TPMS Tire Pressure Monitoring System (315/433 MHz)
    │   ├── spec.md
    │   └── triage_hints.md
    └── modulations/          # Fundamental RF Modulation specifications
        ├── am/               # Amplitude Modulation (AM Broadcast / VHF Air Band)
        │   ├── spec.md
        │   └── triage_hints.md
        ├── ook_ask/          # On-Off Keying & Amplitude Shift Keying
        │   ├── spec.md
        │   └── triage_hints.md
        ├── fsk_gfsk/         # Frequency Shift Keying & Gaussian FSK
        │   ├── spec.md
        │   └── triage_hints.md
        ├── psk/              # Phase Shift Keying (BPSK/QPSK)
        │   ├── spec.md
        │   └── triage_hints.md
        └── qam/              # Quadrature Amplitude Modulation (QAM-16/QAM-64)
            ├── spec.md
            └── triage_hints.md
```

---

## 🚀 Quick Start
To install dependencies and start capturing, triaging, or demodulating signals, follow the step-by-step instructions in the [Quick Start Guide](QUICKSTART.md).

---

## 🧰 Available Tools

| Tool | Description |
|---|---|
| [tools/discover_and_capture.py](tools/discover_and_capture.py) | Automated wideband scan → peak detection → IQ capture → triage pipeline using `rtl_power` and `rtl_sdr` |
| [tools/triage_iq.py](tools/triage_iq.py) | Extracts spectral, temporal, and autocorrelation features from raw IQ files; generates markdown reports and diagnostic plots |
| [tools/explainable_demod.py](tools/explainable_demod.py) | Step-by-step explainable demodulator supporting FSK, FM audio, and analog video modes with diagnostic plots |
| [tools/generate_demo_signal.py](tools/generate_demo_signal.py) | Generates synthetic demo IQ signal files for testing the triage pipeline |
| [tools/test_workflow.py](tools/test_workflow.py) | End-to-end integration tests for the full discover → triage → demod workflow |


---

## 🙏 Acknowledgements, References & Licensing

This project is built upon the incredible work of the open-source Software Defined Radio (SDR) community. We acknowledge and credit the following resources:

* **[Signal Identification Wiki (sigidwiki.com)](https://www.sigidwiki.com/)**: The definitive community-driven database of radio signals. Our triage matrices and web escalation protocols direct agents to reference their extensive catalog. *Sigidwiki content is available under Creative Commons Attribution-ShareAlike.*
* **[RTL-SDR Blog (rtl-sdr.com)](https://www.rtl-sdr.com/)**: For extensive community guides, tool repositories, and accessible hardware that makes this domain possible.
* **[rfhs / rfctf-sdr-tools & rfhs-wiki](https://github.com/rfhs)**: We reference GNU Radio receiver templates (e.g., ZMQ, NBFM, USB) and challenge architectures from the `rfctf-sdr-tools` repository. 
  - *License*: `rfctf-sdr-tools` is released under the **BSD 3-Clause License** (Copyright (c) 2020, rfhs).
* **[GNU Radio](https://www.gnuradio.org/)**: The premier open-source SDR toolkit. Flowgraphs proposed by the agent are designed to run in GNU Radio Companion. *GNU Radio is licensed under the GNU General Public License v3.0 (GPLv3).*

*All original code in this repository is provided under the GNU General Public License v3.0 (GPLv3) unless otherwise specified. References to external tools or websites do not imply endorsement or direct inclusion of their licensed code.*
