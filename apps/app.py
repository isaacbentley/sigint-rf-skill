#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = ["mlx-vlm>=0.6", "numpy", "scipy", "matplotlib"]
# ///
"""
Local, fully-offline PoC for the SigInt-RF skill — a single file.

Runs **Gemma 4** (multimodal) on Apple MLX via mlx-vlm, uses SKILL.md as the
system prompt so the model acts as the "Signals Intelligence RF Expert", and
serves a small web chat UI. Because Gemma 4 has vision, it doesn't just read the
triage *report* — it actually **sees** the triage dashboard image (PSD,
spectrogram, IQ constellation, power envelope) and cross-validates, exactly as
the skill's Explainable-AI rules intend. No cloud, no API keys.

Run (recommended — uv handles Python + deps):
    uv run app.py

Or with your own environment:
    pip install "mlx-vlm>=0.6" numpy scipy matplotlib
    python app.py

Then open http://127.0.0.1:8765

Env vars:
    SIGINT_MLX_MODEL   HF model id   (default: mlx-community/gemma-4-12B-it-4bit)
    SIGINT_MAX_TOKENS  max reply len (default: 2048)
    SIGINT_PORT        web port      (default: 8765)

Requires an Apple Silicon Mac (MLX). The 12B 4-bit model with speculative drafter is ~15 GB, downloaded
once on first chat; the UI, demo and triage work immediately while it loads.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import queue
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# Prevent macOS GPU watchdog timeouts by relaxing the Metal context store timeout.
# This must be set in the environment before the process starts. If not set,
# we re-execute the script with the environment variable configured.
if os.environ.get("AGX_RELAX_CDM_CTXSTORE_TIMEOUT") != "1":
    os.environ["AGX_RELAX_CDM_CTXSTORE_TIMEOUT"] = "1"
    try:
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to re-execute. GPU watchdog timeouts may occur: {e}\n")

ROOT = Path(__file__).resolve().parent.parent
TOOLS = ROOT / "tools"
CAPTURES = ROOT / "captures"
SKILL_MD = ROOT / "SKILL.md"

CAPTURES.mkdir(parents=True, exist_ok=True)

MODEL_ID = os.environ.get("SIGINT_MLX_MODEL", "mlx-community/gemma-4-12B-it-4bit")
MAX_TOKENS = int(os.environ.get("SIGINT_MAX_TOKENS", "2048"))
PORT = int(os.environ.get("SIGINT_PORT", "8765"))

# ----------------------------------------------------------------------------- model
_model = None
_drafter = None
_processor = None
_config = None
_load_error: str | None = None
_task_queue = queue.Queue()
_lock = threading.Lock()


def make_friendly_error(e: Exception) -> str:
    err_type = type(e).__name__
    err_msg = str(e)
    
    if "mlx" in err_msg.lower() and (err_type in ("ModuleNotFoundError", "ImportError")):
        return (
            "Model dependencies are not installed. "
            "Please run 'pip install -r apps/requirements.txt' or start the server using 'uv run apps/app.py'."
        )
    
    if "metal" in err_msg.lower() or "command buffer" in err_msg.lower() or "gpu" in err_msg.lower():
        return (
            "Metal GPU processing timed out or failed. "
            "Please try restarting the server with the CPU fallback enabled: "
            "'SIGINT_DEVICE=cpu uv run apps/app.py'"
        )
        
    if "connection" in err_msg.lower() or "404" in err_msg.lower() or "gemma-4-12b" in err_msg.lower() or ("timeout" in err_msg.lower() and "huggingface" in err_msg.lower()):
        return (
            "Failed to download model weights from Hugging Face. "
            "Please verify your internet connection, ensure you have ~15 GB of disk space, and try again."
        )
        
    return f"{err_type}: {err_msg}"


def get_model():
    """Lazy-load the model so the UI/demo/triage work before the ~15GB download."""
    global _model, _drafter, _processor, _config, _load_error
    if _model is None and _load_error is None:
        with _lock:
            if _model is None and _load_error is None:
                try:
                    import mlx.core as mx
                    
                    # Monkey-patch mx.device_info to prevent KeyError in mlx-vlm when running on CPU
                    _orig_device_info = mx.device_info
                    def _patched_device_info():
                        info = _orig_device_info()
                        if "max_recommended_working_set_size" not in info:
                            try:
                                metal_info = mx.metal.device_info()
                                if "max_recommended_working_set_size" in metal_info:
                                    info["max_recommended_working_set_size"] = metal_info["max_recommended_working_set_size"]
                                else:
                                    info["max_recommended_working_set_size"] = 16 * 1024 * 1024 * 1024
                            except Exception:
                                info["max_recommended_working_set_size"] = 16 * 1024 * 1024 * 1024
                        return info
                    mx.device_info = _patched_device_info

                    device_name = os.environ.get("SIGINT_DEVICE", "gpu").lower()
                    if device_name == "cpu":
                        mx.set_default_device(mx.cpu)
                        print("[mlx] Device forced to CPU", flush=True)
                    from mlx_vlm import load
                    from mlx_vlm.utils import load_config
                    print(f"[mlx-vlm] loading {MODEL_ID} (first run downloads weights)…", flush=True)
                    _model, _processor = load(MODEL_ID)
                    _config = load_config(MODEL_ID)
                    
                    # Load the MTP Drafter model for Speculative Decoding
                    drafter_id = os.environ.get("SIGINT_MLX_DRAFTER")
                    if drafter_id is None and "gemma-4-12b-it" in MODEL_ID.lower():
                        drafter_id = "mlx-community/gemma-4-12B-it-assistant-4bit"
                    if drafter_id:
                        print(f"[mlx-vlm] loading MTP drafter model {drafter_id}…", flush=True)
                        _drafter, _ = load(drafter_id)
                        print("[mlx-vlm] drafter ready", flush=True)
                        
                    print("[mlx-vlm] model engine ready", flush=True)
                except Exception as e:
                    _load_error = make_friendly_error(e)
                    print(f"[mlx-vlm] load failed: {_load_error}", flush=True)
    if _load_error:
        raise RuntimeError(f"model unavailable: {_load_error}")
    return _model, _drafter, _processor, _config


_cached_system_prompt = None

def system_prompt() -> str:
    global _cached_system_prompt
    if _cached_system_prompt is not None:
        return _cached_system_prompt
        
    txt = SKILL_MD.read_text(encoding="utf-8")
    if txt.startswith("---"):
        parts = txt.split("---", 2)
        if len(parts) == 3:
            txt = parts[2].strip()
    
    # Optimize prompt size for the chat UI to prevent GPU timeouts
    # Strip tool reference tables, git/pr rules, and external research logs
    lines = txt.split("\n")
    optimized_lines = []
    skip = False
    skip_headers = [
        "## Web Research Protocol",
        "## Agent & Developer Context Guides",
        "## 🙏 Acknowledgements",
        "## Signal Library Directory Structure",
        "## Signal Identification Reference Matrix"
    ]
    for line in lines:
        if any(line.startswith(h) for h in skip_headers):
            skip = True
        elif line.startswith("## ") and skip:
            skip = False
        if not skip:
            optimized_lines.append(line)
    _cached_system_prompt = "\n".join(optimized_lines).strip()
    return _cached_system_prompt


def generate(messages: list[dict], images: list[str]):
    """Stream a reply via the main thread task queue."""
    result_q = queue.Queue()
    cancel_event = threading.Event()
    _task_queue.put((messages, images, result_q, cancel_event))
    try:
        while True:
            try:
                chunk = result_q.get(timeout=30)
            except queue.Empty:
                yield " "
                continue
            if chunk is None:
                break
            if isinstance(chunk, Exception):
                raise chunk
            yield chunk
    finally:
        cancel_event.set()


def _safe_repo_path(rel: str) -> Path | None:
    p = (ROOT / rel).resolve()
    return p if p.is_relative_to(ROOT) and p.exists() else None


# ----------------------------------------------------------------------------- tools
def run_demo() -> dict:
    out = CAPTURES / "mystery_capture.cf32"
    subprocess.run(
        [sys.executable, str(TOOLS / "generate_demo_signal.py"),
         "--type", "gmsk", "--duration", "0.5", "--sample_rate", "2048000",
         "--output_file", str(out)],
        check=True, cwd=ROOT,
    )
    return {"path": str(out.relative_to(ROOT)), "rate": 2048000}


def run_triage(target: Path, rate: int, mode="overview", offset_hz=0.0, channel_bw=None) -> dict:
    import uuid
    run_id = uuid.uuid4().hex[:8]
    report_name = f"triage_report_{run_id}.md"
    plot_name = f"triage_plot_{run_id}.png"
    
    cmd = [
        sys.executable, str(TOOLS / "triage_iq.py"), 
        "--file", str(target), 
        "--rate", str(rate),
        "--mode", mode
    ]
    if mode == "triage":
        if offset_hz != 0.0:
            cmd.extend(["--offset-hz", str(offset_hz)])
        if channel_bw is not None:
            cmd.extend(["--channel-bw", str(channel_bw)])
            
    subprocess.run(cmd, check=True, cwd=CAPTURES)
    
    report = CAPTURES / "triage_report.md"
    plot = CAPTURES / "triage_plot.png"
    if report.exists(): report.rename(CAPTURES / report_name)
    if plot.exists(): plot.rename(CAPTURES / plot_name)
    
    final_report = CAPTURES / report_name
    final_plot = CAPTURES / plot_name
    
    report_text = final_report.read_text(encoding="utf-8") if final_report.exists() else ""
    
    if mode == "overview":
        meta_file = target.with_suffix(".sigmf-meta")
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                if "annotations" in meta and meta["annotations"]:
                    report_text += "\n\n## SigMF Metadata Annotations\n"
                    for i, ann in enumerate(meta["annotations"]):
                        report_text += f"**Annotation {i+1}**:\n"
                        for k, v in ann.items():
                            report_text += f"  - `{k}`: {v}\n"
            except Exception as e:
                print(f"Failed to parse sigmf-meta: {e}")
                
    return {
        "report": report_text,
        "plot": f"/api/plot?f={plot_name}",
        "image": str(final_plot) if final_plot.exists() else None,
        "capture": target.name,
    }


def run_demod(target: Path, rate: int, mode: str, symbol_rate: float, offset_hz: float, channel_bw: float | None = None) -> dict:
    import uuid
    run_id = uuid.uuid4().hex[:8]
    plot_name = f"demod_diagnostics_{run_id}.png"
    plot_path = CAPTURES / plot_name
            
    cmd = [
        sys.executable, str(TOOLS / "explainable_demod.py"),
        "--file", str(target),
        "--rate", str(rate),
        "--mode", mode,
        "--plot-path", str(plot_path),
        "--verbose"
    ]
    if mode in ("fsk", "psk", "qam"):
        cmd.extend(["--symbol-rate", str(symbol_rate)])
    if offset_hz != 0.0:
        cmd.extend(["--offset-hz", str(offset_hz)])
    if channel_bw is not None:
        cmd.extend(["--channel-bw", str(channel_bw)])
        
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    
    stdout = res.stdout or ""
    stderr = res.stderr or ""
    log_content = stdout
    if res.returncode != 0:
        log_content += f"\n\n⚠️ Demodulator exited with code {res.returncode}\n{stderr}"
        
    return {
        "log": log_content,
        "plot": f"/api/demod_plot?f={plot_name}",
        "image": str(plot_path) if plot_path.exists() else None,
        "capture": target.name,
    }


# ----------------------------------------------------------------------------- http
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _bytes(self, code, ctype, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._bytes(code, "application/json", json.dumps(obj).encode())

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            self._bytes(200, "text/html; charset=utf-8", HTML.encode())
        elif path == "/api/health":
            self._json(200, {"model": MODEL_ID, "loaded": _model is not None, "error": _load_error})
        elif path == "/api/plot":
            u = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(u.query)
            fname = (qs.get("f") or [""])[0]
            if not fname:
                return self._json(400, {"error": "missing f="})
            p = CAPTURES / Path(fname).name
            if p.exists():
                self._bytes(200, "image/png", p.read_bytes())
            else:
                self._json(404, {"error": "no triage plot yet"})
        elif path == "/api/demod_plot":
            u = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(u.query)
            fname = (qs.get("f") or [""])[0]
            if not fname:
                return self._json(400, {"error": "missing f="})
            p = CAPTURES / Path(fname).name
            if p.exists():
                self._bytes(200, "image/png", p.read_bytes())
            else:
                self._json(404, {"error": "no demod diagnostics plot yet"})
        elif path == "/static/marked.min.js":
            p = ROOT / "apps" / "marked.min.js"
            if p.exists():
                self._bytes(200, "application/javascript", p.read_bytes())
            else:
                self._json(404, {"error": "marked.min.js not found locally"})
        else:
            self._json(404, {"error": "not found"})

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        path, qs = u.path, urllib.parse.parse_qs(u.query)
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else b""

        if path == "/api/chat":
            try:
                data = json.loads(body)
                messages = data["messages"]
            except Exception:
                return self._json(400, {"error": "JSON body with messages[] required"})
            images = []
            if data.get("image"):
                p = _safe_repo_path(data["image"])
                if p:
                    images = [str(p)]
            try:
                get_model()  # trigger load / surface errors before streaming
            except RuntimeError as e:
                return self._json(503, {"error": str(e)})
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            try:
                for chunk in generate(messages, images):
                    self.wfile.write(chunk.encode())
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            except Exception as e:
                try:
                    self.wfile.write(f"\n\n⚠️ Generation Error: {e}".encode())
                    self.wfile.flush()
                except Exception:
                    pass

        elif path == "/api/demo":
            try:
                self._json(200, run_demo())
            except subprocess.CalledProcessError as e:
                self._json(500, {"error": f"demo generation failed: {e}"})

        elif path == "/api/triage":
            try:
                ctype = self.headers.get("Content-Type", "")
                if ctype == "application/json":
                    data = json.loads(body)
                    target = (ROOT / data.get("path", "")).resolve()
                    if not target.is_relative_to(ROOT) or not target.exists():
                        return self._json(404, {"error": "Invalid or missing file path"})
                    rate = int(data.get("rate", 2048000))
                    mode = data.get("mode", "triage")
                    offset_hz = float(data.get("offset_hz", 0.0))
                    channel_bw = data.get("channel_bw")
                    if channel_bw is not None:
                        channel_bw = float(channel_bw)
                    try:
                        self._json(200, run_triage(target, rate, mode=mode, offset_hz=offset_hz, channel_bw=channel_bw))
                    except subprocess.CalledProcessError as e:
                        self._json(500, {"error": f"triage failed: {e}"})
                    return

                rate = int((qs.get("rate") or ["2048000"])[0])
            except ValueError:
                return self._json(400, {"error": "Invalid rate value"})
            name = (qs.get("name") or [""])[0]
            path_param = (qs.get("path") or [""])[0]
            if body and name:
                target = CAPTURES / Path(name).name
                try:
                    target.write_bytes(body)
                except OSError as e:
                    return self._json(500, {"error": f"Failed to save file: {e}"})
            elif path_param:
                target = (ROOT / path_param).resolve()
                if not target.is_relative_to(ROOT):
                    return self._json(400, {"error": "path must be inside the repo"})
            else:
                return self._json(400, {"error": "upload a file (?name=) or pass ?path="})
            if not target.exists():
                return self._json(404, {"error": f"capture not found: {target.name}"})
            try:
                self._json(200, run_triage(target, rate, mode="overview"))
            except subprocess.CalledProcessError as e:
                self._json(500, {"error": f"triage failed: {e}"})

        elif path == "/api/demod":
            try:
                data = json.loads(body)
                try:
                    rate = int(data.get("rate", 2048000))
                    symbol_rate = float(data.get("symbol_rate", 250000))
                    offset_hz = float(data.get("offset_hz", 0.0))
                except ValueError:
                    return self._json(400, {"error": "Invalid numerical parameters"})
                mode = data.get("mode", "fsk")
                path_param = data.get("path", "")
                
                if path_param:
                    target = (ROOT / path_param).resolve()
                else:
                    target = CAPTURES / "mystery_capture.cf32"
                    
                if not target.is_relative_to(ROOT):
                    return self._json(400, {"error": "path must be inside the repo"})
                if not target.exists():
                    return self._json(404, {"error": f"capture not found: {target.name}"})
                    
                self._json(200, run_demod(target, rate, mode, symbol_rate, offset_hz))
            except Exception as e:
                self._json(500, {"error": f"demodulation failed: {e}"})

        else:
            self._json(404, {"error": "not found"})


# ----------------------------------------------------------------------------- ui
HTML = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Signals Intelligence RF Expert — local</title>
<script src="/static/marked.min.js"></script>
<style>
 :root{--bg:#0b0f14;--panel:#121821;--ink:#e6edf3;--muted:#8b98a5;--accent:#3fb950;
       --accent2:#1f6feb;--user:#1f6feb22;--bot:#161b22;--line:#222b36;}
 *{box-sizing:border-box;} body{margin:0;font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
   background:var(--bg);color:var(--ink);height:100vh;display:flex;flex-direction:column;}
 header{padding:12px 18px;border-bottom:1px solid var(--line);background:var(--panel);display:flex;align-items:center;gap:12px;flex-wrap:wrap;}
 header h1{font-size:16px;margin:0;font-weight:600;} header .sub{color:var(--muted);font-size:12px;}
 #status{margin-left:auto;font-size:12px;color:var(--muted);display:flex;align-items:center;gap:6px;}
 .dot{width:9px;height:9px;border-radius:50%;background:#8b98a5;}
 .dot.ok{background:var(--accent);}.dot.busy{background:#d29922;}.dot.err{background:#f85149;}
 #toolbar{padding:10px 18px;border-bottom:1px solid var(--line);display:flex;gap:10px;align-items:center;flex-wrap:wrap;}
 button,.btn{background:var(--bot);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:7px 12px;font-size:13px;cursor:pointer;}
 button:hover{border-color:var(--accent2);} button:disabled{opacity:.5;cursor:not-allowed;}
 .rate{width:96px;} input[type=number]{background:var(--bot);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:7px;}
 #chat{flex:1;overflow-y:auto;padding:18px;display:flex;flex-direction:column;gap:14px;}
 .msg{max-width:820px;padding:12px 16px;border-radius:12px;word-wrap:break-word;}
 .msg.user{align-self:flex-end;background:var(--user);border:1px solid #1f6feb55;}
 .msg.bot{align-self:flex-start;background:var(--bot);border:1px solid var(--line);}
 .msg p{margin:0 0 12px 0;line-height:1.6;}
 .msg p:last-child{margin-bottom:0;}
 .msg code{background:rgba(255,255,255,0.08);padding:3px 6px;border-radius:6px;font-family:"SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;font-size:13px;color:#ff9e64;}
 .msg pre{background:#0d1117;border:1px solid var(--line);border-radius:8px;padding:12px;overflow:auto;margin:12px 0;}
 .msg pre code{background:none;padding:0;border-radius:0;font-size:12px;color:inherit;white-space:pre;}
 .msg ul, .msg ol{margin:0 0 12px 0;padding-left:22px;}
 .msg li{margin-bottom:6px;}
 .msg table{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px;border:1px solid var(--line);}
 .msg th, .msg td{border:1px solid var(--line);padding:8px 12px;text-align:left;}
 .msg th{background:rgba(255,255,255,0.06);font-weight:600;}
 .msg tr:nth-child(even){background:rgba(255,255,255,0.02);}
 .msg h1, .msg h2, .msg h3, .msg h4{margin:18px 0 10px 0;font-weight:600;line-height:1.3;color:#f0f6fc;}
 .msg h1{font-size:1.4em;border-bottom:1px solid var(--line);padding-bottom:6px;}
 .msg h2{font-size:1.25em;}
 .msg h3{font-size:1.1em;}
 .msg blockquote{margin:12px 0;padding:0 12px;border-left:4px solid var(--accent2);color:var(--muted);}
 .msg .who{font-size:11px;color:var(--muted);margin-bottom:5px;text-transform:uppercase;letter-spacing:.5px;}
 .msg img{max-width:100%;border-radius:8px;margin-top:10px;border:1px solid var(--line);}
 details{margin-top:8px;} summary{cursor:pointer;color:var(--muted);font-size:12px;}
 details pre{background:#0d1117;border:1px solid var(--line);border-radius:8px;padding:10px;overflow:auto;max-height:280px;font-size:12px;}
 #composer{display:flex;gap:10px;padding:14px 18px;border-top:1px solid var(--line);background:var(--panel);}
 #input{flex:1;background:var(--bot);color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:11px 13px;font:inherit;resize:none;max-height:160px;}
 #send{background:var(--accent2);border-color:var(--accent2);color:#fff;font-weight:600;padding:0 20px;}
 .hint{color:var(--muted);font-size:12px;} a{color:var(--accent2);}
</style></head><body>
 <header>
   <h1>📻 Signals Intelligence RF Expert</h1>
   <span class="sub">local · MLX · Gemma 4 👁 vision · fully offline</span>
   <span id="status"><span class="dot" id="dot"></span><span id="statustext">checking…</span></span>
 </header>
 <div id="toolbar">
   <button id="btnDemo">🎲 Generate demo capture</button>
   <label class="btn">📂 Triage a capture<input id="file" type="file" hidden/></label>
   <label class="hint">rate <input class="rate" id="rate" type="number" value="2048000" step="1000"/> Hz</label>
   <span class="hint">— the model <b>sees</b> the triage plots. Or just chat below.</span>
 </div>
 <div id="chat"></div>
 <div id="composer">
   <textarea id="input" rows="1" placeholder="Ask the RF expert…  (e.g. &quot;what lives on 433 MHz?&quot;)"></textarea>
   <button id="send">Send</button>
 </div>
<script>
if (window.marked) {
  marked.setOptions({
    gfm: true,
    breaks: true
  });
}
function renderMarkdown(text) {
  if (window.marked && typeof window.marked.parse === 'function') {
    return marked.parse(text);
  }
  return text.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])).replace(/\n/g, '<br/>');
}
const chat=document.getElementById('chat'),input=document.getElementById('input'),sendBtn=document.getElementById('send');
const messages=[]; let busy=false; let currentController = null;
function bubble(role,text=''){const el=document.createElement('div');el.className='msg '+(role==='user'?'user':'bot');
 const who=document.createElement('div');who.className='who';who.textContent=role==='user'?'you':'rf expert';
 const body=document.createElement('div');body.innerHTML=renderMarkdown(text);el.append(who,body);chat.appendChild(el);chat.scrollTop=chat.scrollHeight;return body;}
function note(t){const b=bubble('bot',t);b.parentElement.style.opacity=.85;return b;}
async function refreshStatus(){try{const h=await(await fetch('/api/health')).json();const d=document.getElementById('dot'),t=document.getElementById('statustext');
 if(h.error){d.className='dot err';t.textContent='model error';t.parentElement.title=h.error;}else if(h.loaded){d.className='dot ok';t.textContent=h.model+' · ready';t.parentElement.title='';}
 else{d.className='dot';t.textContent=h.model+' · loads on first message';t.parentElement.title='';}}catch{document.getElementById('statustext').textContent='server offline';document.getElementById('dot').className='dot err';}}
async function streamChat(image, loadingText) {
  if (currentController) { currentController.abort(); currentController = null; }
  const myController = new AbortController(); currentController = myController;
  busy=true; sendBtn.disabled=true;
  const d=document.getElementById('dot'), t=document.getElementById('statustext');
  d.className='dot busy'; t.textContent='thinking… (first reply may download/load the model)';
  const body=bubble('bot', loadingText ? `_🤖 ${loadingText}_ ▍` : '▍');
  let parsedParams = null;
  try {
    const resp=await fetch('/api/chat', { signal: currentController.signal,
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({messages, image:image||null})
    });
    if(!resp.ok) {
      let msg=await resp.text();
      try{const errObj=JSON.parse(msg);msg=errObj.error||msg;}catch(e){}
      body.innerHTML=renderMarkdown('⚠️ '+msg); return null;
    }
    const reader=resp.body.getReader(), dec=new TextDecoder();
    let acc=''; let lastRender=0;
    while(true) {
      const {done,value}=await reader.read();
      if(done) break;
      acc+=dec.decode(value,{stream:true});
      const now = Date.now();
      if (now - lastRender > 50) {
        body.innerHTML=renderMarkdown(acc+'▍');
        chat.scrollTop=chat.scrollHeight;
        lastRender=now;
      }
    }
    body.innerHTML=renderMarkdown(acc);
    chat.scrollTop=chat.scrollHeight;
    messages.push({role:'assistant',content:acc});
    
    const jsonMatch = acc.match(/```json\s*(\{[\s\S]*?\})\s*```/);
    if (jsonMatch) {
      try { parsedParams = JSON.parse(jsonMatch[1]); } catch(e) {}
    }
  } catch(e) {
    if(e.name !== 'AbortError') body.innerHTML=renderMarkdown('⚠️ '+e);
  } finally {
    if (currentController === myController) {
      currentController = null;
      busy=false; sendBtn.disabled=false; refreshStatus();
    }
  }
  return parsedParams;
}
async function send(text){if(busy||!text.trim())return;messages.push({role:'user',content:text});bubble('user',text);await streamChat(null, 'Thinking…');}
sendBtn.onclick=()=>{const v=input.value;input.value='';input.style.height='auto';send(v);};
input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();sendBtn.onclick();}});
input.addEventListener('input',()=>{input.style.height='auto';input.style.height=input.scrollHeight+'px';});
document.getElementById('btnDemo').onclick=async()=>{if(busy)return;const n=note('🎲 Generating a demo capture (GMSK burst with a hidden payload)…');
 try{const res=await fetch('/api/demo',{method:'POST'});const r=await res.json();
  if(r.error){n.innerHTML=renderMarkdown('⚠️ '+r.error);return;}
  n.innerHTML=renderMarkdown(`✅ Wrote ${r.path} @ ${r.rate} Hz. Running overview…`);await overview({path:r.path,rate:r.rate});}
 catch(e){n.innerHTML=renderMarkdown('⚠️ '+e);}};
document.getElementById('file').onchange=async e=>{const f=e.target.files[0];if(!f)return;await overview({file:f,rate:+document.getElementById('rate').value});e.target.value='';};

let lastCapture = {};

async function overview({file,path,rate}){if(busy)return;const n=note('📡 Running wideband overview…');
 try{let url,opts;if(file){url=`/api/triage?name=${encodeURIComponent(file.name)}&rate=${rate||2048000}`;opts={method:'POST',body:file};}
  else{url=`/api/triage?path=${encodeURIComponent(path)}&rate=${rate||2048000}`;opts={method:'POST'};}
  const r=await(await fetch(url,opts)).json();if(r.error){n.innerHTML=renderMarkdown('⚠️ '+r.error);return;}
  lastCapture = { path: file ? `captures/${file.name}` : path, rate: rate || 2048000, name: r.capture };
  
  const el=n.parentElement;n.innerHTML=renderMarkdown(`📡 Wideband overview complete for ${r.capture}. Handing to the AI…`);
  const det=document.createElement('details');det.innerHTML='<summary>view raw overview report</summary><pre>'+
   r.report.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))+'</pre>';el.appendChild(det);
  const imgA=document.createElement('a');imgA.href=r.plot+'&t='+Date.now();imgA.target='_blank';const img=document.createElement('img');img.src=imgA.href;img.style.cursor='pointer';imgA.appendChild(img);el.appendChild(imgA);
  const ask='Here is the wideband overview report from triage_iq.py for the capture `' + r.capture + 
   '`, and the attached overview high-res waterfall image. Look at the plots and walk me through what this signal is. ' +
   'If there are multiple signals visible in the waterfall or in the metadata annotations, you MUST isolate a specific signal using triage mode first before demodulating. Output a JSON block like:
```json
{"action": "triage", "offset_hz": 25000000, "channel_bw": 20000000}
```
' +
   'If it is a single signal, you can directly output a JSON block to run the explainable demodulator:
```json
{"action": "demod", "mode": "fsk", "symbol_rate": 250000, "offset_hz": -50000, "channel_bw": 25000000}
```
Valid modes are: fsk, ook, psk, qam, analog_fm, analog_am, analog_video.

'+r.report;
  
  messages.push({role:'user',content:ask});bubble('user','📡 Analyze the wideband overview for '+r.capture);
  const params = await streamChat(r.image, 'Reading and analyzing overview + spectral plots…');
  handleAiAction(params);
 }
 catch(e){if(e.name !== 'AbortError') n.innerHTML=renderMarkdown('⚠️ '+e);}}

function handleAiAction(params) {
  if (!params || !params.action) return;
  if (params.action === 'triage') {
    executeTriage(params);
  } else if (params.action === 'demod') {
    executeDemod(params);
  }
}

async function executeTriage(params) {
  if (busy) return;
  const n = note(`🔬 AI zooming in on channel (offset=${params.offset_hz} Hz, bw=${params.channel_bw} Hz)…`);
  try {
    const payload = { ...lastCapture, mode: 'triage', offset_hz: params.offset_hz, channel_bw: params.channel_bw };
    const resp = await fetch('/api/triage', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const r = await resp.json();
    if (r.error) { n.innerHTML = renderMarkdown('⚠️ ' + r.error); return; }
    
    const el = n.parentElement;
    n.innerHTML = renderMarkdown(`🔬 Triage isolated channel on ${r.capture}. Returning specific stats to AI…`);
    const det = document.createElement('details'); det.innerHTML = '<summary>view isolated triage report</summary><pre>' + r.report.replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c])) + '</pre>'; el.appendChild(det);
    const imgA = document.createElement('a'); imgA.href = r.plot + '&t=' + Date.now(); imgA.target = '_blank'; const img = document.createElement('img'); img.src = imgA.href; img.style.cursor = 'pointer'; imgA.appendChild(img); el.appendChild(imgA);
    
    const ask = 'Here is the highly detailed isolated triage report for the channel you requested: 

' + r.report + 
                '

Analyze these specific metrics. Based on this, output the final demodulation parameters:
```json
{"action": "demod", "mode": "fsk", "symbol_rate": 250000, "offset_hz": ' + params.offset_hz + ', "channel_bw": ' + params.channel_bw + '}
```';
    messages.push({ role: 'user', content: ask });
    bubble('user', `🔬 Analyze isolated channel for ${r.capture}`);
    
    const nextParams = await streamChat(r.image, 'Reading isolated channel report…');
    handleAiAction(nextParams);
  } catch (e) {
    if (e.name !== 'AbortError') n.innerHTML = renderMarkdown('⚠️ ' + e);
  }
}

async function executeDemod(params) {
  if (busy) return;
  const n = bubble('bot', `⚡ AI triggered explainable demodulation (mode=${params.mode.toUpperCase()}, symbol_rate=${params.symbol_rate} Hz, offset=${params.offset_hz} Hz)…`);
  const statusBox = n.parentElement;
  
  busy = true; sendBtn.disabled = true;
  const d = document.getElementById('dot'), t = document.getElementById('statustext');
  d.className = 'dot busy'; t.textContent = 'demodulating…';
  
  try {
    const payload = { ...lastCapture, mode: params.mode, symbol_rate: params.symbol_rate, offset_hz: params.offset_hz, channel_bw: params.channel_bw };
    const resp = await fetch('/api/demod', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    const r = await resp.json();
    if (r.error) { statusBox.innerHTML = `<div class="who">System Assistant</div><p>⚠️ <b>Demodulation failed:</b> ${r.error}</p>`; return; }
    
    statusBox.innerHTML = `
      <div class="who">System Assistant</div>
      <p><b>⚡ Demodulation complete for ${r.capture}!</b> Here is the diagnostic output:</p>
      <details><summary>view raw demodulator output log</summary><pre>${r.log.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}</pre></details>
    `;
    if (r.image) {
      const imgA = document.createElement('a'); imgA.href = r.plot + '&t=' + Date.now(); imgA.target = '_blank'; const img = document.createElement('img'); img.src = imgA.href; img.style.cursor = 'pointer'; imgA.appendChild(img); statusBox.appendChild(imgA);
    }
    chat.scrollTop = chat.scrollHeight;
    
    const validationPrompt = `I have run the explainable demodulator on the capture \`${r.capture}\` with these parameters:
- Mode: ${params.mode.toUpperCase()}
- Frequency Offset: ${params.offset_hz} Hz

Here is the demodulator diagnostics output log and the generated diagnostic plots.
Walk me through the validation of this demodulation:
1. If this is a digital mode (FSK/PSK/OOK), is the eye diagram actually wide open and the clock recovery variance peaked? Or is it a noisy, unsynchronized mess?
2. If this is an analog mode (FM/AM video/audio), does the baseband show clear structure (sync pulses, periodic lines, structured spectrogram) or just random noise?
3. Does the output look like a successful recovery of actual signal structure, or just random entropy? Be extremely wary of false positives.`;

    messages.push({ role: 'user', content: validationPrompt });
    bubble('user', `🔬 Analyze explainable demodulation results for ${r.capture}`);
    await streamChat(r.image, 'Reading and validating demodulation diagnostics plot…');
  } catch (e) {
    statusBox.innerHTML = `<div class="who">System Assistant</div><p>⚠️ <b>Error:</b> ${e}</p>`;
  } finally {
    busy = false; sendBtn.disabled = false; refreshStatus();
  }
}
refreshStatus();setInterval(refreshStatus,4000);
note("👋 Hi! I'm your local RF triage assistant — a vision model running entirely on this Mac. Click “Generate demo capture” to try the full pipeline with no radio (I'll actually look at the plots), upload your own IQ file, or just ask me anything about signals.");
</script></body></html>"""


def main():
    print(f"Signals Intelligence RF Expert (local, vision) → http://127.0.0.1:{PORT}")
    print(f"Model: {MODEL_ID}  (override with SIGINT_MLX_MODEL)")
    
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    
    # Preload and warmup in MAIN thread
    try:
        model, drafter, processor, config = get_model()
        print("[mlx-vlm] warming up KV cache and compiling shaders…", flush=True)
        from mlx_vlm import stream_generate
        from mlx_vlm.prompt_utils import apply_chat_template
        convo = [{"role": "user", "content": "hi"}]
        prompt = apply_chat_template(processor, config, convo, num_images=0)
        kwargs = {"max_tokens": 1}
        if drafter is not None:
            kwargs["draft_model"] = drafter
            kwargs["draft_kind"] = "mtp"
        list(stream_generate(model, processor, prompt, image=[], **kwargs))
        print("[mlx-vlm] warmup complete!", flush=True)
    except Exception as e:
        print(f"[mlx-vlm] warmup failed: {e}", flush=True)

    # Worker loop in main thread
    while True:
        try:
            messages, images, result_q, cancel_event = _task_queue.get(timeout=1.0)
        except queue.Empty:
            continue
        except KeyboardInterrupt:
            break
            
        try:
            model, drafter, processor, config = get_model()
            from mlx_vlm import stream_generate
            from mlx_vlm.prompt_utils import apply_chat_template
            convo = [{"role": "system", "content": system_prompt()}] + messages
            prompt = apply_chat_template(processor, config, convo, num_images=len(images))
            kwargs = {"max_tokens": MAX_TOKENS}
            if drafter is not None:
                kwargs["draft_model"] = drafter
                kwargs["draft_kind"] = "mtp"
            
            for chunk in stream_generate(model, processor, prompt, image=images, **kwargs):
                if cancel_event.is_set():
                    break
                text = getattr(chunk, "text", "")
                if text:
                    result_q.put(text)
            result_q.put(None)
        except Exception as e:
            result_q.put(e)
            result_q.put(None)


if __name__ == "__main__":
    main()
