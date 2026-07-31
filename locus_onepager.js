// locus_onepager.js — generates locus_onepager.pptx
// A slide-ready deck for the Surface Locus device-tracking PROTOTYPE:
// the demo arc, capability ladder, Local AI acceleration, and the 8-Forces triage.
// Run:  node locus_onepager.js

const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.layout = "LAYOUT_16x9";           // 10 x 5.625 in
p.author = "Surface Locus prototype";
p.title = "Surface Locus — Zava Health Seattle (Prototype)";

// ── palette ────────────────────────────────────────────────
const NAVY = "0B1B34", NAVY2 = "12294B";
const LIGHT = "F4F7FB", WHITE = "FFFFFF";
const QCOM = "3253DC", INTUNE = "0A66C2", PURPLE = "7C3AED", ORANGE = "F36F21", GREEN = "16A34A";
const INK = "0F1B2D", BODY = "43536B", DIM = "64748B", ICE = "CADCFC", DIMICE = "9FB0C9";
const HIGH = "DC2626", MED = "D97706", LOW = "64748B", AMBER = "F59E0B";
const HF = "Trebuchet MS", BF = "Calibri";

const shadow = () => ({ type: "outer", color: "0B1B34", blur: 7, offset: 3, angle: 135, opacity: 0.16 });

function bg(s, c) { s.background = { color: c }; }
function accentTitle(s, txt, color, size, tcolor) {
  s.addShape(p.shapes.RECTANGLE, { x: 0.5, y: 0.42, w: 0.09, h: (size >= 30 ? 0.62 : 0.52), fill: { color: color } });
  s.addText(txt, { x: 0.72, y: 0.34, w: 8.9, h: 0.72, fontFace: HF, fontSize: size, bold: true, color: tcolor, margin: 0, valign: "middle" });
}
function card(s, x, y, w, h, fill, accent) {
  s.addShape(p.shapes.RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { color: "E2E8F0", width: 1 }, shadow: shadow() });
  s.addShape(p.shapes.RECTANGLE, { x, y, w: 0.09, h, fill: { color: accent } });
}
function numCircle(s, x, y, d, color, n) {
  s.addShape(p.shapes.OVAL, { x, y, w: d, h: d, fill: { color: color } });
  s.addText(String(n), { x, y, w: d, h: d, align: "center", valign: "middle", fontFace: HF, bold: true, fontSize: 15, color: WHITE, margin: 0 });
}

// ═══════════════════════════ SLIDE 1 — TITLE (dark) ═══════════════════════════
let s = p.addSlide(); bg(s, NAVY);
s.addShape(p.shapes.OVAL, { x: 7.3, y: 2.9, w: 4.2, h: 4.2, fill: { color: ORANGE, transparency: 86 } });
s.addShape(p.shapes.OVAL, { x: 6.3, y: -1.4, w: 3.4, h: 3.4, fill: { color: QCOM, transparency: 84 } });
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 7.15, y: 0.42, w: 2.4, h: 0.42, rectRadius: 0.2, fill: { color: AMBER, transparency: 80 }, line: { color: AMBER, width: 1 } });
s.addText("PROTOTYPE · MOCK DATA", { x: 7.15, y: 0.42, w: 2.4, h: 0.42, align: "center", valign: "middle", fontFace: HF, bold: true, fontSize: 10, color: "FDE68A", margin: 0, charSpacing: 1 });
s.addShape(p.shapes.RECTANGLE, { x: 0.6, y: 1.78, w: 0.1, h: 1.42, fill: { color: ORANGE } });
s.addText("Surface Locus", { x: 0.85, y: 1.7, w: 8.6, h: 0.95, fontFace: HF, bold: true, fontSize: 44, color: WHITE, margin: 0, valign: "middle" });
s.addText("Device Location & Fleet Intelligence — accelerated by Local AI", { x: 0.85, y: 2.72, w: 8.6, h: 0.5, fontFace: HF, fontSize: 20, color: ICE, margin: 0 });
s.addText("Zava Health Seattle · 9-building corporate campus on Cedar Lake + WFH  ·  ~123k endpoints  ·  Intune + Surface Management Portal (future-state concept)", { x: 0.85, y: 3.28, w: 8.6, h: 0.4, fontFace: BF, italic: true, fontSize: 13, color: DIMICE, margin: 0 });
s.addText("Prototype for demonstration only · fabricated data · Zava Health is a fictional demo brand · “Surface Locus” is a concept, not a shipping product · placeholder branding.",
  { x: 0.85, y: 4.9, w: 8.6, h: 0.6, fontFace: BF, fontSize: 10, color: DIMICE, margin: 0 });

// ═══════════════════════════ SLIDE 2 — THE ARC (light) ═══════════════════════════
s = p.addSlide(); bg(s, LIGHT);
accentTitle(s, "The demo in five beats", QCOM, 30, INK);
// problem card (left)
card(s, 0.5, 1.42, 3.5, 3.75, WHITE, ORANGE);
s.addText("The problem", { x: 0.72, y: 1.58, w: 3.2, h: 0.4, fontFace: HF, bold: true, fontSize: 16, color: ORANGE, margin: 0 });
s.addText([
  { text: "~123,000 managed Windows endpoints across a 9-building Seattle campus on Cedar Lake + WFH staff.", options: { bullet: true, breakLine: true, paraSpaceAfter: 10 } },
  { text: "Intune manages them — but thousands carry a blank or stale location, so techs can’t find hardware to fix or reclaim.", options: { bullet: true, breakLine: true, paraSpaceAfter: 10 } },
  { text: "Lost PHI-capable devices and underused assets both hinge on one question: where is it?", options: { bullet: true } },
], { x: 0.72, y: 2.05, w: 3.15, h: 3.0, fontFace: BF, fontSize: 12.5, color: BODY, margin: 0, valign: "top" });
// five beats (right)
const beats = [
  [QCOM, "Fleet Map", "9 buildings on Cedar Lake + WFH, at 123k scale"],
  [INTUNE, "How far Intune goes", "The honest ceiling of MDM today"],
  [PURPLE, "On-device intelligence", "Redact PII → predict location — the hero moment"],
  [ORANGE, "ServiceNow + Utilization", "Dispatch techs · reclaim underused hardware"],
  [GREEN, "Locus in Intune & Surface Portal", "Future-state concept + why on-device"],
];
let by = 1.5;
beats.forEach((b, i) => {
  numCircle(s, 4.45, by, 0.5, b[0], i + 1);
  s.addText(b[1], { x: 5.1, y: by - 0.04, w: 4.4, h: 0.32, fontFace: HF, bold: true, fontSize: 15, color: INK, margin: 0 });
  s.addText(b[2], { x: 5.1, y: by + 0.26, w: 4.4, h: 0.3, fontFace: BF, fontSize: 11.5, color: DIM, margin: 0 });
  by += 0.735;
});

// ═══════════════════════════ SLIDE 3 — CAPABILITY LADDER (light) ═══════════════════════════
s = p.addSlide(); bg(s, LIGHT);
accentTitle(s, "How far Intune goes — and where Local AI takes it", QCOM, 25, INK);
const cols = [
  [INTUNE, "Today with Intune", "Baseline · ships now", ["Coarse: last check-in IP + Entra sign-in city", "Periodic check-in (~8h), only while online", "No offline / RF-dead-zone coverage", "~4,200 endpoints carry a blank / stale location"]],
  [PURPLE, "Local AI Acceleration", "This prototype", ["On-device fused live zone; PII redacted locally", "Continuous, event-driven on the NPU", "Works offline; predicts location with probability", "Feeds ServiceNow dispatch + DEX repurpose"]],
  [ORANGE, "Locus (native)", "Future concept · mock", ["Always-on low-power presence (Surface NPU hub)", "Per-building geofences on the Cedar Lake campus", "Predictive loss/theft before it’s gone", "Surfaced natively in Intune + Surface Mgmt Portal"]],
];
const cw = 2.83, gap = 0.25; let cx = 0.5;
cols.forEach((c) => {
  card(s, cx, 1.35, cw, 3.55, WHITE, c[0]);
  s.addShape(p.shapes.RECTANGLE, { x: cx, y: 1.35, w: cw, h: 0.62, fill: { color: c[0] } });
  s.addText(c[1], { x: cx + 0.14, y: 1.37, w: cw - 0.2, h: 0.36, fontFace: HF, bold: true, fontSize: 14, color: WHITE, margin: 0, valign: "middle" });
  s.addText(c[2], { x: cx + 0.14, y: 1.7, w: cw - 0.2, h: 0.24, fontFace: BF, fontSize: 9.5, color: "E8EEF9", margin: 0 });
  s.addText(c[3].map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < c[3].length - 1, paraSpaceAfter: 8 } })),
    { x: cx + 0.16, y: 2.12, w: cw - 0.3, h: 2.6, fontFace: BF, fontSize: 11, color: BODY, margin: 0, valign: "top" });
  cx += cw + gap;
});
s.addText("Local AI complements Intune — it doesn’t replace it.", { x: 0.5, y: 5.05, w: 9, h: 0.4, align: "center", fontFace: HF, italic: true, bold: true, fontSize: 14, color: INK, margin: 0 });

// ═══════════════════════════ SLIDE 4 — LOCAL AI ACCELERATION (light) ═══════════════════════════
s = p.addSlide(); bg(s, LIGHT);
accentTitle(s, "Local AI acceleration — on the Surface NPU", QCOM, 25, INK);
s.addText("phi-3.5-mini runs on-device via Foundry Local. Three things cloud tracking cannot do:",
  { x: 0.72, y: 1.12, w: 9, h: 0.35, fontFace: BF, fontSize: 13.5, color: DIM, margin: 0 });
const pillars = [
  [QCOM, "Real-time", "Detects loss / theft the instant a device moves — no cloud round-trip."],
  [PURPLE, "Offline", "Keeps working in RF dead zones — parking decks, lakefront blind spots, basements — and flaky WFH links."],
  [ORANGE, "Private", "Location reasoning + PHI stay on-device; only alerts sync. Smaller breach blast radius."],
];
cx = 0.5;
pillars.forEach((pl) => {
  card(s, cx, 1.6, cw, 1.95, WHITE, pl[0]);
  s.addShape(p.shapes.OVAL, { x: cx + 0.18, y: 1.78, w: 0.34, h: 0.34, fill: { color: pl[0] } });
  s.addText(pl[1], { x: cx + 0.62, y: 1.74, w: cw - 0.7, h: 0.42, fontFace: HF, bold: true, fontSize: 17, color: INK, margin: 0, valign: "middle" });
  s.addText(pl[2], { x: cx + 0.2, y: 2.28, w: cw - 0.38, h: 1.15, fontFace: BF, fontSize: 11.5, color: BODY, margin: 0, valign: "top" });
  cx += cw + gap;
});
const chips = ["Natural-language fleet queries", "~<1% battery, always-on", "Per-device learned “normal”", "Cost offload to owned silicon"];
const chw = 2.13; cx = 0.5;
chips.forEach((c) => {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: cx, y: 3.85, w: chw, h: 0.62, rectRadius: 0.1, fill: { color: "E8EEF9" }, line: { color: "C7D6F0", width: 1 } });
  s.addText(c, { x: cx + 0.06, y: 3.85, w: chw - 0.12, h: 0.62, align: "center", valign: "middle", fontFace: BF, bold: true, fontSize: 10.5, color: "1E3A63", margin: 0 });
  cx += chw + 0.09;
});
s.addText("Intune stays the system of record; Local AI adds the real-time, offline, private layer on top.",
  { x: 0.5, y: 4.75, w: 9, h: 0.4, align: "center", fontFace: HF, italic: true, fontSize: 13, color: INK, margin: 0 });

// ═══════════════════════════ SLIDE 5 — INTELLIGENCE PIPELINE (light) ═══════════════════════════
s = p.addSlide(); bg(s, LIGHT);
accentTitle(s, "The on-device pipeline — redact → predict → dispatch → repurpose", QCOM, 22, INK);
s.addText("Zava Health-specific value: sensitive context stays on the device; only useful, de-identified signal flows downstream.",
  { x: 0.72, y: 1.06, w: 9, h: 0.35, fontFace: BF, fontSize: 12.5, color: DIM, margin: 0 });
const steps = [
  [PURPLE, "Redact PII", "Patient↔clinician links, MRNs and contact info are stripped on-device. Only a coarse zone + time bucket may ever sync."],
  [QCOM, "Predict location", "From the redacted signal, a probability distribution over buildings — where a device probably is, not just where it was."],
  [INTUNE, "ServiceNow dispatch", "Writes the resolved (or predicted) location onto the ticket so field techs stop hunting across ~4,200 blank-location endpoints."],
  [GREEN, "Repurpose (DEX)", "Lakeside SysTrack utilization + Locus location flags ~9,500 underused endpoints to reclaim & redeploy."],
];
const sw = 2.2, sgap = 0.153; let sx = 0.5;
steps.forEach((st, i) => {
  card(s, sx, 1.55, sw, 2.5, WHITE, st[0]);
  numCircle(s, sx + 0.2, 1.75, 0.44, st[0], i + 1);
  s.addText(st[1], { x: sx + 0.72, y: 1.75, w: sw - 0.8, h: 0.44, fontFace: HF, bold: true, fontSize: 13.5, color: INK, margin: 0, valign: "middle" });
  s.addText(st[2], { x: sx + 0.22, y: 2.34, w: sw - 0.42, h: 1.55, fontFace: BF, fontSize: 10.5, color: BODY, margin: 0, valign: "top" });
  if (i < steps.length - 1) s.addText("→", { x: sx + sw - 0.04, y: 1.55, w: sgap + 0.08, h: 2.5, align: "center", valign: "middle", fontFace: HF, bold: true, fontSize: 16, color: DIM, margin: 0 });
  sx += sw + sgap;
});
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 4.28, w: 9.26, h: 0.82, rectRadius: 0.1, fill: { color: "ECFDF3" }, line: { color: "A7F3D0", width: 1 } });
s.addText([
  { text: "~$3.1M–$4.4M / year  ", options: { fontFace: HF, bold: true, fontSize: 18, color: GREEN } },
  { text: "estimated avoided by reclaiming underused hardware instead of buying new — made actionable by knowing where each device physically is.", options: { fontFace: BF, fontSize: 12, color: "14532D" } },
], { x: 0.7, y: 4.28, w: 8.9, h: 0.82, valign: "middle", margin: 0 });

// ═══════════════════════════ SLIDE 6 — 8 FORCES (light) ═══════════════════════════
s = p.addSlide(); bg(s, LIGHT);
accentTitle(s, "The 8 Forces of Local AI — triaged for this use case", QCOM, 24, INK);
s.addText([
  { text: "The 8-Forces framework, scored for this use case.  ", options: { color: DIM } },
  { text: "Top 3 here: Privacy · Resilience · Latency.", options: { color: INK, bold: true } },
], { x: 0.72, y: 1.08, w: 9, h: 0.35, fontFace: BF, fontSize: 12.5, margin: 0 });
const H = (t) => ({ text: t, options: { fill: { color: NAVY }, color: WHITE, bold: true, fontFace: HF, fontSize: 11, valign: "middle" } });
const R = (rel) => ({ text: rel, options: { fill: { color: rel === "HIGH" ? HIGH : rel === "MED" ? MED : LOW }, color: WHITE, bold: true, align: "center", valign: "middle", fontFace: HF, fontSize: 10.5 } });
const cell = (t) => ({ text: t, options: { color: BODY, valign: "middle", fontFace: BF, fontSize: 10.5 } });
const rank = (n) => ({ text: String(n), options: { color: INK, bold: true, align: "center", valign: "middle", fontFace: HF, fontSize: 11 } });
const rows = [
  [H("#"), H("Force"), H("Relevance"), H("Why it matters here")],
  [rank(1), cell("Privacy & Sovereignty"), R("HIGH"), cell("Patient↔clinician links + MRNs are HIPAA PHI — redacted on-device, never a cloud honeypot.")],
  [rank(2), cell("Resilience"), R("HIGH"), cell("RF dead zones (server rooms, decks, lakefront) + flaky WFH — keeps working fully offline.")],
  [rank(3), cell("Latency"), R("HIGH"), cell("Loss / theft must be caught the instant a device moves — no cloud round-trip.")],
  [rank(4), cell("Risk Segmentation"), R("HIGH"), cell("Raw location + PHI stay local; only de-identified zone + time sync downstream.")],
  [rank(5), cell("Operational Fit"), R("HIGH"), cell("Surfaces in Intune, Surface Mgmt Portal, ServiceNow + DEX — an added layer, not rip-and-replace.")],
  [rank(6), cell("Governance Granularity"), R("MED"), cell("Per-endpoint policy: geofences, geofence lock, BitLocker enforce.")],
  [rank(7), cell("Throughput at Edge"), R("MED"), cell("Continuous presence for 123k endpoints is better evaluated on each device's NPU.")],
  [rank(8), cell("Cost & Scale"), R("MED"), cell("Offload continuous cloud inference; reclaim ~9,500 underused devices.")],
];
s.addTable(rows, {
  x: 0.5, y: 1.5, w: 9, colW: [0.6, 2.5, 1.25, 4.65], rowH: 0.4,
  border: { type: "solid", pt: 0.5, color: "D8E0EC" }, align: "left", valign: "middle", margin: [2, 5, 2, 5],
});

// ═══════════════════════════ SLIDE 7 — CLOSE / FUTURE (dark) ═══════════════════════════
s = p.addSlide(); bg(s, NAVY);
s.addShape(p.shapes.OVAL, { x: 7.6, y: 3.3, w: 4.0, h: 4.0, fill: { color: ORANGE, transparency: 87 } });
s.addShape(p.shapes.RECTANGLE, { x: 0.5, y: 0.44, w: 0.1, h: 0.62, fill: { color: ORANGE } });
s.addText("Surface Locus — the future-state concept", { x: 0.72, y: 0.36, w: 9, h: 0.7, fontFace: HF, bold: true, fontSize: 28, color: WHITE, margin: 0, valign: "middle" });
s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 1.28, w: 8.9, h: 0.5, rectRadius: 0.08, fill: { color: AMBER, transparency: 82 }, line: { color: AMBER, width: 1, dashType: "dash" } });
s.addText("CONCEPT MOCK-UP — not a real Microsoft or Zava Health product. Illustrative only.",
  { x: 0.6, y: 1.28, w: 8.9, h: 0.5, align: "center", valign: "middle", fontFace: HF, bold: true, fontSize: 12, color: "FDE68A", margin: 0 });
s.addText([
  { text: "Always-on, low-power presence from the Surface sensor hub", options: { bullet: true, breakLine: true, paraSpaceAfter: 12 } },
  { text: "Per-building geofences across the 9-building Cedar Lake campus + WFH", options: { bullet: true, breakLine: true, paraSpaceAfter: 12 } },
  { text: "On-device PII redaction + probabilistic predicted location for the ~4,200 unknown endpoints", options: { bullet: true, breakLine: true, paraSpaceAfter: 12 } },
  { text: "Feeds ServiceNow dispatch + DEX repurpose — surfaced natively in Intune and the Surface Management Portal", options: { bullet: true } },
], { x: 0.75, y: 2.05, w: 8.6, h: 2.0, fontFace: BF, fontSize: 14, color: ICE, margin: 0 });
s.addText("Prototype today — but the NPU and Foundry Local are real.",
  { x: 0.72, y: 4.35, w: 9, h: 0.5, fontFace: HF, bold: true, fontSize: 20, color: ORANGE, margin: 0 });
s.addText("Run it:  python locus_app.py  →  http://127.0.0.1:5075",
  { x: 0.72, y: 5.0, w: 9, h: 0.4, fontFace: BF, fontSize: 12, color: DIMICE, margin: 0 });

p.writeFile({ fileName: "locus_onepager.pptx" }).then((f) => console.log("wrote", f));
