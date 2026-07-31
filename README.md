# 🛰️ Surface Locus — Device Location & Fleet Intelligence (PROTOTYPE)

> ⚠️ **Prototype / demo only.** Every device, location, geofence, alert and
> metric is **fabricated**. **"Surface Locus in Intune" and the "Surface
> Management Portal" views are conceptual future-state mock-ups — NOT shipping
> Microsoft products.** Branding is placeholder only (not official Microsoft /
> Surface / Intune marks). **Zava Health is a fictional demo brand.**

A single-file Flask app showing how **Local AI** — a small language model on the
**Copilot+ Surface NPU** (via Foundry Local, with a deterministic mock fallback)
— accelerates **device location tracking** across **Zava Health's Seattle
corporate campus** (a **9-building campus on Cedar Lake**, 3 buildings on the
water) plus **work-from-home staff**, at the scale of **~123,000 managed
endpoints**. It shows how far **Microsoft Intune** goes today, then adds an
on-device **PII-redaction → predicted-location** pipeline, a **ServiceNow**
dispatch mock, and a **Lakeside SysTrack (DEX)** utilization/repurpose report —
surfaced as a future-state **Surface Locus** experience in both **Intune** and
the **Surface Management Portal**.

## Quick start

```powershell
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r locus_requirements.txt
python locus_app.py
# open http://127.0.0.1:5075
```

Runs fine with **no NPU** (mock mode). With **Foundry Local** + a cached
`phi-3.5-mini` NPU model, answers generate live on the Surface NPU.

## Docs

| Doc | Purpose |
|-----|---------|
| [`locus_README.md`](locus_README.md) | Full overview: every tab, architecture, files |
| [`locus_DEMO_SCRIPT.md`](locus_DEMO_SCRIPT.md) | Full presenter script (acts, timings, what to SAY / DO) |
| [`locus_CLICKTHROUGH.md`](locus_CLICKTHROUGH.md) | Fast step-by-step click-through cheat sheet |
| [`locus_onepager.pptx`](locus_onepager.pptx) | 7-slide one-pager deck |

## The 8 Forces of Local AI (triaged for this use case)

Scored in the 🧭 tab. Highest-ranked here: **1. Privacy & Sovereignty ·
2. Resilience · 3. Latency** — privacy, resilience and real-time latency
dominate a HIPAA-bound, dead-zone-heavy environment.
