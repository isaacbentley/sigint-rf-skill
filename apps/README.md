# SigInt-RF Local Web App

This is a local, fully-offline proof-of-concept (PoC) web application for the **SigInt-RF Skill**. It serves a lightweight web chat interface that allows you to interact with a vision-language model acting as a Signals Intelligence RF Expert.

## Features

- **Local vision model**: Runs **Gemma 4** multimodal model on Apple Silicon using MLX (`mlx-vlm`). No cloud dependencies, API keys, or remote data sharing.
- **Interactive Triage**: Generate demo signals or upload your own IQ files (`.cf32`). The app automatically runs `triage_iq.py` to analyze the capture and feeds the spectral/temporal plots (spectrogram, power envelope, PSD, IQ constellation) directly into the vision model.
- **Markdown Rendering**: Renders and displays structured chat history and assistant explanations with formatted tables, list items, inline code, and diagnostic blocks.
- **Offline Fallback**: Designed with offline operation in mind, using client-side fallback parsing when CDN links for markdown rendering are not accessible.

## Prerequisites

- **Apple Silicon Mac** (M1/M2/M3/M4) is required to run local MLX models.
- **Python**: `>=3.11, <3.14`
- **uv** (recommended) or standard Python package manager.

## Installation

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

Alternatively, you can run it directly using `uv` which automatically handles python versions and dependencies:

```bash
uv run apps/app.py
```

## Running the App

Run the application from the repository root:

```bash
python apps/app.py
```

Once started, open your browser and navigate to:
**http://127.0.0.1:8765**

## Environment Variables

You can configure the application using the following environment variables:

- `SIGINT_MLX_MODEL`: Hugging Face model ID (default: `mlx-community/gemma-4-12B-it-4bit`).
- `SIGINT_MAX_TOKENS`: Maximum reply length (default: `2048`).
- `SIGINT_PORT`: Port to run the HTTP server on (default: `8765`).
- `SIGINT_DEVICE`: MLX execution device, set to `cpu` to force CPU mode and avoid GPU/Metal timeouts (default: `gpu`).
