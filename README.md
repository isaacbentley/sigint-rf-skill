# SigInt RF Agentic Skill 📻🤖

Have you ever stared at a raw IQ signal capture or a software-defined radio (SDR) waterfall plot and wished your AI assistant could instantly tell you what protocol it is, how to demodulate it, or write the exact Python/GNU Radio script to decode it? 

`sigint-rf-skill` is built to do exactly that! It is a structured **AI Agentic Skill** and registry compiling RF signal specifications, triage guidelines, and demodulation instructions. By loading this repository as a Developer Agentic Skill, you instantly equip your favorite AI assistants (like Claude Code and Google Antigravity) with a comprehensive RF signal library, triage matrices, and digital signal processing heuristics. Instead of manually looking up channel frequencies, allocation tables, or struggling with demodulation mathematics, your AI assistant can guide you through the triage process, write clean decoding code, and run diagnostics automatically.

---

## 🤖 Installing the AI Skill

This repository is designed from the ground up as an **Agentic Skill** (a tool and context bundle) for developer AI agents. By loading `sigint-rf-skill`, your AI assistant becomes a specialist in Software Defined Radio (SDR) and RF signals intelligence.

### 🚀 Install as a Skill (any coding agent)

The recommended path for any terminal-capable agent — Claude Code, Gemini / Google Antigravity, GitHub Copilot, Cursor, and more. Paste the prompt below; each agent installs the skill using **its own** native mechanism, so it works regardless of platform:

> **Install prompt:**
>
> Install the SigInt-RF skill from `https://github.com/isaacbentley/sigint-rf-skill.git`:
> 1. **Clone** the repo into your platform's skill/plugin directory if you have one, otherwise a stable local path. Claude Code → `~/.claude/skills/sigint-rf-skill`; Gemini / Antigravity → your plugins/extensions directory; Copilot / Cursor (no skill registry) → clone locally and add `SKILL.md` to your project or global instructions.
> 2. **Register** `SKILL.md` as a skill / system prompt via your native mechanism; if you don't have one, load `SKILL.md` into context for this session.
> 3. **Install the Python tool dependencies:** Set up a local Python virtual environment (`python3 -m venv venv` and activate it) or use `uv`, then install dependencies: `pip install -r <clone>/tools/requirements.txt` (or run tools via `uv run tools/<tool_name>.py`).
> 4. **Confirm** by reading `SKILL.md`'s frontmatter, then tell me where you installed it and how to update it later with `git -C <clone> pull`.

---

## 🚀 Quick Start

You don't need to be a radio engineer to use this. Once the skill is installed, you just **talk to your AI agent in plain language** — it runs the radio tools for you, looks at the signal, and explains what it found.

> 🔌 **Brand new to SDR?** No problem — and no hardware required to start. See the [Hardware Guide](HARDWARE.md) for when you're ready to buy a radio.

### Talk to your agent 🗣️

Talk to your agent like a knowledgeable friend at the radio bench. For example:

| You say… | …and the agent |
|---|---|
| *"I don't have a radio yet — make me a practice signal to play with."* | Generates a demo capture (with a hidden `0xDEADBEEF` message) so you can try everything. |
| *"I've got a capture at `captures/mystery_capture.cf32` — what is it?"* | Figures out the frequency, bandwidth, and modulation, and explains how it knows (with plots). |
| *"Can you pull the data out of it?"* | Walks through the decoding step by step and recovers the payload. |
| *"Something weird is on 433 MHz — can you scan and grab it?"* | Runs a wideband scan, captures the strongest signal, and triages it (needs an SDR). |

Be as casual or as specific as you like. Ask it to *"explain it like I'm new to this,"* *"show me the waterfall,"* or *"what could someone do with this signal?"* — it adapts to you.

### What happens next? 🎉

The agent handles the signal processing behind the scenes, picks the right decoders, and checks in with you before each step. Ask *"why?"*, take it deeper, or just enjoy watching the mystery unravel.

> 🔧 **Curious what's running under the hood?** The exact tools and commands the agent uses are documented in [templates/agent_context/](templates/agent_context/) and [SKILL.md](SKILL.md) — handy if you ever want to run a step yourself.

---

## 💻 Local Offline Web UI

A local offline web UI — a proof-of-concept that runs Gemma on Apple Silicon (MLX), reads `SKILL.md` as its system prompt, and lets you generate demo signals, upload captures, and chat with the model in the browser — lives on the [`web-app`](https://github.com/isaacbentley/sigint-rf-skill/tree/web-app) branch (see its `apps/` directory).

---

## 🌟 Key Features

* **LLM-First Design**: Teaches AI agents to recognize and decode signals without manual math, using structured prompts and heuristics ([SKILL.md](SKILL.md) and `triage_hints.md` files).
* **Automated IQ Triage**: Analyzes raw captures using [tools/triage_iq.py](tools/triage_iq.py) to extract key spectral parameters (center frequency, bandwidth, SNR, temporal patterns, and autocorrelation) and compiles Markdown triage reports optimized for LLMs.
* **Agentic Context Guides**: Features dedicated guides under [templates/agent_context/](templates/agent_context/) (API guidelines, JSON metrics, and GNU Radio boilerplate) to help agents seamlessly control SDR receiver tools.
* **Web Search & Automated PR Flow**: Escalates low-confidence matches to sigidwiki/FCC databases. Proposes new signal definitions and submits Pull Requests linked to new GitHub Issues (referencing [.github/ISSUE_TEMPLATE/new-signal-request.md](.github/ISSUE_TEMPLATE/new-signal-request.md)) after operator confirmation.
* **Signal Library**: Standardizes specifications and triage parameters for common drone, IoT, aviation, and telemetry signals.
* **SDR Receiver Focus**: Tailors receiver tools ([tools/discover_and_capture.py](tools/discover_and_capture.py) and [tools/explainable_demod.py](tools/explainable_demod.py)) specifically for automated SDR capture and demodulation pipelines.

---

## 📂 Directory Layout

```
sigint-rf-skill/
├── README.md                 # This file
├── SKILL.md                  # System instruction/prompt definition for LLM Agentic Skills
├── templates/
│   ├── signal_template.md    # Template for documenting and adding new RF signal types
│   └── agent_context/        # Agent-facing API instructions and templates
│       ├── README.md         # Ingestion guide and step-by-step workflow
│       ├── triage_guide.md   # CLI arguments and JSON metrics mappings for triage_iq.py
│       └── ...               # Additional demodulation and code generation guides
├── tools/
│   ├── discover_and_capture.py  # Automated wideband scan → capture → triage pipeline
│   ├── triage_iq.py             # Python IQ analysis and prompt generator
│   └── ...                      # Additional explainable demodulators and test utilities
└── signals/
    ├── dji_ocusync/          # Example signal family (spec.md + triage_hints.md)
    ├── lora/                 # Example IoT signal family
    ├── ...                   # Additional signal definitions (ADS-B, TPMS, AIS, etc.)
    └── modulations/          # Fundamental RF Modulation specifications
        ├── ook_ask/          # Example base modulation (spec.md + triage_hints.md)
        └── ...               # Additional modulation schemas (AM, FSK, PSK, QAM, etc.)
```

---

## 🧰 Available Tools

You'll rarely call these yourself — your agent runs them for you when you ask. They're listed here for the curious and for contributors:

| Tool | Description |
|---|---|
| [tools/discover_and_capture.py](tools/discover_and_capture.py) | Automated wideband scan → peak detection → IQ capture → triage pipeline using `rtl_power` and `rtl_sdr` |
| [tools/triage_iq.py](tools/triage_iq.py) | Extracts spectral, temporal, and autocorrelation features from raw IQ files; generates markdown reports and diagnostic plots |
| [tools/explainable_demod.py](tools/explainable_demod.py) | Step-by-step explainable demodulator (FSK/OOK, FM/AM audio, PSK/QAM, LoRa, OFDM/SC-FDMA, analog video/FM/AM) with diagnostic plots |
| [tools/generate_demo_signal.py](tools/generate_demo_signal.py) | Synthesizes a practice IQ capture (GMSK/FSK/FM burst, or an NTSC/PAL analog-video FPV signal with a matching SigMF) so you can try the pipeline with no SDR |

> 🧪 **Tests**: [tools/test_workflow.py](tools/test_workflow.py) exercises the end-to-end synth → triage → demod pipeline; [tools/test_read.py](tools/test_read.py) is a fast regression for IQ format decoding (cf32/ci16/cu8/ci8) and the corrupt-capture guard.

---

## 🙏 Acknowledgements, References & Licensing

This project is built upon the incredible work of the open-source Software Defined Radio (SDR) community. We acknowledge and credit the following resources:

* **[Signal Identification Wiki (sigidwiki.com)](https://www.sigidwiki.com/)**: The definitive community-driven database of radio signals. Our triage matrices and web escalation protocols direct agents to reference their extensive catalog. *Sigidwiki content is available under Creative Commons Attribution-ShareAlike.*
* **[RTL-SDR Blog (rtl-sdr.com)](https://www.rtl-sdr.com/)**: For extensive community guides, tool repositories, and accessible hardware that makes this domain possible.
* **[rfhs / rfctf-sdr-tools & rfhs-wiki](https://github.com/rfhs)**: We reference GNU Radio receiver templates (e.g., ZMQ, NBFM, USB) and challenge architectures from the `rfctf-sdr-tools` repository. 
  - *License*: `rfctf-sdr-tools` is released under the **BSD 3-Clause License** (Copyright (c) 2020, rfhs).
* **[GNU Radio](https://www.gnuradio.org/)**: The premier open-source SDR toolkit. Flowgraphs proposed by the agent are designed to run in GNU Radio Companion. *GNU Radio is licensed under the GNU General Public License v3.0 (GPLv3).*

*All original code in this repository is provided under the GNU General Public License v3.0 (GPLv3) unless otherwise specified. References to external tools or websites do not imply endorsement or direct inclusion of their licensed code.*
