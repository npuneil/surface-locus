/* Surface Locus - Executive Pitch Deck generator (pptxgenjs)
 * Writes a ~6-slide executive deck to the user's Downloads folder.
 * PROTOTYPE / mock data - all figures illustrative.
 */
const pptxgen = require("pptxgenjs");
const p = new pptxgen();
p.defineLayout({ name: "W16x9", width: 13.333, height: 7.5 });
p.layout = "W16x9";
const W = 13.333, H = 7.5;

// ---- palette (deep navy dominant, amber sharp accent) ----
const NAVY = "0B1B34";   // dark bg
const INK  = "12294A";   // panels on dark
const LIGHT= "F4F7FB";   // content bg
const CARD = "FFFFFF";   // cards on light
const BLUE = "1E5FBF";   // primary accent
const SKY  = "5AA9FF";   // light accent on dark
const TEAL = "0FB5AE";   // secondary
const AMBER= "F5A623";   // stat accent
const GREEN= "16A34A";   // savings / positive
const RED  = "E5484D";   // problem / pain
const SLATE= "5B6B82";   // muted body
const ICE  = "CADCFC";   // ice blue on dark
const HEAD = "Trebuchet MS";
const BODY = "Calibri";

const sh = () => ({ type: "outer", color: "9FB2CC", blur: 7, offset: 2, angle: 90, opacity: 0.35 });

function bg(slide, color){ slide.background = { color }; }
function rrect(slide, o){ slide.addShape(p.ShapeType.roundRect, Object.assign({ line:{type:"none"}, rectRadius:0.08 }, o)); }
function rect(slide, o){ slide.addShape(p.ShapeType.rect, Object.assign({ line:{type:"none"} }, o)); }
function circle(slide, o){ slide.addShape(p.ShapeType.ellipse, Object.assign({ line:{type:"none"} }, o)); }

// prototype pill (top-right)
function protoPill(slide, dark){
  rrect(slide, { x: W-3.25, y: 0.42, w: 2.75, h: 0.42, fill:{color: AMBER}, rectRadius:0.21 });
  slide.addText("PROTOTYPE  \u00B7  MOCK DATA", { x: W-3.25, y: 0.42, w: 2.75, h: 0.42,
    fontFace: HEAD, fontSize: 11, bold:true, color:"3A2A00", align:"center", valign:"middle", charSpacing:1 });
}
function footer(slide, dark){
  slide.addText(
    "Prototype for demonstration only \u00B7 fabricated data \u00B7 not a shipping product \u00B7 Zava Health is a fictional demo brand \u00B7 placeholder branding, not official Microsoft / Surface / Intune marks",
    { x:0.6, y: H-0.5, w: W-1.2, h:0.35, fontFace: BODY, fontSize: 8, italic:true,
      color: dark ? "6C81A6" : "9AA7BC", align: dark ? "left":"left", valign:"middle" });
}
function eyebrow(slide, txt, x, y, color){
  slide.addText(txt, { x, y, w: 8, h:0.3, fontFace: HEAD, fontSize: 12.5, bold:true,
    color, charSpacing:2, align:"left", valign:"middle", margin:0 });
}

/* ============================ SLIDE 1 - TITLE ============================ */
(function(){
  const s = p.addSlide(); bg(s, NAVY);
  // motif: large translucent rings bottom-right (a "location pin" radar feel)
  circle(s, { x: W-4.6, y: H-4.2, w: 6.2, h: 6.2, fill:{ color: BLUE, transparency: 86 } });
  circle(s, { x: W-3.5, y: H-3.1, w: 4.0, h: 4.0, fill:{ color: SKY, transparency: 88 } });
  circle(s, { x: W-2.55, y: H-2.15, w: 2.1, h: 2.1, fill:{ color: TEAL, transparency: 80 } });
  circle(s, { x: W-1.72, y: H-1.32, w: 0.44, h: 0.44, fill:{ color: AMBER } }); // pin dot
  // left accent bar
  rect(s, { x:0.6, y:2.15, w:0.14, h:2.55, fill:{color: AMBER} });
  protoPill(s, true);
  eyebrow(s, "MICROSOFT SURFACE  \u00B7  LOCAL AI ON THE COPILOT+ NPU", 0.9, 1.7, SKY);
  s.addText("Surface Locus", { x:0.85, y:2.05, w:10.5, h:1.5, fontFace: HEAD, fontSize:60, bold:true, color:"FFFFFF", align:"left", valign:"middle", margin:0 });
  s.addText("Device location & fleet intelligence for the Zava Health endpoint estate", { x:0.9, y:3.55, w:9.6, h:0.9, fontFace: BODY, fontSize:22, color: ICE, align:"left", valign:"middle", margin:0 });
  // chip row
  const chips = ["~123,000 endpoints", "9-building Cedar Lake campus + WFH", "Private, on-device AI"];
  let cx = 0.9;
  chips.forEach(c=>{
    const w = 0.34 + c.length*0.108;
    rrect(s, { x:cx, y:4.75, w, h:0.5, fill:{color: INK}, line:{color:"274063", type:"solid", width:1}, rectRadius:0.25 });
    s.addText(c, { x:cx, y:4.75, w, h:0.5, fontFace: BODY, fontSize:13, bold:true, color:"D8E4F7", align:"center", valign:"middle", margin:0 });
    cx += w + 0.22;
  });
  footer(s, true);
})();

/* ============================ SLIDE 2 - PROBLEM ============================ */
(function(){
  const s = p.addSlide(); bg(s, LIGHT);
  s.addText("The problem: a fleet you can\u2019t fully see", { x:0.6, y:0.55, w:9.5, h:0.8, fontFace: HEAD, fontSize:34, bold:true, color: NAVY, align:"left", valign:"middle", margin:0 });
  s.addText("Intune and DEX tell you a device exists and how healthy it is \u2014 not where it physically is, right now.", { x:0.62, y:1.42, w:8.4, h:0.5, fontFace: BODY, fontSize:15, color: SLATE, align:"left", valign:"middle", margin:0 });

  // left: pain rows
  const pains = [
    ["Techs can\u2019t locate devices", "Field technicians burn hours hunting for endpoints that need a fix, swap or recall."],
    ["Dead zones swallow signal", "Shielded server rooms, parking decks, stairwells and the lakefront break cloud-only tracking."],
    ["WFH sprawl", "Thousands of endpoints live off-campus with no reliable location or presence."],
    ["Wasted & at-risk hardware", "Underused devices go unclaimed; lost/stolen endpoints carry regulated PHI."],
  ];
  let y = 2.25;
  pains.forEach(pr=>{
    circle(s, { x:0.62, y:y+0.04, w:0.34, h:0.34, fill:{color: RED} });
    s.addText("!", { x:0.62, y:y+0.04, w:0.34, h:0.34, fontFace: HEAD, fontSize:16, bold:true, color:"FFFFFF", align:"center", valign:"middle", margin:0 });
    s.addText([
      { text: pr[0]+"\n", options:{ fontFace: HEAD, fontSize:15.5, bold:true, color: NAVY } },
      { text: pr[1], options:{ fontFace: BODY, fontSize:12.5, color: SLATE } },
    ], { x:1.08, y:y-0.06, w:5.5, h:1.0, align:"left", valign:"top", margin:0, lineSpacingMultiple:1.0 });
    y += 1.12;
  });

  // right: 2x2 stat grid
  const stats = [
    ["~123K", "managed endpoints", BLUE],
    ["~4,200", "with unknown location", RED],
    ["9", "campus buildings on Cedar Lake", TEAL],
    ["1,000s", "WFH devices off-campus", AMBER],
  ];
  const gx=7.05, gy=2.2, cw=2.85, ch=1.95, gap=0.3;
  stats.forEach((st,i)=>{
    const x = gx + (i%2)*(cw+gap);
    const yy = gy + Math.floor(i/2)*(ch+gap);
    rrect(s, { x, y:yy, w:cw, h:ch, fill:{color: CARD}, shadow: sh() });
    rect(s, { x, y:yy, w:0.12, h:ch, fill:{color: st[2]} });
    s.addText(st[0], { x:x+0.25, y:yy+0.22, w:cw-0.4, h:0.9, fontFace: HEAD, fontSize:40, bold:true, color: st[2], align:"left", valign:"middle", margin:0 });
    s.addText(st[1], { x:x+0.27, y:yy+1.12, w:cw-0.45, h:0.7, fontFace: BODY, fontSize:13, color: NAVY, align:"left", valign:"top", margin:0 });
  });
  footer(s, false);
})();

/* ============================ SLIDE 3 - SOLUTION ============================ */
(function(){
  const s = p.addSlide(); bg(s, LIGHT);
  // navy hero band with the one-liner
  rect(s, { x:0, y:0, w:W, h:2.35, fill:{color: NAVY} });
  rect(s, { x:0, y:2.35, w:W, h:0.08, fill:{color: AMBER} });
  eyebrow(s, "THE SOLUTION", 0.6, 0.5, SKY);
  s.addText("On-device AI that always knows where every Surface is \u2014 without moving patient data.", { x:0.6, y:0.86, w:12.1, h:1.3, fontFace: HEAD, fontSize:27, bold:true, color:"FFFFFF", align:"left", valign:"middle", margin:0 });

  // 4 capability cards
  const caps = [
    ["Redact PHI on-device", "Patient\u2194clinician links & MRNs scrubbed on the NPU before anything syncs.", TEAL, "\u25C9"],
    ["Predict location", "A probability distribution of where a device is \u2014 from the redacted signal only.", BLUE, "\u25C9"],
    ["Dispatch via ServiceNow", "Resolved / predicted location written onto the ticket so techs go straight there.", AMBER, "\u25A3"],
    ["Reclaim hardware", "Fuse Lakeside SysTrack (DEX) usage + location to repurpose underused devices.", GREEN, "\u267B"],
  ];
  const n=caps.length, m=0.6, gap=0.32;
  const cw = (W - 2*m - (n-1)*gap)/n, cy=2.95, ch=2.75;
  caps.forEach((c,i)=>{
    const x = m + i*(cw+gap);
    rrect(s, { x, y:cy, w:cw, h:ch, fill:{color: CARD}, shadow: sh() });
    rect(s, { x, y:cy, w:cw, h:0.12, fill:{color: c[2]} });
    circle(s, { x:x+0.28, y:cy+0.34, w:0.72, h:0.72, fill:{color: c[2]} });
    s.addText(c[3], { x:x+0.28, y:cy+0.34, w:0.72, h:0.72, fontFace: HEAD, fontSize:24, bold:true, color:"FFFFFF", align:"center", valign:"middle", margin:0 });
    s.addText(c[0], { x:x+0.24, y:cy+1.18, w:cw-0.45, h:0.7, fontFace: HEAD, fontSize:15.5, bold:true, color: NAVY, align:"left", valign:"top", margin:0 });
    s.addText(c[1], { x:x+0.24, y:cy+1.72, w:cw-0.45, h:0.95, fontFace: BODY, fontSize:11.5, color: SLATE, align:"left", valign:"top", margin:0, lineSpacingMultiple:1.02 });
  });
  // bottom band: where it surfaces
  rrect(s, { x:0.6, y:6.05, w:W-1.2, h:0.72, fill:{color:"E7EEF9"} });
  s.addText([
    { text:"Surfaced where IT already works:  ", options:{ fontFace: HEAD, fontSize:13.5, bold:true, color: NAVY } },
    { text:"Microsoft Intune", options:{ fontFace: BODY, fontSize:13.5, bold:true, color: BLUE } },
    { text:"   +   ", options:{ fontFace: BODY, fontSize:13.5, color: SLATE } },
    { text:"Surface Management Portal", options:{ fontFace: BODY, fontSize:13.5, bold:true, color: BLUE } },
    { text:"   \u00B7  an added layer, not a rip-and-replace.", options:{ fontFace: BODY, fontSize:13.5, italic:true, color: SLATE } },
  ], { x:0.6, y:6.05, w:W-1.2, h:0.72, align:"center", valign:"middle", margin:0 });
  footer(s, false);
})();

/* ============================ SLIDE 4 - HOW IT WORKS ============================ */
(function(){
  const s = p.addSlide(); bg(s, LIGHT);
  s.addText("How it works: private by design", { x:0.6, y:0.55, w:10, h:0.8, fontFace: HEAD, fontSize:34, bold:true, color: NAVY, align:"left", valign:"middle", margin:0 });
  s.addText("Raw location and PHI stay on the device. Only a de-identified coarse zone + time bucket ever syncs.", { x:0.62, y:1.4, w:11.5, h:0.5, fontFace: BODY, fontSize:15, color: SLATE, align:"left", valign:"middle", margin:0 });

  // pipeline: 4 on-device nodes then a fan-out
  const nodes = [
    ["On-device\nsignal", "Wi-Fi / BT / cell presence on the endpoint", INK],
    ["Redact PHI\n(NPU)", "Patient\u2194clinician, MRN, contact scrubbed", TEAL],
    ["Predict\nlocation", "Probability distribution of the device", BLUE],
    ["Sync clean\nzone", "Coarse zone + time bucket only", GREEN],
  ];
  const nx0=0.7, ny=2.5, nw=2.5, nh=1.7, ngap=0.62;
  nodes.forEach((nd,i)=>{
    const x = nx0 + i*(nw+ngap);
    rrect(s, { x, y:ny, w:nw, h:nh, fill:{color: CARD}, shadow: sh() });
    rect(s, { x, y:ny, w:nw, h:0.1, fill:{color: nd[2]} });
    s.addText(nd[0], { x:x+0.15, y:ny+0.22, w:nw-0.3, h:0.72, fontFace: HEAD, fontSize:16.5, bold:true, color: NAVY, align:"center", valign:"middle", margin:0 });
    s.addText(nd[1], { x:x+0.18, y:ny+0.95, w:nw-0.36, h:0.65, fontFace: BODY, fontSize:10.5, color: SLATE, align:"center", valign:"top", margin:0, lineSpacingMultiple:1.0 });
    if(i<nodes.length-1){
      s.addText("\u2192", { x:x+nw-0.02, y:ny, w:ngap+0.04, h:nh, fontFace: HEAD, fontSize:26, bold:true, color: SLATE, align:"center", valign:"middle", margin:0 });
    }
  });
  // "on device" bracket label
  rrect(s, { x:nx0, y:ny-0.55, w:(nw*3+ngap*3), h:0.42, fill:{color:"DDE9F7"} });
  s.addText("\uD83D\uDD12  ALL OF THIS RUNS ON THE DEVICE \u2014 NOTHING RAW LEAVES", { x:nx0, y:ny-0.55, w:(nw*3+ngap*3), h:0.42, fontFace: HEAD, fontSize:11.5, bold:true, color: NAVY, align:"center", valign:"middle", charSpacing:1, margin:0 });

  // fan-out consumers
  const cons = ["Microsoft Intune", "ServiceNow", "Surface Mgmt Portal", "Lakeside SysTrack (DEX)"];
  const bandY = ny+nh+0.5;
  s.addText("Only the de-identified zone flows downstream to:", { x:0.7, y:bandY-0.02, w:7.5, h:0.4, fontFace: BODY, fontSize:12.5, italic:true, color: SLATE, align:"left", valign:"middle", margin:0 });
  let ccx=0.7, ccy=bandY+0.45;
  cons.forEach(c=>{
    const w=0.4+c.length*0.115;
    rrect(s, { x:ccx, y:ccy, w, h:0.55, fill:{color: NAVY}, rectRadius:0.27 });
    s.addText(c, { x:ccx, y:ccy, w, h:0.55, fontFace: BODY, fontSize:12.5, bold:true, color:"E4EDFB", align:"center", valign:"middle", margin:0 });
    ccx += w + 0.28;
  });
  // reassurance callout
  rrect(s, { x:0.7, y:6.05, w:W-1.4, h:0.72, fill:{color:"E9F7EE"} });
  s.addText([
    { text:"Result:  ", options:{ fontFace: HEAD, fontSize:13.5, bold:true, color: GREEN } },
    { text:"HIPAA-aligned location intelligence with ", options:{ fontFace: BODY, fontSize:13.5, color: NAVY } },
    { text:"zero PHI sent to the cloud", options:{ fontFace: BODY, fontSize:13.5, bold:true, color: GREEN } },
    { text:" \u2014 and it keeps working offline, then reconciles on reconnect.", options:{ fontFace: BODY, fontSize:13.5, color: NAVY } },
  ], { x:0.9, y:6.05, w:W-1.8, h:0.72, align:"left", valign:"middle", margin:0 });
  footer(s, false);
})();

/* ============================ SLIDE 5 - IMPACT ============================ */
(function(){
  const s = p.addSlide(); bg(s, LIGHT);
  s.addText("What it\u2019s worth", { x:0.6, y:0.55, w:9, h:0.8, fontFace: HEAD, fontSize:34, bold:true, color: NAVY, align:"left", valign:"middle", margin:0 });
  s.addText("Illustrative framing at Zava Health scale \u2014 prototype figures, not a quote.", { x:0.62, y:1.4, w:10, h:0.45, fontFace: BODY, fontSize:14, italic:true, color: SLATE, align:"left", valign:"middle", margin:0 });

  const stats = [
    ["$3.1\u20134.4M", "per year in hardware spend avoided by reclaiming & redeploying", GREEN],
    ["~9,500", "underused endpoints flagged to repurpose", BLUE],
    ["0", "patient records (PHI) sent to the cloud \u2014 HIPAA-safe", TEAL],
    ["~4,200", "unknown-location endpoints made findable", AMBER],
  ];
  const n=4, m=0.6, gap=0.3, cw=(W-2*m-(n-1)*gap)/n, cy=2.1, ch=2.5;
  stats.forEach((st,i)=>{
    const x=m+i*(cw+gap);
    rrect(s, { x, y:cy, w:cw, h:ch, fill:{color: CARD}, shadow: sh() });
    rect(s, { x, y:cy, w:cw, h:0.12, fill:{color: st[2]} });
    s.addText(st[0], { x:x+0.2, y:cy+0.32, w:cw-0.32, h:0.9, fontFace: HEAD, fontSize:32, bold:true, color: st[2], align:"left", valign:"middle", margin:0 });
    s.addText(st[1], { x:x+0.22, y:cy+1.3, w:cw-0.42, h:1.05, fontFace: BODY, fontSize:12.5, color: NAVY, align:"left", valign:"top", margin:0, lineSpacingMultiple:1.02 });
  });

  // 8-forces top 3 strip
  s.addText("Why on-device wins here \u2014 top 3 of the 8 Forces of Local AI", { x:0.6, y:4.95, w:11.5, h:0.5, fontFace: HEAD, fontSize:17, bold:true, color: NAVY, align:"left", valign:"middle", margin:0 });
  const forces = [
    ["1  Privacy & Sovereignty", "Regulated PHI never leaves the device \u2014 no cloud honeypot.", "7C3AED"],
    ["2  Resilience", "Keeps working through RF dead zones & flaky WFH links.", BLUE],
    ["3  Latency", "Loss / theft caught the instant a device moves.", AMBER],
  ];
  const fm=0.6, fgap=0.3, fcw=(W-2*fm-2*fgap)/3, fy=5.5, fh=1.05;
  forces.forEach((f,i)=>{
    const x=fm+i*(fcw+fgap);
    rrect(s, { x, y:fy, w:fcw, h:fh, fill:{color:"FFFFFF"}, line:{color:"D8E1EE", type:"solid", width:1} });
    rect(s, { x, y:fy, w:0.12, h:fh, fill:{color: f[2]} });
    s.addText(f[0], { x:x+0.25, y:fy+0.12, w:fcw-0.4, h:0.4, fontFace: HEAD, fontSize:14.5, bold:true, color: f[2], align:"left", valign:"middle", margin:0 });
    s.addText(f[1], { x:x+0.27, y:fy+0.5, w:fcw-0.45, h:0.5, fontFace: BODY, fontSize:11.5, color: SLATE, align:"left", valign:"top", margin:0, lineSpacingMultiple:1.0 });
  });
  footer(s, false);
})();

/* ============================ SLIDE 6 - WHY NOW / ASK ============================ */
(function(){
  const s = p.addSlide(); bg(s, NAVY);
  circle(s, { x:-1.6, y:-1.6, w:4.6, h:4.6, fill:{ color: BLUE, transparency: 88 } });
  circle(s, { x:W-2.9, y:H-2.9, w:4.4, h:4.4, fill:{ color: TEAL, transparency: 88 } });
  protoPill(s, true);
  eyebrow(s, "WHY NOW", 0.6, 0.55, SKY);
  s.addText("The NPU is real today. The management layer that uses it isn\u2019t \u2014 yet.", { x:0.6, y:0.95, w:11.8, h:1.15, fontFace: HEAD, fontSize:30, bold:true, color:"FFFFFF", align:"left", valign:"middle", margin:0 });

  // two columns: the gap / the ask
  const colW=5.75, cy=2.55, chh=2.7;
  rrect(s, { x:0.6, y:cy, w:colW, h:chh, fill:{color: INK} });
  rect(s, { x:0.6, y:cy, w:0.12, h:chh, fill:{color: SKY} });
  s.addText("The gap", { x:0.85, y:cy+0.22, w:colW-0.5, h:0.5, fontFace: HEAD, fontSize:19, bold:true, color: SKY, align:"left", valign:"middle", margin:0 });
  s.addText([
    { text:"Copilot+ Surface devices ship with a capable NPU right now.\n", options:{ bullet:{code:"2022"}, color:"E4EDFB" } },
    { text:"Intune + DEX give inventory, compliance and health \u2014 but not real-time, private, physical location.\n", options:{ bullet:{code:"2022"}, color:"E4EDFB" } },
    { text:"Cloud-only tracking breaks in dead zones and raises PHI exposure.", options:{ bullet:{code:"2022"}, color:"E4EDFB" } },
  ], { x:0.9, y:cy+0.78, w:colW-0.55, h:chh-1.0, fontFace: BODY, fontSize:13.5, align:"left", valign:"top", margin:0, lineSpacingMultiple:1.05, paraSpaceAfter:6 });

  rrect(s, { x:0.6+colW+0.35, y:cy, w:colW, h:chh, fill:{color: INK} });
  rect(s, { x:0.6+colW+0.35, y:cy, w:0.12, h:chh, fill:{color: AMBER} });
  s.addText("The ask", { x:0.85+colW+0.35, y:cy+0.22, w:colW-0.5, h:0.5, fontFace: HEAD, fontSize:19, bold:true, color: AMBER, align:"left", valign:"middle", margin:0 });
  s.addText([
    { text:"Fund a scoped pilot: a Surface cohort across 3\u20134 Cedar Lake buildings + a WFH group.\n", options:{ bullet:{code:"2022"}, color:"E4EDFB" } },
    { text:"Wire the pilot into Intune, ServiceNow and Lakeside SysTrack.\n", options:{ bullet:{code:"2022"}, color:"E4EDFB" } },
    { text:"Measure devices located, tech hours saved and hardware reclaimed.", options:{ bullet:{code:"2022"}, color:"E4EDFB" } },
  ], { x:0.9+colW+0.35, y:cy+0.78, w:colW-0.55, h:chh-1.0, fontFace: BODY, fontSize:13.5, align:"left", valign:"top", margin:0, lineSpacingMultiple:1.05, paraSpaceAfter:6 });

  // close line
  rect(s, { x:0.6, y:5.75, w:0.14, h:0.85, fill:{color: AMBER} });
  s.addText("Let\u2019s build the layer that turns the Surface NPU into fleet awareness.", { x:0.9, y:5.72, w:11.4, h:0.9, fontFace: HEAD, fontSize:21, bold:true, color:"FFFFFF", align:"left", valign:"middle", margin:0 });
  footer(s, true);
})();

const out = "C:\\Users\\neilmisak\\Downloads\\Surface-Locus-Executive-Pitch.pptx";
p.writeFile({ fileName: out }).then(f=>console.log("wrote " + f)).catch(e=>{ console.error(e); process.exit(1); });
