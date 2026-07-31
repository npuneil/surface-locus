# 🛰️ Surface Locus — Device Location & Fleet Intelligence (PROTOTYPE)

> ⚠️ **This is a prototype / demo.** Every device, location, geofence, alert and
> metric is **fabricated**. **"Surface Locus in Intune" is a conceptual
> future-state mock-up — it is NOT a shipping Microsoft product.**
> The app does not manage a real device fleet and moves no real data. Branding
> is placeholder only (not official Microsoft / Surface / Intune marks).

A single-file Flask app that shows how **Local AI** (a small language model on
the **Copilot+ Surface NPU** via Foundry Local) accelerates **device
location tracking** across **Zava Health's Seattle corporate campus** — a
**9-building campus on Cedar Lake** (3 buildings on the water) plus
**work-from-home staff**, framed at the enterprise scale of **~123,000 managed
endpoints** (thousands with an unknown location). It shows how far **Microsoft
Intune** goes today, adds an on-device **PII-redaction → predicted-location**
pipeline, pipes results into a **ServiceNow** dispatch mock and a **Lakeside
SysTrack (DEX)** utilization/repurpose report, and mocks up where it could go as
**Surface Locus inside Intune**.

> The 18 devices shown are a **representative sample** — the on-device design is
> meant to scale to all ~123,000 endpoints **without a central location database**.
> Numbers (123k / ~4,200 unknown / ~9,500 underused / $3.1–4.4M savings) are
> illustrative framing; **Zava Health is a fictional demo brand**.

## What it demonstrates

| Tab | Story |
|-----|-------|
| 🗺️ **Fleet Map** | Sample fleet of laptops, 2-in-1s & workstations across 9 corporate buildings on **Cedar Lake** + WFH + a courier in transit, over a 123k-endpoint scale banner. Pins colored by status; a "missing" device drifts to a *last-known / off-network* cluster. |
| 💬 **Ask Locus** | Natural-language fleet Q&A answered **on-device** (phi-3.5-mini on the Surface NPU) with a deterministic **mock fallback**. Routes to fleet/predict/redact/utilization/dispatch/incident/triage skills. |
| 🧠 **On-Device Intelligence** | The pipeline: **raw context → redact PII on-device** (patient↔clinician, MRN, contact) **→ predict location** as a probability distribution — from the redacted signal only. |
| 🎫 **ServiceNow** | Mock ServiceNow: Locus writes the resolved (or predicted) physical location onto the ticket (**before → after**) so field techs can find the ~4,200 unknown-location endpoints. |
| 📊 **Utilization** | Fuses **Lakeside SysTrack (DEX)** utilization with Locus location to flag ~9,500 underused endpoints to reclaim & redeploy (est. $3.1–4.4M/yr avoided). |
| 🪜 **Intune → Locus** | Capability ladder: **Today with Intune** (the realistic ceiling) → **Local AI Acceleration** (this prototype) → **Surface Locus (native)** (future concept, surfaced in Intune + the Surface Management Portal). |
| 🧩 **Locus in Intune** | A mock of an Intune admin-center blade: KPIs, per-building geofences, predictive loss/theft alerts — with a prominent CONCEPT MOCK-UP banner. |
| 🖥️ **Locus in Surface Portal** | A mock of the **Microsoft Surface Management Portal**: Surface device inventory (model / **Location** from Locus / DEX health / warranty) plus location-driven repurpose & refresh actions — CONCEPT MOCK-UP. |
| ⚡ **Local AI Benefits** | Benefits of the on-device approach, tailored to device tracking. |
| 🧭 **8 Forces** | The 8 Forces of Local AI, **triaged** for this use case (Privacy & Sovereignty, Resilience and Latency rank highest). |

## How the "Local AI acceleration" works

```
Browser → Flask (127.0.0.1:5075)
            ├─ /api/fleet /ladder /blade /surface /forces /benefits   → mock data (deterministic)
            ├─ /api/predict /servicenow /utilization          → mock data (deterministic)
            ├─ /api/redact (POST)  → on-device PII redactor (regex + name list)
            └─ /api/ask  → locus_engine.query_stream()
                             ├─ Foundry Local → phi-3.5-mini-instruct-qnn-npu (Surface NPU)
                             └─ deterministic MOCK fallback (no runtime needed)
```

Intune keeps doing identity, compliance and remote lock/wipe; the Local AI
layer adds the **real-time, offline, privacy-preserving** intelligence on top.

## Run

```powershell
# from this folder
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r locus_requirements.txt
python locus_app.py
# open http://127.0.0.1:5075
```

Or use `locus_run.ps1` / `locus_run.bat`.

- **No Foundry Local / NPU?** The app runs fine — the status pill shows
  `on-device: mock` and Ask Locus streams deterministic answers.
- **With Foundry Local** running (`foundry service start`) and a
  `phi-3.5-mini` NPU model cached, the pill flips to `on-device: npu` and
  answers are generated live on the Surface NPU. Click the pill to reconnect.

## Files

| File | Purpose |
|------|---------|
| `locus_app.py` | Flask app + inline HTML/CSS/JS (single-page UI) |
| `locus_engine.py` | Foundry Local (Surface NPU) client with mock fallback |
| `locus_data.py` | All mock data + logic: fleet/campus (9 buildings on Cedar Lake), 123k scale, DEX telemetry, capability ladder, Locus blade, 8 forces, benefits, prompts, mock answers, **on-device `redact_pii()`**, predicted locations, ServiceNow tickets, `utilization_report()` |
| `locus_requirements.txt` | `flask`, `openai` |
| `locus_run.ps1` / `.bat` | Convenience launchers |

## Note on the "8 forces"

The prototype uses an explicit **8 Forces of Local AI** framework (see the 🧭 tab)
— each with its guiding question, triaged High/Medium/Low for this scenario:
Latency, Privacy & Sovereignty, Cost & Scale, Resilience, Throughput at Edge,
Risk Segmentation, Governance Granularity, and Operational Fit. Privacy &
Sovereignty, Resilience and Latency rank highest here.
