"""
locus_data.py — Mock data + prompts for the Surface Locus prototype,
tailored to Zava Health's Seattle corporate campus (Cedar Lake).

⚠️  PROTOTYPE / DEMO ONLY. Every endpoint, location, geofence, ticket, metric,
patient/clinician name and dollar figure below is FABRICATED for illustration.
"Surface Locus" as an Intune blade is a conceptual future-state mock-up —
it is NOT a shipping Microsoft product. Zava Health is a fictional demo
brand, not a real health system. No real patient, staff, or device data is
used. Building names are illustrative; only a handful of devices are shown as a
representative sample of a ~123,000-endpoint fleet.

Modules:
  * FLEET_SCALE / CAMPUS         — Zava Health scale framing + campus/lake map meta
  * FLEET_ZONES / FLEET_DEVICES  — 9 corporate buildings (3 on Cedar Lake) + WFH + transit
  * DEX (Lakeside SysTrack)       — supplemental utilization/health per device
  * redact_pii / REDACTION_*      — on-device PII redaction (patient <-> clinician)
  * PREDICTED_LOCATIONS           — probabilistic "where is it now" from redacted signals
  * SERVICENOW_TICKETS            — Locus fills the blank CMDB location for field techs
  * UTILIZATION_REPORT            — find + repurpose underused hardware (DEX + location)
  * CAPABILITY_LADDER / LOCUS_BLADE / EIGHT_FORCES / LOCAL_AI_BENEFITS
  * SYSTEM_PROMPTS / MOCK_RESPONSES / MODULE_ROUTES — the "Ask Locus" SLM tab
"""

from __future__ import annotations

import re


# ─────────────────────────────────────────────────────────────────────────
#  Zava Health fleet-scale framing.  The handful of devices below are a
#  representative SAMPLE — the story is that this scales to every endpoint.
# ─────────────────────────────────────────────────────────────────────────

FLEET_SCALE = {
    "total_endpoints": 123000,
    "unknown_location": 4200,        # thousands with blank / stale physical location
    "stale_or_unknown_pct": 3.4,
    "underused_estimate": 9500,      # DEX-flagged chronically underused endpoints
    "annual_repurpose_savings": "$3.1M–$4.4M",
    "sample_shown": 18,
    "note": (
        "Illustrative figures. The 18 devices shown are a representative sample of "
        "Zava Health's ~123,000 managed Windows endpoints — the same on-device "
        "approach is designed to scale to the entire fleet without a central "
        "location database."
    ),
}

# Campus + Cedar Lake geometry for the inline 1000x560 SVG map.
CAMPUS = {
    "name": "Zava Health Seattle — Corporate Campus",
    "subtitle": "on the shores of Cedar Lake",
    "lake": {"cx": 330, "cy": 305, "rx": 150, "ry": 135, "label": "Cedar Lake"},
    "divider_x": 790,
}


# ─────────────────────────────────────────────────────────────────────────
#  Campus map zones = 9 corporate buildings (3 on Cedar Lake) + offsite.
#  kind: "campus" | "offsite".  lakeside: True for the 3 lakefront buildings.
# ─────────────────────────────────────────────────────────────────────────

FLEET_ZONES = [
    # ── 3 buildings around Cedar Lake ──
    {"id": "cascade",   "name": "Cascade Tower",             "kind": "campus", "lakeside": True,  "x": 330, "y": 120},
    {"id": "exec",       "name": "Cedar Executive Center",   "kind": "campus", "lakeside": True,  "x": 100, "y": 305},
    {"id": "commons",    "name": "Lakeside Commons",           "kind": "campus", "lakeside": True,  "x": 330, "y": 495},
    # ── 6 other corporate buildings ──
    {"id": "innovation", "name": "Innovation & Digital",       "kind": "campus", "lakeside": False, "x": 560, "y": 120},
    {"id": "revcycle",   "name": "Revenue Cycle Center",       "kind": "campus", "lakeside": False, "x": 700, "y": 120},
    {"id": "telehealth", "name": "Care Mgmt & Telehealth",     "kind": "campus", "lakeside": False, "x": 560, "y": 305},
    {"id": "zhu",        "name": "Zava Health University",     "kind": "campus", "lakeside": False, "x": 700, "y": 305},
    {"id": "biomed",     "name": "Central Support / Biomed",   "kind": "campus", "lakeside": False, "x": 560, "y": 490},
    {"id": "parking",    "name": "Parking & Mobility Hub",     "kind": "campus", "lakeside": False, "x": 700, "y": 490},
    # ── offsite ──
    {"id": "transit",    "name": "In Transit",                 "kind": "offsite", "lakeside": False, "x": 875, "y": 150},
    {"id": "wfh",        "name": "WFH / Remote",               "kind": "offsite", "lakeside": False, "x": 875, "y": 380},
]

# status ∈ compliant | at_risk | offline | missing | off_campus
# dex = supplemental Lakeside SysTrack (DEX) signals: health 0-100, util % (usage
# intensity), active_hrs (avg daily active hours), boot_s (boot time seconds).
FLEET_DEVICES = [
    # ── Cascade Tower (lakeside flagship / leadership) ──
    {"id": "SFX-1042", "name": "Exec-Laptop-04",     "type": "Laptop",              "owner": "Campus leadership",      "zone": "cascade",   "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 78, "status": "compliant",  "risk": 8,  "last_seen": 2,  "locus": True,  "dex": {"health": 92, "util": 61, "active_hrs": 6.4, "boot_s": 9},  "note": "Nominal. Lakefront office, docked."},
    {"id": "SFX-1077", "name": "Facilities-2in1-11", "type": "2-in-1 Tablet",       "owner": "Facilities (Cascade)",  "zone": "cascade",   "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 41, "status": "at_risk",    "risk": 63, "last_seen": 6,  "locus": True,  "dex": {"health": 74, "util": 55, "active_hrs": 5.1, "boot_s": 12}, "note": "Left Cascade lakeside perimeter twice today; geofence flag."},

    # ── Cedar Executive Center (lakeside / HR + corporate) ──
    {"id": "INT-1410", "name": "HR-Workstation-6",   "type": "Workstation",         "owner": "People / HR",            "zone": "exec",       "silicon": "Intel Core",   "os": "Win 11 23H2", "battery": 100,"status": "compliant",  "risk": 10, "last_seen": 6,  "locus": False, "dex": {"health": 80, "util": 22, "active_hrs": 2.6, "boot_s": 21}, "note": "Low utilization — repurpose candidate. Intel, not Locus-enrolled."},

    # ── Lakeside Commons (lakeside / shared services + conference) ──
    {"id": "SFX-2210", "name": "Conf-Room-PC-02",    "type": "Conference PC",       "owner": "Lakeside Commons AV",    "zone": "commons",    "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 90, "status": "compliant",  "risk": 5,  "last_seen": 1,  "locus": True,  "dex": {"health": 88, "util": 12, "active_hrs": 1.1, "boot_s": 10}, "note": "Conf Rm C-210. Very low utilization — reclaim candidate."},

    # ── Innovation & Digital (IT / cyber / endpoint eng) ──
    {"id": "SFX-4110", "name": "SecOps-Laptop-3",    "type": "Laptop",              "owner": "Cybersecurity",          "zone": "innovation", "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 63, "status": "offline",    "risk": 34, "last_seen": 28, "locus": True,  "dex": {"health": 90, "util": 70, "active_hrs": 7.2, "boot_s": 8},  "note": "In shielded server room / RF dead zone — on-device presence held last-known zone."},
    {"id": "SFX-4111", "name": "IT-Depot-PC-1",      "type": "Workstation",         "owner": "Endpoint engineering",   "zone": "innovation", "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 84, "status": "compliant",  "risk": 11, "last_seen": 3,  "locus": True,  "dex": {"health": 94, "util": 66, "active_hrs": 6.9, "boot_s": 9},  "note": "Nominal."},

    # ── Revenue Cycle Center (billing + medical coding — PHI-heavy) ──
    {"id": "INT-3301", "name": "Coding-Tab-07",      "type": "Clinical Tablet",     "owner": "Revenue cycle",          "zone": "revcycle",   "silicon": "Intel Core",   "os": "Win 11 23H2", "battery": 22, "status": "at_risk",    "risk": 58, "last_seen": 9,  "locus": False, "dex": {"health": 61, "util": 48, "active_hrs": 4.4, "boot_s": 26}, "note": "Low battery + idle in a non-work corridor. Holds patient<->coder associations. Intel, not Locus-enrolled."},
    {"id": "SFX-5001", "name": "Billing-WOW-2",      "type": "Workstation-on-Wheels","owner": "Patient financial svcs","zone": "revcycle",   "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 71, "status": "compliant",  "risk": 7,  "last_seen": 2,  "locus": True,  "dex": {"health": 89, "util": 72, "active_hrs": 7.5, "boot_s": 9},  "note": "Nominal. High utilization."},

    # ── Care Management & Telehealth ──
    {"id": "SFX-6002", "name": "CareMgmt-Tablet-5",  "type": "Clinical Tablet",     "owner": "Care management",        "zone": "telehealth", "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 88, "status": "compliant",  "risk": 6,  "last_seen": 1,  "locus": True,  "dex": {"health": 91, "util": 64, "active_hrs": 6.1, "boot_s": 8},  "note": "Nominal."},

    # ── Zava Health University (education / simulation) ──
    {"id": "INT-7003", "name": "ZHU-Lab-PC-9",       "type": "Workstation",         "owner": "ZHU simulation lab",     "zone": "zhu",        "silicon": "Intel Core",   "os": "Win 11 23H2", "battery": 100,"status": "compliant",  "risk": 14, "last_seen": 5,  "locus": False, "dex": {"health": 77, "util": 18, "active_hrs": 2.0, "boot_s": 24}, "note": "Seasonal lab PC — chronically underused. Repurpose candidate."},

    # ── Central Support / Biomed-HTM ──
    {"id": "SFX-1210", "name": "Biomed-Laptop-2",    "type": "Laptop",              "owner": "Biomed / HTM",           "zone": "biomed",     "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 52, "status": "compliant",  "risk": 16, "last_seen": 7,  "locus": True,  "dex": {"health": 86, "util": 58, "active_hrs": 5.6, "boot_s": 10}, "note": "Nominal."},

    # ── Parking & Mobility Hub (facilities rounds) ──
    {"id": "SFX-8004", "name": "Mobility-Tablet-2",  "type": "2-in-1 Tablet",       "owner": "Facilities rounds",      "zone": "parking",    "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 33, "status": "compliant",  "risk": 18, "last_seen": 4,  "locus": True,  "dex": {"health": 79, "util": 15, "active_hrs": 1.4, "boot_s": 11}, "note": "L2 charging bay 14. Roaming rounds; low utilization — reassign candidate."},

    # ── Missing (between buildings, off-network) ──
    {"id": "INT-3302", "name": "Coding-Tab-08",      "type": "Clinical Tablet",     "owner": "Revenue cycle",          "zone": "between",    "silicon": "Intel Core",   "os": "Win 11 23H2", "battery": 55, "status": "missing",    "risk": 88, "last_seen": 74, "locus": False, "dex": {"health": 58, "util": 39, "active_hrs": 3.8, "boot_s": 27}, "note": "Last seen leaving Cascade Tower lakeside lobby 18:12; no check-in since. Holds patient<->coder PHI. NOT Locus-enrolled — no on-device fallback."},

    # ── In transit (interoffice courier) ──
    {"id": "SFX-1310", "name": "Courier-Tablet-1",   "type": "2-in-1 Tablet",       "owner": "Interoffice courier",    "zone": "transit",    "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 61, "status": "off_campus",  "risk": 29, "last_seen": 4,  "locus": True,  "dex": {"health": 84, "util": 44, "active_hrs": 4.0, "boot_s": 10}, "note": "Between corporate campus and the data center on an approved courier-route geofence."},

    # ── WFH / remote (4) ──
    {"id": "INT-9005", "name": "RevCycle-Laptop-14", "type": "Laptop",              "owner": "Rev-cycle (WFH)",        "zone": "wfh",        "silicon": "Intel Core",   "os": "Win 11 23H2", "battery": 67, "status": "off_campus",  "risk": 44, "last_seen": 12, "locus": False, "dex": {"health": 70, "util": 52, "active_hrs": 5.0, "boot_s": 23}, "note": "WFH; last IP geolocated 34mi away. No live location (Intune coarse only). Intel, not Locus-enrolled."},
    {"id": "SFX-9006", "name": "Coder-Laptop-22",    "type": "Laptop",              "owner": "Med coder (WFH)",        "zone": "wfh",        "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 58, "status": "at_risk",    "risk": 71, "last_seen": 3,  "locus": True,  "dex": {"health": 82, "util": 63, "active_hrs": 6.2, "boot_s": 9},  "note": "WFH; on-device flag: opened in an unrecognized location, off usual hours."},
    {"id": "SFX-9007", "name": "CareNav-Laptop-31",  "type": "Laptop",              "owner": "Patient nav (WFH)",      "zone": "wfh",        "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 95, "status": "compliant",  "risk": 9,  "last_seen": 2,  "locus": True,  "dex": {"health": 90, "util": 60, "active_hrs": 6.0, "boot_s": 9},  "note": "WFH; on-device presence normal for home geofence."},
    {"id": "SFX-9008", "name": "Telehealth-Lap-05",  "type": "Laptop",              "owner": "Telehealth RN (WFH)",    "zone": "wfh",        "silicon": "Copilot+ Surface", "os": "Win 11 24H2", "battery": 40, "status": "compliant",  "risk": 12, "last_seen": 1,  "locus": True,  "dex": {"health": 85, "util": 57, "active_hrs": 5.8, "boot_s": 10}, "note": "WFH; nominal."},
]

STATUS_META = {
    "compliant":  {"label": "Compliant",  "color": "#22C55E"},
    "at_risk":    {"label": "At risk",    "color": "#F59E0B"},
    "offline":    {"label": "Offline",    "color": "#94A3B8"},
    "missing":    {"label": "Missing",    "color": "#EF4444"},
    "off_campus": {"label": "Off-campus", "color": "#38BDF8"},
}


def fleet_summary() -> dict:
    """Roll-up counters computed from FLEET_DEVICES (kept honest, not hard-coded)."""
    counts: dict[str, int] = {k: 0 for k in STATUS_META}
    locus = wfh = campus = transit = high_risk = underused = 0
    for d in FLEET_DEVICES:
        counts[d["status"]] = counts.get(d["status"], 0) + 1
        if d.get("locus"):
            locus += 1
        if d["zone"] == "wfh":
            wfh += 1
        elif d["zone"] == "transit":
            transit += 1
        else:
            campus += 1
        if d["risk"] >= 60:
            high_risk += 1
        if d.get("dex", {}).get("util", 100) < 25:
            underused += 1
    return {
        "total": len(FLEET_DEVICES),
        "campus": campus,
        "wfh": wfh,
        "transit": transit,
        "locus_enrolled": locus,
        "high_risk": high_risk,
        "underused": underused,
        "status_counts": counts,
        "scale": FLEET_SCALE,
    }


# ─────────────────────────────────────────────────────────────────────────
#  On-device PII redaction.  Sensitive context (which PATIENT was seen by which
#  CLINICIAN, MRNs, DOBs, contact info) is scrubbed & tokenized ON THE DEVICE
#  before any location signal or summary syncs to Intune / ServiceNow.  Only a
#  coarse zone + time-bucket survives — enough to model location, no PHI.
# ─────────────────────────────────────────────────────────────────────────

# Known fabricated patient names used in the demo examples (guarantees a clean
# redaction on-stage; the regexes below handle free-typed input reasonably).
_DEMO_PATIENT_NAMES = ["Maria Delgado", "John P. Whitfield", "Rosa Klein", "David Okafor"]

_REDACT_RULES = [
    ("EMAIL",     re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
    ("SSN",       re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    ("PHONE",     re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE]"),
    ("MRN",       re.compile(r"\bMRN[:#\s]*\d{5,10}\b", re.I), "[MRN]"),
    ("DOB/DATE",  re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"), "[DATE]"),
    ("CLINICIAN", re.compile(r"\b(?:Dr\.?|Provider|Physician)\s+(?:[A-Z]\.\s*)?[A-Z][a-zA-Z'-]+(?:\s+[A-Z][a-zA-Z'-]+)?"), "[CLINICIAN]"),
    ("PATIENT",   re.compile(r"\b[Pp]atient\s+[A-Z][a-zA-Z'.-]+(?:\s+[A-Z]\.?)?(?:\s+[A-Z][a-zA-Z'.-]+)?"), "Patient [PATIENT]"),
    ("MRN",       re.compile(r"\b\d{7,10}\b"), "[MRN]"),  # bare long ids -> MRN-like
]


def redact_pii(text: str) -> dict:
    """Deterministic on-device PII redactor. Returns the tokenized text plus the
    list of removed items. Illustrative — a shipping version would pair this with
    the on-device SLM for context-aware de-identification."""
    text = text or ""
    removed: list[dict] = []
    redacted = text

    for name in _DEMO_PATIENT_NAMES:
        if name in redacted:
            removed.append({"type": "PATIENT", "value": name})
            redacted = redacted.replace(name, "[PATIENT]")

    for label, pat, token in _REDACT_RULES:
        def _sub(m, _label=label, _token=token):
            val = m.group(0)
            # keep the leading 'Patient '/'Dr ' word visible where the token embeds it
            removed.append({"type": _label, "value": val.strip()})
            return _token
        redacted = pat.sub(_sub, redacted)

    return {
        "raw": text,
        "redacted": redacted,
        "removed": removed,
        "removed_count": len(removed),
    }


REDACTION_EXAMPLES = [
    {
        "label": "Coding tablet — encounter note",
        "raw": "Encounter for Patient Maria Delgado (MRN 00447162), seen by Dr. A. Rivera at 18:04 in Cascade Tower 6-East. DOB 04/12/1979, contact 407-555-0148.",
        "kept": "Cascade Tower (coarse zone) · 18:00–18:30 (time bucket)",
    },
    {
        "label": "Revenue-cycle work item",
        "raw": "Coding queue: John P. Whitfield, MRN 3391085, provider Dr. Sanjay Patel, Revenue Cycle Center; email jwhitfield@example.org.",
        "kept": "Revenue Cycle Center (coarse zone)",
    },
    {
        "label": "Device telemetry line (pre-sync)",
        "raw": "device=INT-3302 user=coder note='Patient Rosa Klein w/ Dr. Okafor' loc='Cascade lobby' t=18:12 ssn=412-55-9981",
        "kept": "zone=cascade t-bucket=18:00-18:30 (device id + coarse zone only)",
    },
]


# ─────────────────────────────────────────────────────────────────────────
#  Predicted location (probabilistic).  From the REDACTED movement signal +
#  learned per-device patterns, the on-device model estimates where a device is
#  now (and would go next), with a probability distribution over zones.
#  "Intune tells you where it was; Local AI tells you where it probably is."
# ─────────────────────────────────────────────────────────────────────────

PREDICTED_LOCATIONS = {
    "INT-3302": {
        "device": "INT-3302 · Coding-Tab-08",
        "headline": "Most likely still on-campus in the Parking & Mobility Hub",
        "confidence": "Moderate (0.62)",
        "method": "On-device sequence model over the last-known vector + shift-change egress patterns. Inputs are the REDACTED movement signal only — no patient or clinician identity.",
        "candidates": [
            {"zone": "parking",    "name": "Parking & Mobility Hub",   "prob": 44},
            {"zone": "offcampus",  "name": "Off-campus (NW exit)",     "prob": 23},
            {"zone": "transit",    "name": "Interoffice courier route", "prob": 15},
            {"zone": "cascade",   "name": "Cascade Tower (returned)", "prob": 11},
            {"zone": "commons",    "name": "Lakeside Commons",          "prob": 7},
        ],
        "rationale": "Last vector headed NW from the Cascade lakeside lobby toward the parking deck at 18:12, matching the 18:00–18:30 shift-change egress pattern. No badge read at any campus exit turnstile since, so the device is most probably still on-campus in the parking structure — dispatch a technician there first.",
    },
    "SFX-9006": {
        "device": "SFX-9006 · Coder-Laptop-22 (WFH)",
        "headline": "Predicted at an unrecognized location ~6mi from the registered home geofence",
        "confidence": "Elevated anomaly (0.71)",
        "method": "On-device home-geofence model. Flag fired offline; only a coarse anomaly signal (not raw coordinates) is what syncs.",
        "candidates": [
            {"zone": "home_anom",  "name": "Unrecognized location (current)", "prob": 58},
            {"zone": "home",       "name": "Registered home geofence",        "prob": 33},
            {"zone": "transit",    "name": "In transit",                       "prob": 9},
        ],
        "rationale": "Opened outside the learned home geofence during off-hours. On-device model predicts an unrecognized residential block ~6mi from the registered home — step-up auth and verify with the user before it syncs anything sensitive.",
    },
    "SFX-1042": {
        "device": "SFX-1042 · Exec-Laptop-04",
        "headline": "High-confidence present in Cascade Tower (lakefront office)",
        "confidence": "High (0.92)",
        "method": "On-device presence model over the learned daily pattern.",
        "candidates": [
            {"zone": "cascade",   "name": "Cascade Tower",        "prob": 92},
            {"zone": "commons",    "name": "Lakeside Commons",      "prob": 5},
            {"zone": "parking",    "name": "Parking & Mobility Hub", "prob": 3},
        ],
        "rationale": "Movement matches the device's learned weekday pattern; prediction is confident even between Wi-Fi check-ins. Shown to make the point that prediction is not just for lost devices.",
    },
}


# ─────────────────────────────────────────────────────────────────────────
#  ServiceNow (mock).  Locus's resolved physical location is written into the
#  CMDB / task so a field technician knows exactly WHERE to go — closing the
#  "thousands of endpoints with unknown location" gap.  MOCK — not a real
#  ServiceNow instance.
# ─────────────────────────────────────────────────────────────────────────

SERVICENOW_TICKETS = [
    {
        "number": "TASK0102934", "type": "Hardware refresh", "priority": "3 - Moderate", "state": "Assigned",
        "ci": "SFX-8004 · Mobility-Tablet-2", "group": "EUC Field Services",
        "short_desc": "Windows 11 refresh wave — collect & re-image endpoint",
        "loc_before": "Unknown (CMDB location blank)",
        "loc_after": "Parking & Mobility Hub · L2 charging bay 14",
        "conf": 91,
        "note": "Locus resolved the physical location the tech drives to. Also flagged low utilization (15%).",
    },
    {
        "number": "INC0459211", "type": "Lost asset", "priority": "1 - Critical", "state": "In Progress",
        "ci": "INT-3302 · Coding-Tab-08", "group": "Cybersecurity",
        "short_desc": "PHI-capable tablet missing — locate & remote-lock",
        "loc_before": "Unknown (off-network 74m)",
        "loc_after": "Predicted: Parking & Mobility Hub (44%) — see Predicted Location",
        "conf": 44,
        "note": "Not Locus-enrolled → uses predicted location from redacted movement signal.",
    },
    {
        "number": "TASK0102955", "type": "Break/fix", "priority": "2 - High", "state": "Assigned",
        "ci": "INT-3301 · Coding-Tab-07", "group": "EUC Field Services",
        "short_desc": "Battery swap + charger fault on clinical tablet",
        "loc_before": "Stale (Revenue Cycle, 9m old)",
        "loc_after": "Revenue Cycle Center · 3rd-floor NW cube block",
        "conf": 88,
        "note": "Locus upgraded a stale CMDB location to a live one — no ticket ping-pong.",
    },
    {
        "number": "TASK0103010", "type": "Asset reclaim", "priority": "4 - Low", "state": "New",
        "ci": "SFX-2210 · Conf-Room-PC-02", "group": "IT Asset Management",
        "short_desc": "Reclaim chronically underused endpoint for redeployment",
        "loc_before": "Unknown (CMDB location blank)",
        "loc_after": "Lakeside Commons · Conf Rm C-210",
        "conf": 95,
        "note": "DEX utilization 12% + Locus location → reclaim & redeploy instead of buying new.",
    },
]

SERVICENOW_SUMMARY = {
    "auto_located": 4,           # in this sample
    "fleet_unknown_before": FLEET_SCALE["unknown_location"],
    "note": (
        "Mock ServiceNow integration. Across ~123,000 endpoints, thousands carry a "
        "blank or stale CMDB location, so field techs waste truck-rolls hunting for "
        "hardware. Locus writes the resolved (or predicted) physical location "
        "onto the ticket automatically."
    ),
}


# ─────────────────────────────────────────────────────────────────────────
#  Utilization & repurpose.  Lakeside SysTrack (DEX) tells you a device is
#  underused; Locus tells you WHERE it physically is — so it can actually be
#  reclaimed and redeployed instead of buying new hardware.
# ─────────────────────────────────────────────────────────────────────────

def _underused_candidates() -> list[dict]:
    out = []
    for d in FLEET_DEVICES:
        util = d.get("dex", {}).get("util", 100)
        if util < 25:
            zone = next((z for z in FLEET_ZONES if z["id"] == d["zone"]), None)
            out.append({
                "id": d["id"], "name": d["name"], "type": d["type"],
                "building": zone["name"] if zone else d["zone"],
                "util": util, "active_hrs": d.get("dex", {}).get("active_hrs"),
                "health": d.get("dex", {}).get("health"),
                "recommendation": "Reclaim & redeploy" if util < 16 else "Redeploy / downgrade",
            })
    return sorted(out, key=lambda r: r["util"])


UTILIZATION_REPORT = {
    "source": "Lakeside SysTrack (DEX) utilization + Locus on-device location",
    "summary": {
        "sample_underused": None,   # filled at request time
        "fleet_underused_est": FLEET_SCALE["underused_estimate"],
        "annual_savings_est": FLEET_SCALE["annual_repurpose_savings"],
        "threshold": "utilization < 25% sustained",
    },
    "note": (
        "DEX tools like Lakeside SysTrack already surface underused endpoints — but "
        "'reclaim it' fails when nobody knows where the device physically is. Fusing "
        "DEX utilization with Locus's on-device location makes repurposing "
        "actionable at fleet scale (~9,500 flagged across ~123,000 endpoints)."
    ),
}


def utilization_report() -> dict:
    cands = _underused_candidates()
    rep = dict(UTILIZATION_REPORT)
    rep["candidates"] = cands
    rep["summary"] = dict(UTILIZATION_REPORT["summary"], sample_underused=len(cands))
    return rep


# ─────────────────────────────────────────────────────────────────────────
#  Capability ladder — "how far Intune goes" → Local AI → Locus future.
# ─────────────────────────────────────────────────────────────────────────

CAPABILITY_LADDER = {
    "dimensions": [
        "Location granularity",
        "Update cadence",
        "Works offline / RF dead zones",
        "Loss & theft detection",
        "Privacy of location & PHI",
        "Downstream systems (ServiceNow, DEX)",
        "Automated response",
    ],
    "tiers": [
        {
            "id": "intune_today",
            "name": "Today with Intune",
            "tag": "Baseline (ships now)",
            "accent": "#0A66C2",
            "blurb": "How far standard Microsoft Intune / Entra goes today across Zava Health's ~123k Windows endpoints.",
            "rows": [
                "Coarse: last check-in public IP + Entra sign-in city; thousands of endpoints carry a blank/stale location.",
                "Periodic check-in (~8h default) and only while the device is online.",
                "No — the device must reach the Intune service to report anything.",
                "Manual: user reports loss; admin issues remote lock / wipe on next check-in.",
                "Inventory + sign-in geo flow to the Intune cloud; PHI context is not location-aware.",
                "CMDB location fields often blank → field techs can't find the hardware to fix it.",
                "Conditional Access, compliance policy, remote lock / wipe / retire.",
            ],
        },
        {
            "id": "local_ai",
            "name": "Local AI Acceleration",
            "tag": "This prototype",
            "accent": "#7C3AED",
            "blurb": "An on-device SLM (phi-3.5-mini) on the Surface NPU adds real-time reasoning, redaction and prediction on top of Intune.",
            "rows": [
                "Fine: on-device fuses Wi-Fi/BLE/badge/sensor into a live building-level zone, kept on the device.",
                "Continuous & event-driven — the NPU evaluates presence and movement in real time.",
                "Yes — detection, redaction and prediction run locally; results sync when back online.",
                "Automatic + predictive: on-device model flags egress instantly and predicts where a device is now.",
                "On-device PII redaction: patient<->clinician associations are scrubbed before anything syncs.",
                "Writes resolved / predicted location into ServiceNow; fuses Lakeside SysTrack (DEX) utilization.",
                "Local graduated response: warn, disable app access, pre-stage lock, queue admin alert.",
            ],
        },
        {
            "id": "locus",
            "name": "Surface Locus (native)",
            "tag": "Future-state mock-up",
            "accent": "#F36F21",
            "blurb": "Concept: on-device Locus surfaced natively in both the Intune admin center and the Surface Management Portal. MOCK — not a real product.",
            "rows": [
                "Always-on precise, policy-scoped presence from the Surface low-power sensor hub.",
                "Continuous at <1% battery, even in Modern Standby; secure aggregate to Intune.",
                "Yes — device holds last-known + reasons locally, then reconciles on secure reconnect.",
                "Predictive fleet-wide: learns each device's normal pattern and flags deviations before loss.",
                "Privacy-by-design: raw location + PHI never leave the device; only policy-scoped signals sync.",
                "Native ServiceNow dispatch + DEX-driven repurposing across all ~123k endpoints.",
                "Automated recovery: geofence lock, BitLocker enforce, Find-My, technician dispatch.",
            ],
        },
    ],
}


# ─────────────────────────────────────────────────────────────────────────
#  Mock of the "Surface Locus" blade inside the Intune admin center.
# ─────────────────────────────────────────────────────────────────────────

LOCUS_BLADE = {
    "breadcrumb": ["Microsoft Intune", "Devices", "Surface Locus", "Preview"],
    "kpis": [
        {"label": "Managed endpoints",     "value": "123,000", "hint": "Zava Health fleet (illustrative)"},
        {"label": "Unknown location",      "value": "~4,200",  "hint": "blank/stale — Locus target"},
        {"label": "On-campus (sample)",    "value": "13",      "hint": "live building-level presence"},
        {"label": "WFH / remote",          "value": "4",       "hint": "home geofences"},
        {"label": "Auto-located to SNOW",  "value": "4",       "hint": "CMDB location filled"},
        {"label": "Repurpose candidates",  "value": "~9,500",  "hint": "DEX underused + located"},
    ],
    "geofences": [
        {"name": "Cascade Tower (lakeside)", "devices": 2, "state": "1 egress flag (18:12)"},
        {"name": "Revenue Cycle Center",       "devices": 2, "state": "1 at-risk (low battery)"},
        {"name": "Approved courier route",     "devices": 1, "state": "on-route"},
        {"name": "WFH home geofences",         "devices": 4, "state": "1 anomaly (Coder-Laptop-22)"},
    ],
    "alerts": [
        {"sev": "high", "device": "INT-3302 · Coding-Tab-08", "text": "Missing — left Cascade lakeside lobby 18:12, no check-in for 74m. Not Locus-enrolled → predicted location only.", "action": "Locate via Predicted Location · remote-lock · INC0459211"},
        {"sev": "med",  "device": "SFX-9006 · Coder-Laptop-22", "text": "WFH anomaly — opened in unrecognized location, off hours. On-device flag fired offline; PHI redacted before sync.", "action": "Step-up auth · verify with user"},
        {"sev": "med",  "device": "SFX-1077 · Facilities-2in1-11", "text": "Repeated Cascade lakeside-perimeter egress; on-device geofence held through the dead zone.", "action": "Notify facilities lead"},
        {"sev": "low",  "device": "SFX-2210 · Conf-Room-PC-02", "text": "Chronically underused (DEX util 12%); Locus located it in Lakeside Commons C-210.", "action": "Reclaim → TASK0103010"},
    ],
}


# ─────────────────────────────────────────────────────────────────────────
#  Mock of "Locus" inside the Microsoft Surface Management Portal — the
#  Surface admin's hardware view (inventory, DEX health, warranty) now with a
#  live Location column + location-driven repurpose / refresh actions.
# ─────────────────────────────────────────────────────────────────────────

SURFACE_PORTAL = {
    "breadcrumb": ["Microsoft Surface Management Portal", "Devices", "Locus location insights", "Preview"],
    "kpis": [
        {"label": "Surface devices managed", "value": "38,400",   "hint": "Copilot+ & legacy (illustrative)"},
        {"label": "Copilot+ NPU-enabled",    "value": "22,100",   "hint": "Locus-eligible, on-device presence"},
        {"label": "Located by Locus",        "value": "21,650",   "hint": "live building-level zone"},
        {"label": "Warranty expiring <90d",  "value": "1,240",    "hint": "pinpointed for proactive refresh"},
        {"label": "Repurpose candidates",    "value": "~9,500",   "hint": "DEX underused + located"},
        {"label": "Avg fleet health (DEX)",  "value": "86 / 100", "hint": "Lakeside SysTrack blended"},
    ],
    "devices": [
        {"model": "Surface Laptop 7",        "silicon": "Copilot+ · Surface NPU", "device": "SFX-1042 · Exec-Laptop-04",        "location": "Cascade Tower (lakeside), L12 — docked",  "health": "92 / 100", "warranty": "Active → 2027",   "action": "Nominal"},
        {"model": "Surface Pro 11",          "silicon": "Copilot+ · Surface NPU", "device": "SFX-2210 · Conf-Room-PC-02",       "location": "Lakeside Commons — Conf C-210",            "health": "88 / 100", "warranty": "Active → 2026",   "action": "Reclaim — util 12% → TASK0103010"},
        {"model": "Surface Laptop Studio 2", "silicon": "Copilot+ · Surface NPU", "device": "SFX-5001 · Billing-WOW-2",         "location": "Revenue Cycle Center, 2F",                 "health": "89 / 100", "warranty": "Expiring 71d",    "action": "Field-collect at known location; battery refresh"},
        {"model": "Surface Pro 11",          "silicon": "Copilot+ · Surface NPU", "device": "SFX-8004 · Mobility-Tablet-2",     "location": "Parking L2 — charging bay 14",             "health": "79 / 100", "warranty": "Active → 2026",   "action": "Reassign — util 15%"},
        {"model": "Surface Pro 10 (Intel)",  "silicon": "Legacy Intel · no NPU",  "device": "INT-3302 · Coding-Tab-08",         "location": "Predicted: Cascade lakeside lobby (78%)", "health": "58 / 100", "warranty": "Out of warranty", "action": "Locate + retire → refresh to Copilot+"},
        {"model": "Surface Laptop 7",        "silicon": "Copilot+ · Surface NPU", "device": "SFX-9006 · Coder-Laptop-22 (WFH)", "location": "Home geofence — anomaly flagged",          "health": "82 / 100", "warranty": "Active → 2027",   "action": "Verify with user; PHI redacted on-device"},
    ],
    "insights": [
        {"title": "Locus filled ~4,200 blank locations",
         "body": "Every Locus-enrolled Surface reports a building-level zone straight into the portal — no extra agent, no cloud round-trip. Unknown-location devices fall from thousands toward zero."},
        {"title": "~9,500 repurpose candidates surfaced",
         "body": "Copilot+ Surface devices with DEX utilization under 20% and a confirmed Locus location — ready to reclaim, relocate and redeploy instead of buying new hardware."},
        {"title": "Warranty + location in one view",
         "body": "1,240 devices with warranty under 90 days are pinpointed by Locus, so a technician collects them on the first visit — refresh planning driven by real placement, not spreadsheets."},
    ],
}


# ─────────────────────────────────────────────────────────────────────────
#  The 8 Forces of Local AI, triaged for THIS use case.
#  relevance ∈ high | medium | low  (rank is 1 = most relevant)
# ─────────────────────────────────────────────────────────────────────────

EIGHT_FORCES = {
    "note": (
        "The 8 Forces of Local AI — the framework for deciding when to move AI on-device. "
        "Each force is scored for Zava Health's scenario: tracking ~123,000 endpoints across "
        "the Seattle corporate campus (Cedar Lake) and WFH staff. This use case answers 'yes' "
        "to most of them — which is exactly what makes it a strong Local AI candidate."
    ),
    "forces": [
        {"id": "privacy",      "name": "Privacy & Sovereignty",   "rank": 1, "relevance": "high",
         "question": "Is the data too sensitive, regulated, or confidential to leave the device?",
         "why": "The device holds which PATIENT was seen by which CLINICIAN, plus MRNs — regulated PHI under HIPAA. On-device redaction scrubs those associations before any location signal syncs, so there is no cloud honeypot of patient or staff movement."},
        {"id": "resilience",   "name": "Resilience",              "rank": 2, "relevance": "high",
         "question": "Must the solution continue working when offline or with poor connectivity?",
         "why": "Corporate towers have RF dead zones — shielded server rooms, parking decks, stairwells — and WFH links are flaky. On-device presence, prediction and loss detection keep working with no connection, then reconcile on reconnect."},
        {"id": "latency",      "name": "Latency",                 "rank": 3, "relevance": "high",
         "question": "Does the experience require real-time or near-instant response?",
         "why": "Loss, theft and 'wandering device' detection must be instant. Local anomaly detection on the NPU beats a cloud round-trip — critical for a device already leaving the building."},
        {"id": "segmentation", "name": "Risk Segmentation",       "rank": 4, "relevance": "high",
         "question": "Should sensitive portions of the workflow remain local while other parts leverage cloud models?",
         "why": "This is the core design: raw location and PHI stay on the device; only a de-identified coarse zone and time-bucket flow to Intune, ServiceNow and DEX. Sensitive steps stay local; everything else can still use the cloud."},
        {"id": "opfit",        "name": "Operational Fit",         "rank": 5, "relevance": "high",
         "question": "Can the solution integrate into existing enterprise management, security, and deployment processes?",
         "why": "Locus surfaces inside tools Zava Health already runs — Intune, the Surface Management Portal, ServiceNow dispatch and Lakeside SysTrack (DEX) — so it is an added layer, not a rip-and-replace."},
        {"id": "governance",   "name": "Governance Granularity",  "rank": 6, "relevance": "medium",
         "question": "Does policy enforcement, management, or control need to occur at the endpoint/device level?",
         "why": "Policy must act at the endpoint: per-building geofences, geofence lock, BitLocker enforcement and predictive loss/theft rules run on the device and are managed per-device from Intune and the Surface portal."},
        {"id": "throughput",   "name": "Throughput at Edge",      "rank": 7, "relevance": "medium",
         "question": "Does the workload generate continuous, high-volume inference that is better processed locally?",
         "why": "Continuously evaluating presence and movement for ~123,000 endpoints is high-volume, always-on inference — far more efficient on each device's NPU than streaming it all to the cloud."},
        {"id": "cost",         "name": "Cost & Scale",            "rank": 8, "relevance": "medium",
         "question": "Would cloud inference costs become excessive due to usage volume?",
         "why": "At 123k endpoints, continuous cloud location and LLM inference costs would balloon; the owned NPU offloads it. Reclaiming ~9,500 DEX-underused devices is a concrete supporting economic win."},
    ],
    "top_three": ["privacy", "resilience", "latency"],
}


LOCAL_AI_BENEFITS = [
    {"title": "On-device PII redaction", "body": "Patient<->clinician associations, MRNs and contact info are scrubbed and tokenized on the device before any location signal or summary syncs. Only a coarse zone + time-bucket survives."},
    {"title": "Predicted location with probability", "body": "From the redacted movement signal, the NPU estimates where a device probably is now — with a probability distribution — even while off-network. Intune tells you where it was; Local AI tells you where it is."},
    {"title": "Fills the ServiceNow location gap", "body": "Thousands of endpoints carry a blank CMDB location. Locus writes the resolved (or predicted) building/floor/bay onto the ticket, so a field tech drives straight to the device."},
    {"title": "Find & repurpose underused hardware", "body": "Fuses Lakeside SysTrack (DEX) utilization with on-device location: ~9,500 chronically underused endpoints become findable and reclaimable instead of buying new."},
    {"title": "Instant, on-device detection", "body": "Geofence breaches and loss/theft anomalies are caught by the Surface NPU in real time — no cloud round-trip while a device is already walking out the door."},
    {"title": "Keeps working offline", "body": "Presence, redaction and prediction run locally, so RF dead zones (shielded rooms, parking decks) and flaky WFH links don't create blind spots."},
    {"title": "Privacy & HIPAA posture", "body": "Location reasoning and PHI stay on the device; only policy-scoped alerts and summaries ever sync. Smaller cloud data footprint = smaller breach blast radius."},
    {"title": "Low battery cost at fleet scale", "body": "The low-power NPU sensor-hub enables always-on presence at ~<1% battery, viable across 123k laptops, 2-in-1s and WOWs in continuous use."},
    {"title": "Complements — not replaces — Intune", "body": "Intune keeps doing identity, compliance and remote lock/wipe; Local AI adds the real-time, offline, privacy-preserving layer plus ServiceNow + DEX outcomes on top."},
]


# ─────────────────────────────────────────────────────────────────────────
#  "Ask Locus" — on-device SLM tab: prompts, routing, deterministic mocks.
# ─────────────────────────────────────────────────────────────────────────

_ONDEVICE_PERSONA = (
    "You are Surface Locus, an on-device fleet-intelligence analyst running "
    "locally on a Copilot+ Surface NPU via Foundry Local. You help Zava Health's "
    "endpoint & security team track ~123,000 Windows devices across the Seattle "
    "corporate campus (Cedar Lake, 9 buildings) and WFH staff. Answer ONLY from the "
    "fleet context provided; never invent devices or locations. Be concise and "
    "operational. Output GitHub-flavored markdown. Always close with a one-line "
    "blockquote noting the analysis ran on-device with no location data or PHI leaving "
    "the device."
)

SYSTEM_PROMPTS = {
    "fleet_query": _ONDEVICE_PERSONA + (
        " For a fleet question, respond with a short direct answer, a markdown table "
        "of the relevant devices (ID, name, building, status, risk, last seen), and a "
        "'Recommended next step' line."
    ),
    "incident": _ONDEVICE_PERSONA + (
        " For an incident, respond with sections: Incident Summary, Timeline "
        "(bulleted), Current Risk, and Recommended Actions (numbered with timeframes)."
    ),
    "risk_triage": _ONDEVICE_PERSONA + (
        " For a triage request, respond with a prioritized markdown table (Priority, "
        "Device, Why, Action) ordered by risk, then a one-line summary."
    ),
    "predict": _ONDEVICE_PERSONA + (
        " For a location-prediction request, give the single most-likely location, "
        "then a markdown table of candidate locations with probabilities, then the "
        "rationale. Stress that only the redacted movement signal is used."
    ),
    "redact": _ONDEVICE_PERSONA + (
        " For a redaction request, show what PII is stripped on-device (patient, "
        "clinician, MRN, contact) and exactly what coarse signal remains for location "
        "modeling. Emphasize nothing sensitive leaves the device."
    ),
    "utilization": _ONDEVICE_PERSONA + (
        " For a utilization/repurpose request, list underused devices with their "
        "building location and a reclaim recommendation, then the fleet-scale "
        "extrapolation and savings."
    ),
    "dispatch": _ONDEVICE_PERSONA + (
        " For a dispatch/ServiceNow request, show the resolved (or predicted) physical "
        "location Locus writes onto the ticket so a technician can find the device."
    ),
}

# keyword → module routing for the free-text box.  Specific intents first;
# "left the wing"-style questions stay fleet queries; "missing/lost" → incident.
MODULE_ROUTES = [
    (("predict", "likely", "probab", "where will", "most likely", "where is it now"), "predict"),
    (("redact", "pii", "leaves the device", "leave the device", "scrub", "de-identif", "anonymiz", "phi"), "redact"),
    (("underused", "reclaim", "repurpose", "utiliz", "under-used", "idle hardware"), "utilization"),
    (("dispatch", "technician", "servicenow", "service now", "cmdb", "where to send", "find the device"), "dispatch"),
    (("missing", "lost", "stolen", "theft", "incident", "walked", "wander"), "incident"),
    (("triage", "prioriti", "highest risk", "at risk", "at-risk", "risk"), "risk_triage"),
]
DEFAULT_MODULE = "fleet_query"


def route_module(query: str) -> str:
    q = (query or "").lower()
    for keys, module in MODULE_ROUTES:
        if any(k in q for k in keys):
            return module
    return DEFAULT_MODULE


MOCK_RESPONSES = {
    "general": "Analysis complete — processed on-device on the Copilot+ Surface NPU. No location data or PHI left the device.",

    "fleet_query": """## 🛰️ On-device fleet answer

**Question interpreted as:** which devices left a lakeside building after 18:00 today.

**Direct answer:** 2 revenue-cycle tablets show egress from the Cascade Tower lakeside area after 18:00 — one is now **Missing**.

| Device | Name | Building (last) | Status | Risk | Last seen |
|--------|------|-----------------|--------|------|-----------|
| INT-3302 | Coding-Tab-08 | Cascade Tower → between buildings (left 18:12) | 🔴 Missing | 88 | 74m ago |
| INT-3301 | Coding-Tab-07 | Revenue Cycle Center (non-work corridor) | 🟠 At risk | 58 | 9m ago |

Both are **Intel-based and not Locus-enrolled**, so there is no on-device
fallback once they drop off the network. Locus-enrolled Copilot+ Surface devices in
the same buildings kept reporting building-level presence locally.

**Recommended next step:** locate INT-3302 via **Predicted Location**, remote-lock
on next check-in, and prioritize Locus enrollment for the Intel tablets in
Revenue Cycle.

> 🛡️ *Answered on-device on the Surface NPU — no device locations or PHI left this machine.*""",

    "incident": """## 🚨 Incident Summary — INT-3302 · Coding-Tab-08

A Locus-**unenrolled** Intel clinical tablet assigned to **Revenue Cycle** left
the **Cascade Tower** lakeside lobby at **18:12** and has not checked in for **74
minutes**. It holds patient↔coder associations, so PHI exposure is the concern.
Because it lacks the on-device agent, its last known position is only as fresh as
its final Wi-Fi association.

### Timeline
- **18:08** — Normal use inside Cascade Tower (6-East).
- **18:12** — Crossed the Cascade lakeside geofence (egress event) heading NW.
- **18:13** — Last Wi-Fi association near the lakeside lobby; then offline.
- **now (+74m)** — No Intune check-in; no on-device fallback (not enrolled).

### Current Risk
**High (88/100).** PHI-capable, off-network, no live location. A Locus-enrolled
Copilot+ Surface device would still be reasoning about its location locally and could
pre-stage a lock offline. Predicted location: **Parking & Mobility Hub (44%)**.

### Recommended Actions
1. **Now** — Dispatch to the **Parking & Mobility Hub** (predicted 44%); auto-filed as **INC0459211** in ServiceNow.
2. **Now** — Flag in Intune for **remote lock + BitLocker enforce** on next check-in.
3. **+15 min** — If no check-in, disable app access via Conditional Access.
4. **This week** — Enroll the remaining Intel Revenue-Cycle tablets in Locus so egress is caught **offline and in real time**.

> 🛡️ *This incident was assembled on-device on the Surface NPU — no locations or PHI left this machine.*""",

    "risk_triage": """## 🎯 WFH laptop risk triage (on-device)

Prioritized from the live fleet, highest risk first:

| Priority | Device | Why | Action |
|----------|--------|-----|--------|
| 1 | SFX-9006 · Coder-Laptop-22 | Opened in an **unrecognized location, off hours**; on-device flag fired while offline | Step-up auth + verify with user now |
| 2 | INT-9005 · RevCycle-Laptop-14 | WFH, **Intel + not Locus-enrolled** → only coarse IP geo, last seen 34mi away | Confirm location; prioritize enrollment |
| 3 | SFX-9008 · Telehealth-Lap-05 | Low battery on shift; nominal otherwise | Monitor — no action |

**Summary:** 1 WFH laptop needs immediate verification (Coder-Laptop-22); the
biggest structural gap is the **non-Locus Intel laptop**, trackable only by
coarse cloud IP geolocation.

> 🛡️ *Triaged on-device on the Surface NPU — WFH staff locations never left the device.*""",

    "predict": """## 📍 Predicted location — INT-3302 · Coding-Tab-08

**Most likely: still on-campus in the Parking & Mobility Hub.** Confidence **Moderate (0.62)**.

| Candidate location | Probability |
|--------------------|-------------|
| Parking & Mobility Hub | ▓▓▓▓▓ 44% |
| Off-campus (NW exit) | ▓▓▓ 23% |
| Interoffice courier route | ▓▓ 15% |
| Cascade Tower (returned) | ▓ 11% |
| Lakeside Commons | ▪ 7% |

**Rationale:** last vector headed NW from the Cascade lakeside lobby at 18:12,
matching the 18:00–18:30 egress pattern; no badge read at any exit turnstile
since, so it is probably still on-campus in the parking structure. The model uses
**only the redacted movement signal** — no patient or clinician identity.

> 🛡️ *Predicted on-device on the Surface NPU from redacted signals — no PHI or raw location left this machine.*""",

    "redact": """## 🔒 On-device PII redaction (pre-sync)

Before any location signal leaves a coding tablet, the on-device model strips PHI:

**Raw (on device only):**
`Encounter for Patient Maria Delgado (MRN 00447162), seen by Dr. A. Rivera at 18:04 in Cascade Tower 6-East.`

**Redacted (what may sync):**
`Encounter for Patient [PATIENT] (MRN [MRN]), seen by [CLINICIAN] at [DATE] in Cascade Tower 6-East.`

**Removed on-device:** patient name, MRN, clinician identity, precise time.
**Kept for location modeling:** `Cascade Tower` (coarse zone) + `18:00–18:30` (time bucket).

So even if the device is later lost, the sync stream never carried who-saw-whom.

> 🛡️ *Redacted on-device on the Surface NPU — the patient↔clinician association never left this machine.*""",

    "utilization": """## 📊 Underused hardware — reclaim & repurpose

From **Lakeside SysTrack (DEX)** utilization fused with Locus location:

| Device | Building | Util | Recommendation |
|--------|----------|------|----------------|
| SFX-2210 · Conf-Room-PC-02 | Lakeside Commons (C-210) | 12% | Reclaim & redeploy |
| SFX-8004 · Mobility-Tablet-2 | Parking & Mobility Hub (bay 14) | 15% | Reassign to field techs |
| INT-7003 · ZHU-Lab-PC-9 | Zava Health University | 18% | Reclaim to spare pool |
| INT-1410 · HR-Workstation-6 | Cedar Executive Center | 22% | Redeploy / downgrade |

**At fleet scale:** DEX flags **~9,500** chronically underused endpoints across
**~123,000**. DEX knows they're idle; Locus adds **where they physically are**,
so they can actually be collected — est. **$3.1M–$4.4M/yr** avoided in new hardware.

> 🛡️ *Correlated on-device — utilization + building location without shipping raw telemetry to the cloud.*""",

    "dispatch": """## 🎫 ServiceNow dispatch — fill the location gap

Locus writes the resolved (or predicted) physical location onto the ticket so a
field tech drives straight to the device:

| Ticket | CI | Location before | Locus location |
|--------|----|-----------------|-------------------|
| TASK0102934 | SFX-8004 · Mobility-Tablet-2 | Unknown (blank) | Parking & Mobility Hub · L2 bay 14 (91%) |
| INC0459211 | INT-3302 · Coding-Tab-08 | Unknown (off-network) | Predicted: Parking & Mobility Hub (44%) |
| TASK0102955 | INT-3301 · Coding-Tab-07 | Stale (9m) | Revenue Cycle Center · 3rd-floor NW (88%) |

**Why it matters:** across ~123,000 endpoints, thousands have a blank/stale CMDB
location, so techs waste truck-rolls. Locus closes that gap automatically.

> 🛡️ *Locations resolved on-device on the Surface NPU — only the coarse building/bay is written to the ticket.*""",
}
