"""
locus_engine.py — On-device inference for the Surface Locus prototype.

Pipeline: Copilot+ Surface NPU (phi-3.5-mini-instruct-qnn-npu via Foundry
Local) → deterministic mock fallback.

Design contract (matches the other Local AI showcases in this workspace):
  * ALL text generation goes through `engine.query_stream(system, prompt, module)`
    so the metrics footer never lies.
  * If Foundry Local isn't reachable or no NPU/CPU model can be warmed, the
    engine silently falls back to the deterministic MOCK_RESPONSES so the demo
    never dead-ends on a machine without the runtime.

The live path is intentionally best-effort and fully wrapped in try/except:
the guaranteed, always-correct path is the mock. That keeps the prototype
demoable on any laptop while still lighting up the real Surface NPU when the
runtime is present.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from typing import Generator, Optional

from locus_data import MOCK_RESPONSES

# Foundry Local alias preferences (small "reasoning" role), NPU first.
SMALL_PREFERENCES = [
    ("phi-3.5-mini", "NPU"),
    ("phi-3-mini-128k", "NPU"),
    ("qwen2.5-1.5b", "NPU"),
    ("qwen2.5-7b", "NPU"),
]


@dataclass
class Metrics:
    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_ms: float = 0.0
    device: str = "mock"
    model: str = "none"
    live: bool = False
    loading: bool = False

    @property
    def avg_ms(self) -> float:
        return self.total_ms / max(self.requests, 1)

    @property
    def tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def record(self, ms: float, out_toks: int, in_toks: int = 0) -> None:
        self.requests += 1
        self.output_tokens += max(0, int(out_toks))
        self.input_tokens += max(0, int(in_toks))
        self.total_ms += ms

    def to_dict(self) -> dict:
        return {
            "requests": self.requests,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "tokens": self.tokens,
            "avg_ms": round(self.avg_ms, 1),
            "device": self.device,
            "model": self.model,
            "live": self.live,
            "loading": self.loading,
        }


# ── Foundry Local discovery helpers ──────────────────────────────────────

def _http_get_json(url: str, timeout: float = 4.0) -> Optional[dict]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def _http_get(url: str, timeout: float = 600.0) -> Optional[dict]:
    """GET returning a small status dict. /openai/load/<alias> is GET-only on
    current Foundry Local builds and blocks until the model is warm."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return {"status": r.status}
    except Exception as e:
        return {"_error": f"{type(e).__name__}: {e}"}


def _discover_endpoint() -> Optional[str]:
    """Best-effort discovery of the live Foundry Local inference endpoint."""
    env = os.environ.get("FOUNDRY_ENDPOINT")
    if env:
        cand = env.rstrip("/")
        if _http_get_json(cand + "/v1/models") is not None:
            return cand

    # Ask Windows which port the Inference.Service.Agent is actually listening
    # on — the CLI sometimes reports a stale/management port.
    try:
        ps = (
            "Get-NetTCPConnection -State Listen -LocalAddress 127.0.0.1 "
            "-ErrorAction SilentlyContinue | ForEach-Object { "
            "  $p = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue; "
            "  if ($p -and $p.ProcessName -match 'Inference\\.Service\\.Agent') { $_.LocalPort } "
            "} | Select-Object -First 1"
        )
        out = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True, text=True, timeout=8,
        ).stdout.strip()
        if out.isdigit():
            cand = f"http://127.0.0.1:{out}"
            if _http_get_json(cand + "/v1/models", timeout=3) is not None:
                return cand
    except Exception:
        pass

    # Fall back to parsing the CLI output.
    for args in (["foundry", "service", "status"], ["foundry", "service", "ps"]):
        try:
            out = subprocess.run(args, capture_output=True, text=True, timeout=8).stdout
            for m in re.finditer(r"http://127\.0\.0\.1:\d+", out or ""):
                cand = m.group(0)
                if _http_get_json(cand + "/v1/models", timeout=3) is not None:
                    return cand
        except Exception:
            continue
    return None


def _resolve_loaded_model(ep: str, alias: str, prefer_device: str) -> Optional[tuple]:
    j = _http_get_json(ep + "/v1/models")
    models = (j or {}).get("data", []) or []
    norm = alias.lower()
    matches = []
    for m in models:
        mid = (m.get("id") or "").lower()
        if not mid or not mid.startswith(norm):
            continue
        if "qnn-npu" in mid:
            dev = "NPU"
        elif "qnn-gpu" in mid or "generic-gpu" in mid:
            dev = "GPU"
        else:
            dev = "CPU"
        matches.append((m["id"], dev))
    if not matches:
        return None
    matches.sort(key=lambda t: 0 if t[1] == prefer_device else 1)
    return matches[0]


# ── Engine ───────────────────────────────────────────────────────────────

class LocusEngine:
    def __init__(self, autoload: bool = True):
        self.metrics = Metrics()
        self._client = None            # openai.OpenAI
        self._endpoint: Optional[str] = None
        self._model_id: Optional[str] = None
        self._device: Optional[str] = None
        self._lock = threading.Lock()
        if autoload and os.environ.get("LOCUS_SKIP_LOAD") != "1":
            self.metrics.loading = True
            threading.Thread(target=self._load_model, daemon=True).start()

    @property
    def is_live(self) -> bool:
        return self._client is not None and self._model_id is not None

    def _load_model(self) -> None:
        try:
            try:
                from openai import OpenAI
            except Exception:
                print("[Locus] openai package not installed — mock only")
                return

            ep = _discover_endpoint()
            if not ep:
                print("[Locus] Foundry Local not found — mock only")
                return
            self._endpoint = ep
            print(f"[Locus] Foundry Local at {ep}")

            for alias, prefer_dev in SMALL_PREFERENCES:
                print(f"[Locus] loading {alias} ...")
                load_res = _http_get(f"{ep}/openai/load/{alias}", timeout=600)
                if load_res and "_error" in load_res:
                    print(f"[Locus]   load: {load_res['_error']}")

                resolved = None
                for _ in range(6):
                    resolved = _resolve_loaded_model(ep, alias, prefer_dev)
                    if resolved:
                        break
                    time.sleep(2)
                if not resolved:
                    continue

                model_id, dev = resolved
                try:
                    client = OpenAI(base_url=f"{ep}/v1", api_key="not-needed", timeout=120.0)
                    r = client.chat.completions.create(
                        model=model_id,
                        messages=[{"role": "user", "content": "Hi"}],
                        max_tokens=4, stream=False,
                    )
                    _ = r.choices[0].message.content or ""
                except Exception as e:
                    print(f"[Locus] {alias} smoke test failed: {e}")
                    continue

                self._client = client
                self._model_id = model_id
                self._device = dev
                self.metrics.model = alias
                self.metrics.device = {"NPU": "npu", "GPU": "gpu"}.get(dev, "cpu")
                self.metrics.live = True
                print(f"[Locus] ✅ {alias} on {dev} ready")
                return

            print("[Locus] no model could be warmed — mock mode")
        finally:
            self.metrics.loading = False

    def reconnect(self) -> bool:
        self._client = None
        self._model_id = None
        self.metrics.live = False
        self.metrics.loading = True
        self._load_model()
        return self.metrics.live

    # ── inference ────────────────────────────────────────────────────────

    def _foundry_stream(self, system_msg: str, prompt: str) -> Generator[str, None, None]:
        with self._lock:
            start = time.time()
            out_toks = 0
            approx_in = max(1, len((system_msg + " " + prompt).split()))
            try:
                stream = self._client.chat.completions.create(
                    model=self._model_id,
                    messages=[
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=1024, temperature=0.3, stream=True,
                )
                for event in stream:
                    delta = ""
                    try:
                        delta = event.choices[0].delta.content or ""
                    except Exception:
                        delta = ""
                    if not delta:
                        continue
                    out_toks += max(1, len(delta.split()))
                    yield delta
            finally:
                self.metrics.record((time.time() - start) * 1000.0, out_toks, approx_in)

    def query_stream(self, system_msg: str, prompt: str, module: str) -> Generator[str, None, None]:
        """Stream inference: Foundry Local (NPU) → mock. Never raises."""
        if self.is_live:
            try:
                got = False
                for chunk in self._foundry_stream(system_msg, prompt):
                    got = True
                    yield chunk
                if got:
                    return
            except Exception as e:
                print(f"[Locus] live inference failed: {e} — mock fallback")
        yield from self._mock_stream(module)

    def _mock_stream(self, module: str) -> Generator[str, None, None]:
        resp = MOCK_RESPONSES.get(module) or MOCK_RESPONSES["general"]
        words = resp.split(" ")
        self.metrics.record(0.0, len(words), max(1, len(module.split("_"))))
        for i, word in enumerate(words):
            yield word + " "
            if i < 8:
                time.sleep(0.02)
            elif "|" in word or "---" in word:
                time.sleep(0.05)
            else:
                time.sleep(0.035)
