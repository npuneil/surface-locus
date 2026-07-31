"""
locus_app.py — Surface Locus · Device Location & Fleet Intelligence
(PROTOTYPE).

A single-file Flask app that showcases how Local AI (an on-device SLM on the
Copilot+ Surface NPU via Foundry Local) accelerates device-location
tracking across a medical campus and WFH staff — and where that could go if it
were surfaced natively inside Microsoft Intune as a concept called
"Surface Locus".

⚠️  PROTOTYPE / MOCK. All data is fabricated. "Surface Locus"
is a conceptual future-state mock-up, not a shipping Microsoft
product. Nothing here manages a real device fleet.

Run:  python locus_app.py   →   http://127.0.0.1:5075
"""

from __future__ import annotations

import json
import sys

# Windows consoles default to cp1252 and choke on the emoji/arrow log lines.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

from flask import Flask, Response, jsonify, request, stream_with_context

import locus_data as gd
from locus_engine import LocusEngine

app = Flask(__name__)
engine = LocusEngine()


# ── API ──────────────────────────────────────────────────────────────────

@app.get("/api/fleet")
def api_fleet():
    return jsonify({
        "zones": gd.FLEET_ZONES,
        "devices": gd.FLEET_DEVICES,
        "status_meta": gd.STATUS_META,
        "summary": gd.fleet_summary(),
        "campus": gd.CAMPUS,
        "scale": gd.FLEET_SCALE,
    })


@app.get("/api/ladder")
def api_ladder():
    return jsonify(gd.CAPABILITY_LADDER)


@app.get("/api/blade")
def api_blade():
    return jsonify(gd.LOCUS_BLADE)


@app.get("/api/surface")
def api_surface():
    return jsonify(gd.SURFACE_PORTAL)


@app.get("/api/forces")
def api_forces():
    return jsonify(gd.EIGHT_FORCES)


@app.get("/api/benefits")
def api_benefits():
    return jsonify(gd.LOCAL_AI_BENEFITS)


@app.get("/api/status")
def api_status():
    return jsonify(engine.metrics.to_dict())


@app.post("/api/reconnect")
def api_reconnect():
    ok = engine.reconnect()
    return jsonify({"live": ok, **engine.metrics.to_dict()})


@app.get("/api/predict")
def api_predict():
    return jsonify(gd.PREDICTED_LOCATIONS)


@app.get("/api/redact/examples")
def api_redact_examples():
    return jsonify(gd.REDACTION_EXAMPLES)


@app.post("/api/redact")
def api_redact():
    body = request.get_json(silent=True) or {}
    return jsonify(gd.redact_pii(body.get("text") or ""))


@app.get("/api/servicenow")
def api_servicenow():
    return jsonify({"tickets": gd.SERVICENOW_TICKETS, "summary": gd.SERVICENOW_SUMMARY})


@app.get("/api/utilization")
def api_utilization():
    return jsonify(gd.utilization_report())


def _fleet_context() -> str:
    slim = [
        {k: d[k] for k in ("id", "name", "type", "owner", "zone", "status", "risk", "last_seen", "locus", "silicon")}
        for d in gd.FLEET_DEVICES
    ]
    zones = {z["id"]: z["name"] for z in gd.FLEET_ZONES}
    return json.dumps({"zones": zones, "devices": slim}, ensure_ascii=False)


@app.post("/api/ask")
def api_ask():
    body = request.get_json(silent=True) or {}
    query = (body.get("query") or "").strip()
    if not query:
        return jsonify({"error": "empty query"}), 400
    module = gd.route_module(query)
    system_msg = gd.SYSTEM_PROMPTS.get(module, gd.SYSTEM_PROMPTS["fleet_query"])
    prompt = f"Fleet context (JSON):\n{_fleet_context()}\n\nQuestion: {query}"

    def generate():
        try:
            for chunk in engine.query_stream(system_msg, prompt, module):
                yield chunk
        except Exception as e:  # never dead-end
            yield f"\n\n> ⚠️ on-device fallback engaged ({type(e).__name__}).\n"

    return Response(stream_with_context(generate()),
                    mimetype="text/plain; charset=utf-8")


@app.get("/")
def index():
    return Response(INDEX_HTML, mimetype="text/html")


# ── UI (inline single page) ──────────────────────────────────────────────

INDEX_HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Surface Locus · Device Tracking Prototype</title>
<style>
  :root{
    --bg1:#081226; --bg2:#0d1c3a; --bg3:#111a40;
    --surface:#3253DC; --intune:#0A66C2; --accent:#F36F21; --purple:#7C3AED;
    --ink:#F1F5F9; --dim:#9FB0C9; --line:rgba(148,163,184,.18);
    --card:rgba(15,23,42,.55); --ok:#22C55E; --warn:#F59E0B; --bad:#EF4444; --info:#38BDF8;
  }
  *{box-sizing:border-box}
  html,body{margin:0;padding:0}
  body{
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
    color:var(--ink); min-height:100vh;
    background:
      radial-gradient(1100px 560px at 8% -12%, rgba(50,83,220,.42), transparent 60%),
      radial-gradient(900px 520px at 112% 6%, rgba(243,111,33,.22), transparent 60%),
      linear-gradient(160deg,var(--bg1),var(--bg2) 55%,var(--bg3));
    background-attachment:fixed;
  }
  header{display:flex;align-items:center;justify-content:space-between;
    padding:16px 26px;border-bottom:1px solid var(--line);backdrop-filter:blur(6px);
    position:sticky;top:0;z-index:20;background:rgba(8,18,38,.72)}
  .brand{display:flex;align-items:center;gap:14px}
  .logo{width:38px;height:38px;border-radius:10px;
    background:linear-gradient(135deg,var(--surface),var(--accent));
    display:flex;align-items:center;justify-content:center;font-size:20px}
  .brand h1{font-size:16px;margin:0;letter-spacing:.2px}
  .brand p{margin:2px 0 0;font-size:11.5px;color:var(--dim)}
  .badges{display:flex;align-items:center;gap:10px}
  .proto{background:rgba(245,158,11,.16);border:1px solid rgba(245,158,11,.5);
    color:#FCD34D;font-weight:700;font-size:11px;padding:5px 11px;border-radius:999px;
    letter-spacing:.4px}
  .pill{display:flex;align-items:center;gap:7px;font-size:11.5px;color:var(--dim);
    border:1px solid var(--line);padding:5px 11px;border-radius:999px;cursor:pointer}
  .dot{width:8px;height:8px;border-radius:50%;background:var(--dim)}
  .dot.live{background:var(--ok);box-shadow:0 0 8px var(--ok)}
  .dot.mock{background:var(--warn)}
  nav{display:flex;gap:6px;flex-wrap:wrap;padding:14px 26px 0}
  nav button{background:transparent;border:1px solid var(--line);color:var(--dim);
    padding:9px 15px;border-radius:10px;font-size:13px;cursor:pointer;transition:.15s}
  nav button:hover{color:var(--ink)}
  nav button.active{background:linear-gradient(135deg,rgba(50,83,220,.34),rgba(124,58,237,.28));
    border-color:rgba(124,58,237,.5);color:#fff}
  main{padding:20px 26px 60px;max-width:1240px;margin:0 auto}
  .view{display:none;animation:fade .25s ease}
  .view.active{display:block}
  @keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
  .card{background:var(--card);border:1px solid var(--line);border-radius:16px;
    padding:18px;backdrop-filter:blur(7px)}
  h2.section{font-size:20px;margin:2px 0 4px}
  p.lede{color:var(--dim);margin:0 0 16px;font-size:13.5px;max-width:900px}
  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:14px}
  .kpi{background:rgba(2,6,23,.4);border:1px solid var(--line);border-radius:12px;padding:12px 13px}
  .kpi .n{font-size:22px;font-weight:800}
  .kpi .l{font-size:11px;color:var(--dim);margin-top:2px}
  .maprow{display:grid;grid-template-columns:1.55fr 1fr;gap:16px}
  @media(max-width:960px){.maprow{grid-template-columns:1fr}}
  svg{width:100%;height:auto;display:block;border-radius:12px;background:rgba(2,6,23,.35)}
  .zone{fill:rgba(255,255,255,.04);stroke:rgba(148,163,184,.35);stroke-width:1}
  .zone.offsite{stroke-dasharray:5 4;stroke:rgba(56,189,248,.45)}
  .zlabel{fill:var(--dim);font-size:11px;font-weight:600}
  .legend{display:flex;flex-wrap:wrap;gap:12px;margin-top:10px;font-size:11.5px;color:var(--dim)}
  .legend span{display:inline-flex;align-items:center;gap:6px}
  .chip{width:10px;height:10px;border-radius:50%}
  table{width:100%;border-collapse:collapse;font-size:12.5px}
  th,td{text-align:left;padding:8px 9px;border-bottom:1px solid var(--line);vertical-align:top}
  th{color:var(--dim);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.4px}
  tr:hover td{background:rgba(255,255,255,.03)}
  .tag{display:inline-block;padding:2px 8px;border-radius:999px;font-size:10.5px;font-weight:700}
  .mono{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:11.5px}
  .askwrap{display:grid;grid-template-columns:1fr;gap:14px}
  .presets{display:flex;flex-wrap:wrap;gap:8px}
  .presets button{background:rgba(50,83,220,.14);border:1px solid rgba(50,83,220,.4);
    color:#cdd8ff;font-size:12px;padding:7px 11px;border-radius:9px;cursor:pointer}
  .askbar{display:flex;gap:9px}
  .askbar input{flex:1;background:rgba(2,6,23,.5);border:1px solid var(--line);
    color:var(--ink);padding:11px 13px;border-radius:11px;font-size:13.5px}
  .askbar button{background:linear-gradient(135deg,var(--surface),var(--purple));border:0;
    color:#fff;font-weight:700;padding:0 18px;border-radius:11px;cursor:pointer;font-size:13.5px}
  .askbar button:disabled{opacity:.5;cursor:default}
  .out{background:rgba(2,6,23,.45);border:1px solid var(--line);border-radius:13px;
    padding:16px 18px;min-height:120px;font-size:13.5px;line-height:1.55}
  .out h2,.out h3{margin:14px 0 6px}
  .out table{margin:8px 0}
  .out blockquote{border-left:3px solid var(--accent);margin:12px 0 0;padding:6px 12px;
    color:var(--dim);background:rgba(243,111,33,.08);border-radius:0 8px 8px 0}
  .out code{background:rgba(148,163,184,.16);padding:1px 5px;border-radius:5px;font-size:12px}
  .out hr{border:0;border-top:1px solid var(--line);margin:12px 0}
  .metrics{display:flex;flex-wrap:wrap;gap:16px;margin-top:12px;font-size:11.5px;color:var(--dim)}
  .metrics b{color:var(--ink)}
  .ladder{overflow-x:auto}
  .ladder table{min-width:840px}
  .ladder th.dim{width:150px}
  .tierhead{padding:10px;border-radius:10px 10px 0 0;color:#fff;font-weight:700;font-size:13px}
  .tierhead small{display:block;font-weight:500;opacity:.85;font-size:10.5px;margin-top:2px}
  .blade{border:1px solid rgba(10,102,194,.55);border-radius:14px;overflow:hidden;
    background:linear-gradient(180deg,rgba(10,102,194,.12),rgba(2,6,23,.4))}
  .bladebar{background:linear-gradient(90deg,#0A66C2,#0a4f96);padding:10px 16px;display:flex;
    align-items:center;justify-content:space-between}
  .crumb{font-size:12px;color:#dbeafe}
  .crumb b{color:#fff}
  .npu{font-size:10.5px;background:rgba(243,111,33,.25);border:1px solid rgba(243,111,33,.6);
    color:#fed7aa;padding:3px 9px;border-radius:999px;font-weight:700}
  .bladebody{padding:16px}
  .blade.smp{border-color:rgba(15,118,110,.55)}
  .blade.smp .bladebar{background:linear-gradient(90deg,#0f766e,#0b4f4a)}
  .mockbanner{background:repeating-linear-gradient(45deg,rgba(245,158,11,.16),rgba(245,158,11,.16) 12px,rgba(245,158,11,.07) 12px,rgba(245,158,11,.07) 24px);
    border:1px dashed rgba(245,158,11,.6);color:#FCD34D;font-size:11.5px;font-weight:700;
    padding:8px 12px;border-radius:9px;margin-bottom:14px;text-align:center;letter-spacing:.3px}
  .geo{display:grid;grid-template-columns:1fr 1fr;gap:10px}
  @media(max-width:760px){.geo{grid-template-columns:1fr}}
  .geoitem{background:rgba(2,6,23,.4);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
  .alert{display:flex;gap:10px;padding:10px 12px;border-radius:10px;margin-top:8px;
    border:1px solid var(--line);background:rgba(2,6,23,.4)}
  .sev{width:8px;border-radius:4px;flex:0 0 8px}
  .sev.high{background:var(--bad)} .sev.med{background:var(--warn)} .sev.low{background:var(--dim)}
  .alert .d{font-size:11px;color:var(--dim);margin-top:3px}
  .alert .a{font-size:11px;color:#cdd8ff;margin-top:4px}
  .grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
  @media(max-width:760px){.grid2{grid-template-columns:1fr}}
  .benefit{background:rgba(2,6,23,.4);border:1px solid var(--line);border-radius:12px;padding:14px 15px}
  .benefit h4{margin:0 0 6px;font-size:14px}
  .benefit p{margin:0;font-size:12.5px;color:var(--dim);line-height:1.5}
  .relv{font-size:10.5px;font-weight:800;padding:3px 9px;border-radius:999px}
  .relv.high{background:rgba(239,68,68,.18);color:#fecaca;border:1px solid rgba(239,68,68,.5)}
  .relv.medium{background:rgba(245,158,11,.16);color:#fde68a;border:1px solid rgba(245,158,11,.5)}
  .relv.low{background:rgba(148,163,184,.14);color:#cbd5e1;border:1px solid var(--line)}
  .top3{background:rgba(124,58,237,.12);border:1px solid rgba(124,58,237,.4);border-radius:12px;
    padding:12px 14px;margin-bottom:14px;font-size:13px}
  /* scale banner */
  .scalebar{display:flex;flex-wrap:wrap;align-items:center;gap:14px;margin-bottom:12px;
    background:linear-gradient(90deg,rgba(50,83,220,.14),rgba(243,111,33,.10));
    border:1px solid var(--line);border-radius:12px;padding:11px 15px}
  .scaleitem{display:flex;flex-direction:column;line-height:1.15}
  .scaleitem b{font-size:18px;font-weight:800}
  .scaleitem span{font-size:10.5px;color:var(--dim)}
  .scalenote{flex:1;min-width:220px;font-size:11px;color:var(--dim);text-align:right}
  /* lake + lakeside zones */
  .lake{fill:rgba(56,189,248,.14);stroke:rgba(56,189,248,.45);stroke-width:1.5;stroke-dasharray:2 4}
  .lakelabel{fill:rgba(125,211,252,.8);font-size:12px;font-style:italic;font-weight:600}
  .zone.lakeside{stroke:rgba(56,189,248,.65);fill:rgba(56,189,248,.06)}
  /* pipeline flow */
  .flowsteps{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:16px}
  .flowstep{background:rgba(2,6,23,.45);border:1px solid var(--line);border-radius:11px;
    padding:10px 14px;font-size:13px;font-weight:600;display:flex;align-items:center;gap:9px}
  .fnum{width:22px;height:22px;border-radius:50%;background:linear-gradient(135deg,var(--surface),var(--purple));
    display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:800;color:#fff}
  .farrow{color:var(--dim);font-size:18px}
  /* redaction */
  textarea#redactIn{width:100%;background:rgba(2,6,23,.5);border:1px solid var(--line);color:var(--ink);
    padding:11px 13px;border-radius:11px;font-size:13px;resize:vertical;font-family:inherit}
  .redgrid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
  @media(max-width:760px){.redgrid{grid-template-columns:1fr}}
  .redlabel{font-size:10.5px;text-transform:uppercase;letter-spacing:.4px;color:var(--dim);margin-bottom:5px}
  .redbox{border-radius:11px;padding:12px 13px;font-size:12.5px;line-height:1.5;min-height:74px;
    white-space:pre-wrap;font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
  .redbox.raw{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.4)}
  .redbox.red{background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.45)}
  .redchips{margin-top:12px;font-size:12px;display:flex;flex-wrap:wrap;gap:7px;align-items:center}
  .redchip{background:rgba(239,68,68,.14);border:1px solid rgba(239,68,68,.45);color:#fecaca;
    padding:3px 9px;border-radius:999px;font-size:11px;font-weight:700}
  .redkept{margin-top:10px;font-size:12px;color:var(--dim);background:rgba(34,197,94,.07);
    border:1px solid rgba(34,197,94,.3);border-radius:9px;padding:8px 11px}
  .redkept b{color:#bbf7d0}
  .mini{font-size:11px;color:var(--dim);font-weight:400}
  /* prediction */
  #predSel{background:rgba(2,6,23,.5);border:1px solid var(--line);color:var(--ink);
    padding:10px 12px;border-radius:11px;font-size:13.5px;min-width:280px}
  .predhead{display:flex;align-items:center;gap:10px;margin-bottom:12px;font-size:14px}
  .predconf{font-size:10.5px;font-weight:800;padding:3px 9px;border-radius:999px;
    background:rgba(124,58,237,.18);color:#ddd6fe;border:1px solid rgba(124,58,237,.5)}
  .predrow{display:flex;align-items:center;gap:10px;margin:6px 0}
  .predname{width:230px;font-size:12.5px;flex:0 0 230px}
  @media(max-width:620px){.predname{width:140px;flex-basis:140px}}
  .predbar{flex:1;height:14px;background:rgba(2,6,23,.5);border:1px solid var(--line);
    border-radius:999px;overflow:hidden}
  .predfill{height:100%;background:linear-gradient(90deg,var(--surface),var(--accent))}
  .predpct{width:44px;text-align:right;font-size:12px;font-weight:700}
  .predwhy{margin-top:12px;font-size:12.5px;color:var(--dim);line-height:1.55}
  .predwhy b{color:var(--ink)}
  .predmethod{margin-top:10px;font-size:11.5px;color:var(--dim);background:rgba(2,6,23,.4);
    border:1px solid var(--line);border-radius:9px;padding:8px 11px}
  /* servicenow */
  .mockword{background:rgba(245,158,11,.16);border:1px solid rgba(245,158,11,.5);color:#FCD34D;
    font-size:10.5px;font-weight:700;padding:2px 8px;border-radius:999px}
  .snow{background:var(--card);border:1px solid var(--line);border-left:3px solid #16A34A;
    border-radius:12px;padding:14px 16px;margin-bottom:12px}
  .snowhead{display:flex;align-items:center;gap:10px;flex-wrap:wrap}
  .snownum{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:13px;font-weight:700;color:#86efac}
  .snowtype{font-size:11px;color:var(--dim)}
  .snowpri,.snowstate{font-size:10.5px;padding:2px 8px;border-radius:999px;border:1px solid var(--line);color:var(--dim)}
  .snowdesc{font-size:13px;margin-top:6px;font-weight:600}
  .snowmeta{font-size:11.5px;color:var(--dim);margin-top:3px}
  .snowmeta b{color:var(--ink);font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
  .snowloc{display:flex;align-items:stretch;gap:10px;margin-top:11px;flex-wrap:wrap}
  .locbefore,.locafter{flex:1;min-width:200px;border-radius:10px;padding:9px 11px;font-size:12.5px;font-weight:600}
  .locbefore span,.locafter span{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.4px;
    font-weight:700;margin-bottom:3px}
  .locbefore{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.4)}
  .locbefore span{color:#fca5a5}
  .locafter{background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.45)}
  .locafter span{color:#86efac}
  .locarrow{display:flex;align-items:center;color:var(--dim);font-size:20px}
  .snownote{font-size:11.5px;color:var(--dim);margin-top:10px}
  /* utilization */
  .ubar{display:inline-block;width:100px;height:12px;background:rgba(2,6,23,.5);border:1px solid var(--line);
    border-radius:999px;overflow:hidden;vertical-align:middle;margin-right:8px}
  .ufill{height:100%;background:linear-gradient(90deg,#EF4444,#F59E0B)}
  .upct{font-size:12px;font-weight:700}
  .utilnote{font-size:12px;color:var(--dim);margin-top:12px;line-height:1.55}
  .utilnote b{color:var(--ink)}
  .foot{color:var(--dim);font-size:11px;margin-top:18px;text-align:center}
</style>
</head>
<body>
<header>
  <div class="brand">
    <div class="logo">🛰️</div>
    <div>
      <h1>Surface Locus · Zava Health Seattle — Device Location &amp; Fleet Intelligence</h1>
      <p>Local AI on the Surface NPU · Corporate campus on Cedar Lake + WFH · ~123k endpoints · Intune + Surface Management Portal (future-state concept)</p>
    </div>
  </div>
  <div class="badges">
    <span class="proto">PROTOTYPE · MOCK DATA</span>
    <span class="pill" id="statusPill" title="Click to reconnect to Foundry Local">
      <span class="dot mock" id="statusDot"></span><span id="statusText">on-device: mock</span>
    </span>
  </div>
</header>

<nav id="nav">
  <button data-v="map" class="active">🗺️ Fleet Map</button>
  <button data-v="ask">💬 Ask Locus</button>
  <button data-v="intel">🧠 On-Device Intelligence</button>
  <button data-v="snow">🎫 ServiceNow</button>
  <button data-v="util">📊 Utilization</button>
  <button data-v="ladder">🪜 Intune → Locus</button>
  <button data-v="blade">🧩 Locus in Intune</button>
  <button data-v="surface">🖥️ Locus in Surface Portal</button>
  <button data-v="benefits">⚡ Local AI Benefits</button>
  <button data-v="forces">🧭 8 Forces</button>
</nav>

<main>
  <!-- FLEET MAP -->
  <section class="view active" id="view-map">
    <h2 class="section">Live fleet map — Zava Health Seattle corporate campus (Cedar Lake)</h2>
    <p class="lede">A representative sample of Zava Health's ~123,000 managed endpoints: laptops, 2-in-1s and
      workstations across 9 corporate buildings — 3 on the shores of Cedar Lake — plus work-from-home staff and an
      interoffice courier. Pins are colored by status; on-device presence keeps reporting even in RF dead zones.</p>
    <div class="scalebar" id="scaleBar"></div>
    <div class="kpis" id="fleetKpis"></div>
    <div class="maprow">
      <div class="card">
        <svg id="map" viewBox="0 0 1000 560" role="img" aria-label="Campus map"></svg>
        <div class="legend" id="legend"></div>
      </div>
      <div class="card" style="overflow:auto;max-height:560px">
        <table id="fleetTable"><thead><tr>
          <th>Device</th><th>Zone</th><th>Status</th><th>Risk</th><th>Locus</th>
        </tr></thead><tbody></tbody></table>
      </div>
    </div>
  </section>

  <!-- ASK LOCUS -->
  <section class="view" id="view-ask">
    <h2 class="section">Ask Locus — on-device fleet Q&amp;A</h2>
    <p class="lede">Natural-language questions answered by a small language model (phi-3.5-mini) on the
      Copilot+ Surface <b>Surface NPU</b> via Foundry Local. Falls back to a deterministic mock if the runtime
      isn't present — so the story lands on any laptop. Location reasoning stays on the device.</p>
    <div class="askwrap">
      <div class="presets" id="presets"></div>
      <div class="askbar">
        <input id="q" placeholder="e.g. Where is the missing Coding-Tab-08 most likely right now?" />
        <button id="askBtn">Ask on-device</button>
      </div>
      <div class="out" id="answer"><span style="color:var(--dim)">Answer streams here…</span></div>
      <div class="metrics" id="askMetrics"></div>
    </div>
  </section>

  <!-- ON-DEVICE INTELLIGENCE (redact -> predict) -->
  <section class="view" id="view-intel">
    <h2 class="section">On-device intelligence — redact PII, then predict location</h2>
    <p class="lede">The pipeline that never leaves the device: sensitive context (which <b>patient</b> was seen by which
      <b>clinician</b>, MRNs, contact info) is <b>redacted on-device</b>, and only the coarse, tokenized movement signal
      feeds a model that <b>predicts where a device probably is</b> — with a probability distribution.</p>

    <div class="flowsteps">
      <div class="flowstep"><span class="fnum">1</span>Raw context on device</div>
      <div class="farrow">→</div>
      <div class="flowstep"><span class="fnum">2</span>Redact PII (on-device)</div>
      <div class="farrow">→</div>
      <div class="flowstep"><span class="fnum">3</span>Predict location (probabilistic)</div>
    </div>

    <div class="card">
      <h4 style="margin:2px 0 10px">🔒 On-device PII redaction</h4>
      <div class="presets" id="redactPresets"></div>
      <textarea id="redactIn" rows="3" placeholder="Paste a record… e.g. Encounter for Patient Maria Delgado (MRN 00447162), seen by Dr. A. Rivera in Cascade Tower."></textarea>
      <div class="askbar" style="margin-top:8px"><button id="redactBtn">Redact on-device</button></div>
      <div class="redgrid">
        <div><div class="redlabel">Raw (device only)</div><div class="redbox raw" id="redRaw">—</div></div>
        <div><div class="redlabel">Redacted (may sync)</div><div class="redbox red" id="redOut">—</div></div>
      </div>
      <div id="redRemoved" class="redchips"></div>
      <div class="redkept" id="redKept"></div>
    </div>

    <div class="card" style="margin-top:14px">
      <h4 style="margin:2px 0 10px">📍 Predicted location <span class="mini">(from the redacted signal)</span></h4>
      <div class="askbar" style="margin-bottom:12px"><select id="predSel"></select></div>
      <div id="predOut"></div>
    </div>
    <p class="lede" style="margin-top:12px">Prediction uses only the redacted movement features above — no patient or
      clinician identity, no raw coordinates. Estimates are illustrative.</p>
  </section>

  <!-- SERVICENOW -->
  <section class="view" id="view-snow">
    <h2 class="section">ServiceNow dispatch — fill the blank location so techs find the device</h2>
    <p class="lede">Across ~123,000 endpoints, thousands carry a blank or stale CMDB location, so field technicians waste
      truck-rolls hunting for hardware. Locus writes the <b>resolved (or predicted) physical location</b> onto the
      ticket automatically. <span class="mockword">Mock ServiceNow — illustrative.</span></p>
    <div class="kpis" id="snowKpis"></div>
    <div id="snowList"></div>
  </section>

  <!-- UTILIZATION -->
  <section class="view" id="view-util">
    <h2 class="section">Utilization &amp; repurpose — find underused hardware, then locate it</h2>
    <p class="lede">Lakeside <b>SysTrack (DEX)</b> already flags underused endpoints — but "reclaim it" fails when nobody
      knows where it physically is. Fusing DEX utilization with Locus's on-device location makes repurposing
      actionable at fleet scale.</p>
    <div class="kpis" id="utilKpis"></div>
    <div class="card" style="overflow-x:auto"><table id="utilTable"><thead><tr>
      <th>Device</th><th>Building</th><th style="width:170px">Utilization</th><th>Health</th><th>Recommendation</th>
    </tr></thead><tbody></tbody></table></div>
    <div class="utilnote" id="utilNote"></div>
  </section>

  <!-- LADDER -->
  <section class="view" id="view-ladder">
    <h2 class="section">How far Intune goes — and where Local AI takes it</h2>
    <p class="lede">Left: the ceiling of standard Intune / Entra for a Windows fleet today. Middle: this
      prototype's on-device Local AI layer. Right: a future-state concept, "Surface Locus" surfaced
      natively inside Intune and the Surface Management Portal (mock-up, not a real product).</p>
    <div class="card ladder"><table id="ladderTable"></table></div>
  </section>

  <!-- BLADE -->
  <section class="view" id="view-blade">
    <h2 class="section">Future state: "Surface Locus" inside the Intune admin center</h2>
    <p class="lede">A mock-up of what an on-device Locus could look like if it were a first-class blade
      in Intune — always-on low-power presence, fleet geofences, and predictive loss/theft, all powered by
      the Surface NPU.</p>
    <div class="blade">
      <div class="bladebar">
        <div class="crumb" id="crumb"></div>
        <span class="npu" id="npuBadge">Powered by Surface NPU · on-device</span>
      </div>
      <div class="bladebody">
        <div class="mockbanner">⚠️ CONCEPT MOCK-UP — “Surface Locus in Intune” is not a real Microsoft product. Illustrative only.</div>
        <div class="kpis" id="bladeKpis"></div>
        <h4 style="margin:6px 0 8px">Active geofences</h4>
        <div class="geo" id="bladeGeo"></div>
        <h4 style="margin:16px 0 8px">Live alert feed</h4>
        <div id="bladeAlerts"></div>
      </div>
    </div>
  </section>

  <!-- SURFACE MANAGEMENT PORTAL -->
  <section class="view" id="view-surface">
    <h2 class="section">Future state: "Locus" inside the Surface Management Portal</h2>
    <p class="lede">The same on-device location intelligence, surfaced where Surface admins already manage
      hardware — device inventory, DEX health and warranty — now with a live <b>Location</b> column and
      location-driven repurpose / refresh actions. Concept mock-up, not a real product.</p>
    <div class="blade smp">
      <div class="bladebar">
        <div class="crumb" id="crumbS"></div>
        <span class="npu" id="npuBadgeS">Powered by Surface NPU · on-device</span>
      </div>
      <div class="bladebody">
        <div class="mockbanner">⚠️ CONCEPT MOCK-UP — “Locus in the Surface Management Portal” is not a real Microsoft product. Illustrative only.</div>
        <div class="kpis" id="surfKpis"></div>
        <h4 style="margin:6px 0 8px">Device inventory — with Locus location &amp; DEX health</h4>
        <div class="card" style="overflow:auto">
          <table id="surfTable"><thead><tr>
            <th>Surface model</th><th>Device</th><th>Location (Locus)</th><th>DEX health</th><th>Warranty</th><th>Recommended action</th>
          </tr></thead><tbody></tbody></table>
        </div>
        <h4 style="margin:16px 0 8px">Fleet insights</h4>
        <div class="grid2" id="surfInsights"></div>
      </div>
    </div>
  </section>

  <!-- BENEFITS -->
  <section class="view" id="view-benefits">
    <h2 class="section">Why Local AI — benefits for device tracking</h2>
    <p class="lede">What moving the tracking intelligence on-device (Surface NPU) buys you, specifically for
      a medical campus + WFH scenario.</p>
    <div class="grid2" id="benefits"></div>
  </section>

  <!-- FORCES -->
  <section class="view" id="view-forces">
    <h2 class="section">The 8 Forces of Local AI — triaged for this use case</h2>
    <p class="lede" id="forcesNote"></p>
    <div class="top3" id="top3"></div>
    <div class="card" style="overflow-x:auto">
      <table id="forcesTable"><thead><tr>
        <th style="width:44px">Rank</th><th>Force</th><th style="width:110px">Relevance</th><th>Why it matters here</th>
      </tr></thead><tbody></tbody></table>
    </div>
  </section>

  <div class="foot">Prototype for demonstration only · fabricated data · not a shipping product ·
    Zava Health is a fictional demo brand · building names, ServiceNow tickets and figures are illustrative ·
    Placeholder branding, not official Microsoft / Surface / Intune / Zava Health marks.</div>
</main>

<script>
const $ = s => document.querySelector(s);
const esc = s => (s==null?'':String(s)).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');

// ---- tiny markdown renderer (headings, bold, code, lists, tables, quote, hr)
function inline(t){
  return esc(t)
    .replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>')
    .replace(/\*([^*]+)\*/g,'<i>$1</i>')
    .replace(/`([^`]+)`/g,'<code>$1</code>');
}
function md(src){
  const lines = (src||'').replace(/\r/g,'').split('\n');
  let html='', i=0, para=[];
  const flush=()=>{ if(para.length){ html+='<p>'+para.map(inline).join(' ')+'</p>'; para=[]; } };
  while(i<lines.length){
    let ln = lines[i];
    if(/^\s*$/.test(ln)){ flush(); i++; continue; }
    if(/^\s*(---|\*\*\*)\s*$/.test(ln)){ flush(); html+='<hr/>'; i++; continue; }
    let h = ln.match(/^\s*(#{1,4})\s+(.*)$/);
    if(h){ flush(); const n=h[1].length; html+='<h'+n+'>'+inline(h[2])+'</h'+n+'>'; i++; continue; }
    if(/^\s*>\s?/.test(ln)){ flush(); let q=[]; while(i<lines.length&&/^\s*>\s?/.test(lines[i])){ q.push(lines[i].replace(/^\s*>\s?/,'')); i++; } html+='<blockquote>'+q.map(inline).join(' ')+'</blockquote>'; continue; }
    // table
    if(/^\s*\|.*\|\s*$/.test(ln) && i+1<lines.length && /^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i+1]) && lines[i+1].indexOf('-')>=0){
      flush();
      const cells = r => r.replace(/^\s*\|/,'').replace(/\|\s*$/,'').split('|').map(c=>c.trim());
      const head = cells(ln); i+=2; let rows=[];
      while(i<lines.length && /^\s*\|.*\|\s*$/.test(lines[i])){ rows.push(cells(lines[i])); i++; }
      html+='<table><thead><tr>'+head.map(c=>'<th>'+inline(c)+'</th>').join('')+'</tr></thead><tbody>'+
        rows.map(r=>'<tr>'+r.map(c=>'<td>'+inline(c)+'</td>').join('')+'</tr>').join('')+'</tbody></table>';
      continue;
    }
    // lists
    if(/^\s*([-*]|\d+\.)\s+/.test(ln)){
      flush(); const ordered=/^\s*\d+\.\s+/.test(ln); let items=[];
      while(i<lines.length && /^\s*([-*]|\d+\.)\s+/.test(lines[i])){ items.push(lines[i].replace(/^\s*([-*]|\d+\.)\s+/,'')); i++; }
      html+=(ordered?'<ol>':'<ul>')+items.map(t=>'<li>'+inline(t)+'</li>').join('')+(ordered?'</ol>':'</ul>');
      continue;
    }
    para.push(ln.trim()); i++;
  }
  flush();
  return html;
}

// ---- nav
function activateView(v){
  const btn=document.querySelector('#nav button[data-v="'+v+'"]'); if(!btn) return;
  document.querySelectorAll('#nav button').forEach(x=>x.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.view').forEach(x=>x.classList.remove('active'));
  $('#view-'+v).classList.add('active');
}
document.querySelectorAll('#nav button').forEach(b=>b.onclick=()=>{
  activateView(b.dataset.v);
  history.replaceState(null,'','#'+b.dataset.v);
});
window.addEventListener('hashchange',()=>{ const v=location.hash.replace('#',''); if(v) activateView(v); });
if(location.hash){ const v=location.hash.replace('#',''); if(document.querySelector('#view-'+v)) activateView(v); }

// ---- status pill
async function refreshStatus(){
  try{
    const m = await (await fetch('/api/status')).json();
    const dot=$('#statusDot'), txt=$('#statusText');
    if(m.loading){ dot.className='dot'; txt.textContent='on-device: warming NPU…'; }
    else if(m.live){ dot.className='dot live'; txt.textContent='on-device: '+m.device+' · '+m.model; }
    else { dot.className='dot mock'; txt.textContent='on-device: mock (Foundry Local not found)'; }
  }catch(e){}
}
$('#statusPill').onclick=async()=>{ $('#statusText').textContent='reconnecting…';
  try{ await fetch('/api/reconnect',{method:'POST'}); }catch(e){} refreshStatus(); };

// ---- FLEET
const UNKNOWN={x:875,y:500,name:'Last-known / off-network (unresolved)'};
let ZMETA={};
async function loadFleet(){
  const f = await (await fetch('/api/fleet')).json();
  ZMETA=f.status_meta;
  const s=f.summary, sc=f.scale||s.scale||{};
  // scale banner
  $('#scaleBar').innerHTML=[
    ['Managed endpoints',(sc.total_endpoints||0).toLocaleString()],
    ['Unknown / stale location','~'+(sc.unknown_location||0).toLocaleString()],
    ['Underused (fleet est.)','~'+(sc.underused_estimate||0).toLocaleString()],
    ['Shown here',(sc.sample_shown||s.total)+' sample']
  ].map(k=>`<div class="scaleitem"><b>${k[1]}</b><span>${k[0]}</span></div>`).join('')+
    `<div class="scalenote">${esc(sc.note||'')}</div>`;
  // KPIs
  $('#fleetKpis').innerHTML=[
    ['Sample devices',s.total],['On-campus',s.campus],['WFH',s.wfh],
    ['In transit',s.transit],['Locus-enrolled',s.locus_enrolled+' / '+s.total],
    ['High-risk (≥60)',s.high_risk],['Underused (<25%)',s.underused]
  ].map(k=>`<div class="kpi"><div class="n">${k[1]}</div><div class="l">${k[0]}</div></div>`).join('');
  // map
  const zById={}; f.zones.forEach(z=>zById[z.id]=z);
  const C=f.campus||{}, lake=C.lake||{}, divX=C.divider_x||790;
  let svg='';
  if(lake.cx){
    svg+=`<ellipse cx="${lake.cx}" cy="${lake.cy}" rx="${lake.rx}" ry="${lake.ry}" class="lake"/>`;
    svg+=`<text x="${lake.cx}" y="${lake.cy}" text-anchor="middle" class="lakelabel">${esc(lake.label||'Lake')}</text>`;
  }
  svg+=`<line x1="${divX}" y1="20" x2="${divX}" y2="540" stroke="rgba(148,163,184,.25)" stroke-dasharray="4 5"/>`;
  svg+=`<text x="${divX+12}" y="34" class="zlabel" fill="#7dd3fc">OFF-CAMPUS</text>`;
  f.zones.forEach(z=>{
    const cls='zone'+(z.kind==='offsite'?' offsite':'')+(z.lakeside?' lakeside':'');
    svg+=`<rect class="${cls}" x="${z.x-66}" y="${z.y-30}" width="132" height="60" rx="9"/>`;
    svg+=`<text class="zlabel" x="${z.x}" y="${z.y-14}" text-anchor="middle">${esc(z.name)}</text>`;
  });
  const groups={};
  f.devices.forEach(d=>{ const z=zById[d.zone]; const key=z?d.zone:'__unknown'; (groups[key]=groups[key]||[]).push(d); });
  Object.keys(groups).forEach(key=>{
    const anchor = key==='__unknown'?UNKNOWN:zById[key];
    groups[key].forEach((d,idx)=>{
      const per=4, col=idx%per, row=Math.floor(idx/per);
      const px=anchor.x-30+col*20, py=anchor.y+6+row*14;
      const c=(ZMETA[d.status]||{}).color||'#94a3b8';
      const ring = d.status==='missing'?' stroke="#fff" stroke-dasharray="2 2" stroke-width="1.5"':'';
      svg+=`<circle cx="${px}" cy="${py}" r="6" fill="${c}"${ring}><title>${esc(d.id+' · '+d.name+' — '+((ZMETA[d.status]||{}).label||d.status)+' (risk '+d.risk+')')}</title></circle>`;
    });
    if(key==='__unknown'){
      svg+=`<text class="zlabel" x="${UNKNOWN.x}" y="${UNKNOWN.y-14}" text-anchor="middle" fill="#fca5a5">${esc(UNKNOWN.name)}</text>`;
    }
  });
  $('#map').innerHTML=svg;
  $('#legend').innerHTML=Object.keys(ZMETA).map(k=>`<span><span class="chip" style="background:${ZMETA[k].color}"></span>${esc(ZMETA[k].label)}</span>`).join('');
  $('#fleetTable tbody').innerHTML=f.devices.map(d=>{
    const m=ZMETA[d.status]||{}; const zn=(zById[d.zone]||{}).name||d.zone;
    return `<tr>
      <td><span class="mono">${esc(d.id)}</span><br><span style="color:var(--dim)">${esc(d.name)}</span></td>
      <td>${esc(zn)}</td>
      <td><span class="tag" style="background:${(m.color||'#334155')}22;color:${m.color||'#cbd5e1'};border:1px solid ${(m.color||'#334155')}66">${esc(m.label||d.status)}</span></td>
      <td>${d.risk}</td>
      <td>${d.locus?'✅':'—'}</td>
    </tr>`;
  }).join('');
}

// ---- ASK
const PRESETS=[
  'Which devices left a lakeside building after 18:00?',
  'Where is the missing Coding-Tab-08 most likely right now?',
  'What leaves the device after redaction for a coding tablet?',
  'Which underused devices can we reclaim, and where are they?',
  'Summarize the missing Coding-Tab-08 incident and recommend next steps.',
  'Triage my highest-risk WFH laptops right now.'
];
$('#presets').innerHTML=PRESETS.map((p,i)=>`<button data-p="${i}">${esc(p)}</button>`).join('');
document.querySelectorAll('#presets button').forEach(b=>b.onclick=()=>{ $('#q').value=PRESETS[b.dataset.p]; ask(); });
$('#askBtn').onclick=ask;
$('#q').addEventListener('keydown',e=>{ if(e.key==='Enter') ask(); });

let busy=false;
async function ask(){
  const q=$('#q').value.trim(); if(!q||busy) return;
  busy=true; $('#askBtn').disabled=true;
  const out=$('#answer'); out.innerHTML='<span style="color:var(--dim)">🛰️ reasoning on-device…</span>';
  let raw='';
  try{
    const res=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:q})});
    const reader=res.body.getReader(); const dec=new TextDecoder();
    while(true){ const {done,value}=await reader.read(); if(done) break;
      raw+=dec.decode(value,{stream:true}); out.innerHTML=md(raw); }
    out.innerHTML=md(raw);
  }catch(e){ out.innerHTML='<span style="color:var(--bad)">Error: '+esc(e.message)+'</span>'; }
  busy=false; $('#askBtn').disabled=false;
  refreshStatus(); refreshAskMetrics();
}
async function refreshAskMetrics(){
  try{ const m=await (await fetch('/api/status')).json();
    $('#askMetrics').innerHTML=[
      ['device',m.live?m.device:'mock'],['model',m.live?m.model:'deterministic'],
      ['requests',m.requests],['avg latency',m.avg_ms+' ms'],['tokens',m.tokens]
    ].map(x=>`<span>${x[0]}: <b>${esc(x[1])}</b></span>`).join('');
  }catch(e){}
}

// ---- LADDER
async function loadLadder(){
  const L=await (await fetch('/api/ladder')).json();
  let h='<thead><tr><th class="dim"></th>';
  L.tiers.forEach(t=>{ h+=`<th style="padding:0"><div class="tierhead" style="background:${t.accent}">${esc(t.name)}<small>${esc(t.tag)}</small></div></th>`; });
  h+='</tr><tr><th class="dim"></th>'+L.tiers.map(t=>`<td style="color:var(--dim);font-size:11.5px">${esc(t.blurb)}</td>`).join('')+'</tr></thead><tbody>';
  L.dimensions.forEach((dim,r)=>{
    h+=`<tr><th class="dim">${esc(dim)}</th>`+L.tiers.map(t=>`<td>${esc(t.rows[r])}</td>`).join('')+'</tr>';
  });
  h+='</tbody>'; $('#ladderTable').innerHTML=h;
}

// ---- BLADE
async function loadBlade(){
  const b=await (await fetch('/api/blade')).json();
  $('#crumb').innerHTML=b.breadcrumb.map((c,i)=>i===b.breadcrumb.length-1?'<b>'+esc(c)+'</b>':esc(c)).join(' <span style="opacity:.5">›</span> ');
  $('#bladeKpis').innerHTML=b.kpis.map(k=>`<div class="kpi"><div class="n" style="font-size:18px">${esc(k.value)}</div><div class="l">${esc(k.label)}</div><div class="l" style="color:#7dd3fc">${esc(k.hint)}</div></div>`).join('');
  $('#bladeGeo').innerHTML=b.geofences.map(g=>`<div class="geoitem"><b>${esc(g.name)}</b><div class="l" style="color:var(--dim);font-size:11.5px;margin-top:3px">${g.devices} device(s) · ${esc(g.state)}</div></div>`).join('');
  $('#bladeAlerts').innerHTML=b.alerts.map(a=>`<div class="alert"><div class="sev ${a.sev}"></div><div><b>${esc(a.device)}</b><div class="d">${esc(a.text)}</div><div class="a">↳ ${esc(a.action)}</div></div></div>`).join('');
}

// ---- SURFACE MANAGEMENT PORTAL
async function loadSurface(){
  const s=await (await fetch('/api/surface')).json();
  $('#crumbS').innerHTML=s.breadcrumb.map((c,i)=>i===s.breadcrumb.length-1?'<b>'+esc(c)+'</b>':esc(c)).join(' <span style="opacity:.5">›</span> ');
  $('#surfKpis').innerHTML=s.kpis.map(k=>`<div class="kpi"><div class="n" style="font-size:18px">${esc(k.value)}</div><div class="l">${esc(k.label)}</div><div class="l" style="color:#7dd3fc">${esc(k.hint)}</div></div>`).join('');
  $('#surfTable tbody').innerHTML=s.devices.map(d=>`<tr><td><b>${esc(d.model)}</b><div class="l" style="color:var(--dim);font-size:11px">${esc(d.silicon)}</div></td><td>${esc(d.device)}</td><td>${esc(d.location)}</td><td>${esc(d.health)}</td><td>${esc(d.warranty)}</td><td>${esc(d.action)}</td></tr>`).join('');
  $('#surfInsights').innerHTML=s.insights.map(x=>`<div class="benefit"><h4>${esc(x.title)}</h4><p>${esc(x.body)}</p></div>`).join('');
}

// ---- BENEFITS
async function loadBenefits(){
  const B=await (await fetch('/api/benefits')).json();
  $('#benefits').innerHTML=B.map(x=>`<div class="benefit"><h4>${esc(x.title)}</h4><p>${esc(x.body)}</p></div>`).join('');
}

// ---- FORCES
async function loadForces(){
  const F=await (await fetch('/api/forces')).json();
  $('#forcesNote').textContent=F.note;
  const byId={}; F.forces.forEach(f=>byId[f.id]=f);
  $('#top3').innerHTML='<b>Most relevant here:</b> '+F.top_three.map((id,i)=>`${i+1}. ${esc(byId[id].name)}`).join('  ·  ')+
    ' <span style="color:var(--dim)">— privacy, resilience and real-time latency dominate a HIPAA-bound, dead-zone-heavy environment.</span>';
  const sorted=[...F.forces].sort((a,b)=>a.rank-b.rank);
  $('#forcesTable tbody').innerHTML=sorted.map(f=>`<tr>
    <td><b>${f.rank}</b></td><td><b>${esc(f.name)}</b><div class="l" style="color:var(--dim);font-size:11px;margin-top:2px;font-style:italic">${esc(f.question||'')}</div></td>
    <td><span class="relv ${f.relevance}">${f.relevance.toUpperCase()}</span></td>
    <td>${esc(f.why)}</td></tr>`).join('');
}

// ---- ON-DEVICE INTELLIGENCE (redact -> predict)
let PREDS={};
async function initIntel(){
  try{
    const ex=await (await fetch('/api/redact/examples')).json();
    $('#redactPresets').innerHTML=ex.map((e,i)=>`<button data-r="${i}">${esc(e.label)}</button>`).join('');
    document.querySelectorAll('#redactPresets button').forEach(b=>b.onclick=()=>{ $('#redactIn').value=ex[b.dataset.r].raw; doRedact(ex[b.dataset.r].kept); });
  }catch(e){}
  $('#redactBtn').onclick=()=>doRedact();
  try{
    PREDS=await (await fetch('/api/predict')).json();
    $('#predSel').innerHTML=Object.keys(PREDS).map(k=>`<option value="${k}">${esc(PREDS[k].device)}</option>`).join('');
    $('#predSel').onchange=()=>renderPred($('#predSel').value);
    const first=Object.keys(PREDS)[0]; if(first) renderPred(first);
  }catch(e){}
}
async function doRedact(kept){
  const text=$('#redactIn').value.trim(); if(!text) return;
  $('#redRaw').textContent=text;
  try{
    const r=await (await fetch('/api/redact',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})})).json();
    $('#redOut').textContent=r.redacted;
    const byType={}; (r.removed||[]).forEach(x=>{ byType[x.type]=(byType[x.type]||0)+1; });
    const keys=Object.keys(byType);
    $('#redRemoved').innerHTML='<span class="redlabel" style="display:inline">Removed on-device:</span> '+
      (keys.length?keys.map(t=>`<span class="redchip">${esc(t)} ×${byType[t]}</span>`).join(''):'<span style="color:var(--dim)">nothing sensitive found</span>');
    $('#redKept').innerHTML='<b>Kept for location modeling:</b> '+esc(kept||'coarse building zone + time bucket only');
  }catch(e){ $('#redOut').textContent='error'; }
}
function renderPred(id){
  const p=PREDS[id]; if(!p){ $('#predOut').innerHTML=''; return; }
  const bars=p.candidates.map(c=>`<div class="predrow"><div class="predname">${esc(c.name)}</div>
    <div class="predbar"><div class="predfill" style="width:${c.prob}%"></div></div>
    <div class="predpct">${c.prob}%</div></div>`).join('');
  $('#predOut').innerHTML=`<div class="predhead"><span class="predconf">${esc(p.confidence)}</span><b>${esc(p.headline)}</b></div>
    ${bars}
    <div class="predwhy"><b>Rationale.</b> ${esc(p.rationale)}</div>
    <div class="predmethod">🔒 ${esc(p.method)}</div>`;
}

// ---- SERVICENOW
async function loadServiceNow(){
  const d=await (await fetch('/api/servicenow')).json();
  $('#snowKpis').innerHTML=[
    ['Auto-located (sample)',d.summary.auto_located],
    ['Fleet unknown-location','~'+(d.summary.fleet_unknown_before||0).toLocaleString()],
    ['Tickets shown',d.tickets.length]
  ].map(k=>`<div class="kpi"><div class="n">${k[1]}</div><div class="l">${k[0]}</div></div>`).join('');
  $('#snowList').innerHTML=d.tickets.map(t=>`
    <div class="snow">
      <div class="snowhead"><span class="snownum">${esc(t.number)}</span>
        <span class="snowtype">${esc(t.type)}</span>
        <span class="snowpri">${esc(t.priority)}</span>
        <span class="snowstate">${esc(t.state)}</span></div>
      <div class="snowdesc">${esc(t.short_desc)}</div>
      <div class="snowmeta">CI <b>${esc(t.ci)}</b> · ${esc(t.group)}</div>
      <div class="snowloc">
        <div class="locbefore"><span>Location before</span>${esc(t.loc_before)}</div>
        <div class="locarrow">→</div>
        <div class="locafter"><span>Locus location (${t.conf}%)</span>${esc(t.loc_after)}</div>
      </div>
      <div class="snownote">🛡️ ${esc(t.note)}</div>
    </div>`).join('')+`<div class="utilnote">${esc(d.summary.note)}</div>`;
}

// ---- UTILIZATION
async function loadUtil(){
  const u=await (await fetch('/api/utilization')).json();
  const su=u.summary||{};
  $('#utilKpis').innerHTML=[
    ['Underused (sample)',su.sample_underused],
    ['Underused (fleet est.)','~'+(su.fleet_underused_est||0).toLocaleString()],
    ['Est. annual savings',su.annual_savings_est],
    ['Threshold',su.threshold]
  ].map(k=>`<div class="kpi"><div class="n" style="font-size:16px">${esc(k[1])}</div><div class="l">${esc(k[0])}</div></div>`).join('');
  $('#utilTable tbody').innerHTML=(u.candidates||[]).map(c=>`<tr>
    <td><span class="mono">${esc(c.id)}</span><br><span style="color:var(--dim)">${esc(c.name)}</span></td>
    <td>${esc(c.building)}</td>
    <td><div class="ubar"><div class="ufill" style="width:${c.util}%"></div></div><span class="upct">${c.util}%</span></td>
    <td>${c.health}</td>
    <td>${esc(c.recommendation)}</td>
  </tr>`).join('');
  $('#utilNote').innerHTML='<b>Source:</b> '+esc(u.source||'')+'. '+esc(u.note||'');
}

// ---- boot
loadFleet(); loadLadder(); loadBlade(); loadSurface(); loadBenefits(); loadForces();
initIntel(); loadServiceNow(); loadUtil();
refreshStatus(); setInterval(refreshStatus, 6000);
// presenter reset
document.addEventListener('keydown',e=>{ if(e.shiftKey && (e.key==='R'||e.key==='r')){ refreshStatus(); } });
</script>
</body>
</html>"""


if __name__ == "__main__":
    print("Surface Locus prototype -> http://127.0.0.1:5075  (PROTOTYPE / mock data)")
    app.run(host="127.0.0.1", port=5075, threaded=True)
