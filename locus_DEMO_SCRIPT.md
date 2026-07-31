# 🎬 Surface Locus — Presenter Demo Script (Zava Health Seattle)

> **Prototype demo.** All data is fabricated and this is **not affiliated with or
> endorsed by Zava Health**. "Surface Locus in Intune" is a **future-state
> concept mock-up**, not a shipping product. Say this out loud at the start and
> again at the future-state tab — it builds trust, not doubt.

**App:** `python locus_app.py` → **http://127.0.0.1:5075**
**Total time:** ~10 min full walkthrough · ~3 min lightning cut (both below)
**One-liner:** *"Intune manages Zava Health's ~123,000 endpoints; Local AI on the Copilot+ Surface NPU lets each device locate and protect itself — instantly, offline, and privately — then pipes clean signal into ServiceNow and asset repurposing."*

---

## 0. Pre-flight (before the audience is watching)

1. Start the server: `python locus_app.py` (or `locus_run.ps1`).
2. Optional — light up the **real NPU**: `foundry service start` with a
   `phi-3.5-mini` NPU model cached, then click the status pill → it flips to
   `on-device: npu`. **If you skip this, the demo still works** — the pill
   shows `mock` and answers stream deterministically. Don't apologize for mock;
   it's the failsafe.
3. Run `locus_demo_check.ps1` — it should print **READY (green)** (17 checks).
4. Open the browser to the **🗺️ Fleet Map** tab. Full-screen it.
5. Presenter hotkeys: **click the status pill** to reconnect the NPU. Tabs are
   deep-linkable (`#intel`, `#snow`, `#util`) if you want to preset a screen.

---

## 1. The hook (45 sec) — Fleet Map tab

**[SAY]**
> "This is Zava Health's corporate campus in Seattle — **nine buildings on Cedar Lake**, three of them right on the water — plus thousands of work-from-home billing, coding and telehealth staff. Across the enterprise that's about **123,000 managed Windows endpoints**. Two questions keep IT and security up at night: *Where is that device right now?* — and for the **thousands with no known location**, *how do we ever find it to fix or reclaim it?*"
>
> "Everything you'll see is a **prototype** with mock data — but the pattern, the silicon, and the on-device model are real."

**[DO]** Gesture at the **scale banner**: 123,000 managed · ~4,200 unknown/stale · ~9,500 underused · 18 shown. Then the map: Cedar Lake in the middle, 3 lakeside buildings (Cascade Tower, Cedar Executive Center, Lakeside Commons) outlined in cyan, 6 inland, and the off-campus lane (transit, WFH, and one red **unresolved** pin).

**[SAY]**
> "We only plot a representative **18 devices** here — the whole point is that this on-device approach **scales to all 123,000 without a central location database**."

---

## 2. Act 1 — "How far Intune goes today" (2 min)

### 2a. The gap (Fleet Map tab)
**[DO]** Point to the red pin in the **"Last-known / off-network (unresolved)"** cluster (bottom-right).

**[SAY]**
> "This red one — **Coding-Tab-08** — left the **Cascade Tower** lakeside lobby at 18:12 and hasn't checked in since. It's an older Intel tablet, **not** enrolled in on-device tracking. The moment it left Wi-Fi, it went dark. Multiply that by the **~4,200** endpoints across the fleet with a blank or stale location, and you have field techs doing truck-rolls just to *find* hardware."

**[DO]** Point to the WFH cluster (top-right, off-campus divider).

**[SAY]**
> "And the WFH laptops? Intune knows the **city** from the sign-in IP — that's it."

### 2b. The ceiling (🪜 Intune → Locus tab, LEFT column only)
**[DO]** Switch to **🪜 Intune → Locus**. Point at the **left** column.

**[SAY]**
> "Standard Intune is excellent at inventory, compliance, Conditional Access, remote lock and wipe. But the location row is **coarse, cloud-dependent, periodic** — and roughly 4,200 endpoints carry a blank or stale location that never cleanly reaches ServiceNow or the DEX tools."

**Land the line:** *"Intune tells you where a device **was** when it last phoned home. We want to know where it **is** — and we want that to be usable downstream."*

---

## 3. Act 2 — "On-device intelligence" (3 min) ⭐ hero moment

### 3a. The pipeline (🧠 On-Device Intelligence tab)
**[DO]** Switch to **🧠 On-Device Intelligence**. Point at the 3-step pipeline: **Raw context → Redact PII (on-device) → Predict location.**

**[SAY]**
> "Here's the heart of it. Endpoints in a health system see sensitive context — *which patient was seen by which clinician*, MRNs, contact info. That is exactly the data you do **not** want streaming to a cloud tracker."

**[DO]** In the **redaction card**, click a preset (e.g. *"Coding tablet — encounter note"*) → click **Redact on-device**.

**[SAY]**
> "Watch the two panes. On the left, the raw record — patient name, MRN, clinician, phone, DOB. On the right, what's allowed to sync: everything sensitive is **tokenized on the device**. The chips show exactly what was removed. All that's kept for location modeling is a **coarse building zone and a time bucket**."

**[DO]** Scroll to the **Predicted location** card. It's showing **INT-3302 · Coding-Tab-08**.

**[SAY]**
> "Now feed *only that redacted signal* into the model. It doesn't just tell us where the device *was* — it predicts where it **probably is**, as a probability distribution: **44% Parking & Mobility Hub**, 23% off-campus, and so on. The rationale is right there — last vector headed northwest from the Cascade lakeside lobby at shift change, no badge read at any exit turnstile since. So dispatch a tech to the **parking deck first**."

**Land the line:** *"Intune tells you where it **was**; Local AI tells you where it **probably is** — and it got there without ever touching a patient or clinician identity."*

### 3b. Ask Locus (💬 Ask Locus tab) — optional reinforcement
**[DO]** Switch to **💬 Ask Locus**. Click preset **"Where is the missing Coding-Tab-08 most likely right now?"** Let it stream.

**[SAY]**
> "Same engine, conversational. phi-3.5-mini on the **Copilot+ Surface Surface NPU** via Foundry Local — token-by-token local inference, no cloud round-trip. Try the redaction and utilization presets too; they all route to the right on-device skill."

---

## 4. Act 3 — "Make it operational" (2.5 min)

### 4a. ServiceNow dispatch (🎫 ServiceNow tab)
**[DO]** Switch to **🎫 ServiceNow**. Point at the **before → after** location cards.

**[SAY]**
> "Insight is worthless if it dies in a dashboard. Locus writes the resolved — or predicted — physical location **onto the ServiceNow ticket**. Look at each card: location **before** was *Unknown* or *stale*; **after**, it's *Parking & Mobility Hub · L2 charging bay 14* at 91% confidence. The field tech now knows exactly where to go — across the ~4,200 unknown-location endpoints. This is a **mock** ServiceNow, but the integration shape is real."

**[DO]** Call out the **INC0459211** lost-asset ticket — it uses the *predicted* location because the device isn't Locus-enrolled.

### 4b. Utilization & repurpose (📊 Utilization tab)
**[DO]** Switch to **📊 Utilization**.

**[SAY]**
> "Same location intelligence, a very different business case. Zava Health already gets device-experience data from **Lakeside SysTrack**. SysTrack tells you a device is **underused** — but 'reclaim it' fails when nobody knows where it physically is. Fuse DEX utilization with Locus location and repurposing becomes actionable: here are underused endpoints, their building, and a recommendation. At fleet scale that's **~9,500 underused endpoints** — an estimated **$3.1M–$4.4M a year** you can avoid spending on new hardware."

**Land the line:** *"The same 'where is it' answer both **finds a lost device** and **reclaims an idle one**."*

---

## 5. Act 4 — "Future state: Locus in Intune **and** the Surface Management Portal" (1.5 min)

**[DO]** Switch to **🧩 Locus in Intune**. Point at the dashed **CONCEPT MOCK-UP** banner first.

**[SAY]**
> "Where could this go? Imagine it lived **natively inside the Intune admin center** as a blade called Surface Locus — **a concept mock-up, not a real product**. Always-on, low-power presence from the NPU sensor hub, under 1% battery. **Per-building geofences** across the nine Cedar Lake buildings and WFH. On-device redaction and predicted location for the ~4,200 unknown endpoints. And it feeds ServiceNow dispatch and DEX repurpose automatically."

**[DO]** Now switch to **🖥️ Locus in Surface Portal** (teal chrome). Point at the **device inventory** table.

**[SAY]**
> "And because we're taking this in-house as a Surface-led solution, the *same* intelligence shows up where Surface admins already work — the **Surface Management Portal**. Each device now has a live **Location** column next to its **DEX health** and **warranty**, so a tech collects a warranty-expiring device on the first visit, and ~9,500 underused Copilot+ Surface devices become repurpose candidates instead of new purchases."

**Land the line:** *"Intune keeps doing identity and compliance. Locus adds the real-time, offline, privacy-preserving layer on top — surfaced in **both** Intune and the Surface Management Portal. It **complements** them, it doesn't replace them."*

---

## 6. Close — benefits + the 8 forces (1 min)

**[DO]** Switch to **⚡ Local AI Benefits** (scroll once), then **🧭 8 Forces**.

**[SAY]**
> "Why on-device? For **this** use case — location across a health-system campus plus WFH — five of the eight forces score High: **Privacy & Sovereignty** (the patient↔clinician link is redacted on-device, never a cloud honeypot), **Resilience** (parking decks, lakefront blind spots, flaky home links), **Latency** (catch it the instant it moves), **Risk Segmentation** (sensitive data stays local; only clean signal syncs) and **Operational Fit** (it drops into the Intune, Surface portal and ServiceNow you already run). Cost, throughput and governance matter too — but privacy, resilience and latency are the headline."

**[DO]** Point at the top-3 banner.

**[SAY]** (final)
> "One more time — this is a **prototype**, mock data, Zava Health is fictional. But the silicon is real, the NPU is real, and Foundry Local runs today. The gap between this mock and a shipping capability is smaller than it looks."

---

## ⚡ Lightning cut (3 minutes)

1. **Fleet Map (40s)** — "Zava Health Seattle, 9 buildings on Cedar Lake + WFH, ~123k endpoints, ~4,200 with no known location. This red one, Coding-Tab-08, left Cascade and went dark."
2. **On-Device Intelligence (80s)** — redact preset → **Redact on-device** ("patient↔clinician stripped on the device"), then the prediction card ("44% Parking & Mobility Hub — from the redacted signal only").
3. **ServiceNow (25s)** — "That location is written onto the ticket — Unknown → Parking bay 14 at 91%. Techs stop hunting."
4. **Utilization (20s)** — "Same signal + Lakeside SysTrack = reclaim ~9,500 underused, ~$3.1–4.4M/yr."
5. **8 Forces (15s)** — "Privacy, resilience, latency are the top three of eight. Prototype — but the NPU's real."

---

## 🛡️ Objection handling / anticipated Q&A

- **"Is any of this tracking real?"** → No — a **prototype with fabricated data**, Zava Health is fictional. The NPU, Foundry Local, and phi-3.5-mini are real and run today.
- **"Where do the 123k / 4,200 / 9,500 numbers come from?"** → Illustrative framing for the demo. Swap in the customer's real Intune/Lakeside figures for a live engagement.
- **"Is 'Surface Locus in Intune' a real product?"** → No — a **future-state concept mock-up**, labeled that way in the UI on purpose.
- **"Doesn't this replace Intune / Lakeside / ServiceNow?"** → No. Intune stays the system of record; Lakeside stays the DEX source; ServiceNow stays the workflow. Locus is the **on-device location layer** that feeds them.
- **"How is location determined?"** → In the prototype it's mocked. In practice, on-device signal fusion (Wi-Fi/BLE/badge/sensor-hub) reasoned about locally — raw signals and PHI stay on the device; only redacted, policy-scoped output syncs.
- **"What about PHI / HIPAA / staff surveillance?"** → That's *why* it's on-device. The **redaction step** strips patient↔clinician links before anything leaves the device; only de-identified zone + time and alerts sync. Scope geofences to devices, not people.
- **"How does the prediction work without PHI?"** → It consumes only the **redacted** movement features — coarse zone + time bucket + learned per-device pattern. No patient/clinician identity, no raw coordinates.
- **"Battery cost of always-on?"** → The point of the **Surface low-power sensor hub** — presence at ~<1% battery vs. CPU polling.
- **"Why not just do this in the cloud?"** → Latency, reliability (RF dead zones), and privacy — don't build a cloud honeypot of patient/staff movement.

---

## 🎯 Audience-specific angles (swap the emphasis)

- **Endpoint management / IT admin:** lead with the 🪜 ladder and "complements Intune"; stress no rip-and-replace and the native admin-center concept.
- **Security / CISO:** lead with the redaction pipeline + the missing-device prediction + 8 Forces; stress reduced cloud PHI footprint and tamper-resistance.
- **Service desk / field ops:** lead with **🎫 ServiceNow** — "your techs stop hunting for ~4,200 devices."
- **IT asset management / finance:** lead with **📊 Utilization** — reclaim ~9,500 underused, ~$3.1–4.4M/yr avoided.
- **Executive:** lead with the scale banner + the pipeline; stress privacy, analyst-time saved, and hardware dollars reclaimed.

---

## 🔑 Phrases worth memorizing

- *"Intune tells you where it **was**; Local AI tells you where it **is** — with a probability."*
- *"The patient↔clinician link is redacted **on the device** — only de-identified signal ever syncs."*
- *"The same 'where is it' answer both finds a lost device and reclaims an idle one."*
- *"It **complements** Intune, Lakeside and ServiceNow — it doesn't replace them."*
- *"Prototype today — but the NPU and Foundry Local are real."*
