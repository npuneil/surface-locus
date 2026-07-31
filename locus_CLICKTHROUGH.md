# Surface Locus — Click-Through Checklist (Zava Health Seattle)
**A shot-by-shot script for a ~4-5 min screen recording (or a live headless walk-through).**
Prototype · mock data · concept mock-up · **Zava Health is a fictional demo brand**.
Pair with `locus_DEMO_SCRIPT.md` for the full narrated version.

---

## Pre-roll (before you hit record)
- [ ] Server up: `python locus_app.py` → console shows `http://127.0.0.1:5075`
- [ ] Optional self-test: `./locus_demo_check.ps1` → **READY** (17 checks)
- [ ] Browser at **http://127.0.0.1:5075**, zoom 100%, window maximized, notifications off
- [ ] Know your engine badge: **npu** (NPU live) or **mock** (deterministic fallback) — both demo fine
- [ ] Tip: tabs deep-link — `…:5075/#intel`, `#snow`, `#util` — handy for jumping straight to a screen

---

## The click sequence

| # | Click / Action | Expected on screen | Say (≤14 words) |
|---|----------------|--------------------|-----------------|
| 1 | Land on **🗺️ Fleet Map** | Scale banner: 123,000 · ~4,200 unknown · ~9,500 underused · 18 shown. Cedar Lake center; 3 lakeside buildings outlined cyan | "Zava Health Seattle — 9 buildings on Cedar Lake, ~123k endpoints, thousands with no known location." |
| 2 | Point at the **MISSING** pin (INT-3302 Coding-Tab-08, bottom-right off-network) | Red dashed pin in "Last-known / off-network (unresolved)" | "This tablet left Cascade Tower and went dark — one of ~4,200 with no location." |
| 3 | Click **🪜 Intune → Locus** (left column) | 3-tier ladder; left column shows coarse/periodic + "~4,200 blank/stale" | "Intune tells you where it *was* — coarse, cloud-bound, and often blank." |
| 4 | Click **🧠 On-Device Intelligence** | Pipeline: Raw → Redact PII → Predict. Redaction + prediction cards | "The heart of it: redact on-device, then predict location." |
| 5 | Click a redaction preset, then **Redact on-device** | Left pane raw (name/MRN/clinician/phone); right pane tokenized `[PATIENT] [MRN] [CLINICIAN] [PHONE]`; removed chips | "Patient↔clinician, MRN, contact — all stripped on the device. Only coarse zone + time survives." |
| 6 | Scroll to **Predicted location** (INT-3302) | Probability bars: 44% Parking & Mobility Hub, 23% off-campus… + rationale | "From the redacted signal only — where it *probably* is, with probability." |
| 7 | (Optional) Click **💬 Ask Locus** → preset "Where is the missing Coding-Tab-08…" | Answer streams token-by-token; badge **npu**/**mock**; routes to *predict* | "Same NPU, conversational — local inference, no cloud round-trip." |
| 8 | Click **🎫 ServiceNow** | 4 tickets; each shows location **before (Unknown/stale) → after (resolved, %)** | "That location is written onto the ticket — techs stop hunting for the device." |
| 9 | Click **📊 Utilization** | KPIs (~9,500 underused, $3.1–4.4M/yr) + table of underused devices w/ recommendation | "Fuse Lakeside SysTrack utilization with location — reclaim ~9,500 idle endpoints." |
| 10 | Click **🧩 Locus in Intune** | Mock Intune blade + dashed CONCEPT banner; geofences + KPIs | "Future state — a Locus blade *inside* Intune. Concept mock-up only." |
| 11 | Click **🖥️ Locus in Surface Portal** | Surface Mgmt Portal mock (teal): device inventory with **Location + DEX health + warranty** + repurpose/refresh actions | "Same intelligence in the Surface admin portal — model, location, health, warranty in one view." |
| 12 | Click **🧭 8 Forces** | 8-forces triage; top 3 = Privacy · Resilience · Latency | "Triaged against the 8 forces — top three: privacy, resilience, latency." |
| 13 | Return to **🗺️ Fleet Map** | Back to the map overview | "Prototype today — but the NPU and Foundry Local are real." |

---

## Recording tips
- **Pace:** on step 5, pause so the audience reads both panes; on step 7, hold the streamed answer until it finishes (~10-15s).
- **Zoom for the hero:** on steps 5-6, zoom the browser to ~125% so redaction tokens + probability bars read clearly on video.
- **Deterministic:** in mock mode every answer/redaction is repeatable — re-click freely if a take stutters.
- **Total runtime:** ~4-5 min. For a 90-sec cut, keep steps 1, 5, 6, 8, 9 only.

## Reset between takes
- Refresh the browser (F5) to clear panes and return to **Fleet Map** (or navigate via `#map`).
- If the NPU dropped to mock mid-demo, click the **status pill** to reconnect — but mock mode is demo-safe, so don't stall over it.

## Honesty line (keep it on screen / say once)
> "This is a **prototype** with **fabricated data**, **Zava Health is a fictional demo brand**. *Surface Locus in Intune* is a **concept mock-up**, not a shipping product — but on-device inference on the Surface NPU via Foundry Local is real."
