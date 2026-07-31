# locus_demo_check.ps1 — pre-flight readiness check for the Copilot+ Surface
# Locus prototype. Run this right before a live demo. Prints READY (green)
# or NOT READY (red) with the failing checks.
#
#   ./locus_demo_check.ps1            # checks http://127.0.0.1:5075
#   ./locus_demo_check.ps1 -Base http://127.0.0.1:5075

param([string]$Base = "http://127.0.0.1:5075")

$ErrorActionPreference = "Stop"
$fail = @()

function Check([string]$name, [scriptblock]$test) {
    try {
        & $test | Out-Null
        Write-Host ("  [PASS] " + $name) -ForegroundColor Green
    } catch {
        $script:fail += $name
        Write-Host ("  [FAIL] " + $name + "  ->  " + $_.Exception.Message) -ForegroundColor Red
    }
}

function Assert([bool]$cond, [string]$msg) {
    if (-not $cond) { throw $msg }
}

function Ask([string]$q) {
    $body = @{ query = $q } | ConvertTo-Json -Compress
    return (Invoke-WebRequest -Method Post -Uri "$Base/api/ask" -ContentType "application/json" `
            -Body $body -TimeoutSec 40 -UseBasicParsing).Content
}

Write-Host ""
Write-Host "Surface Locus - pre-flight check @ $Base" -ForegroundColor Cyan
Write-Host "(PROTOTYPE / mock data)" -ForegroundColor DarkGray
Write-Host ""

# 0. server reachable?
try {
    Invoke-WebRequest -Uri "$Base/api/status" -TimeoutSec 6 -UseBasicParsing | Out-Null
} catch {
    Write-Host "  [FAIL] server not reachable at $Base" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Start it first:  python locus_app.py" -ForegroundColor Yellow
    Write-Host "NOT READY" -ForegroundColor Red
    exit 1
}

# 1. engine status
$status = Invoke-RestMethod "$Base/api/status" -TimeoutSec 6
$live = [bool]$status.live
$mode = if ($status.loading) { "warming NPU..." } elseif ($live) { "LIVE on $($status.device) ($($status.model))" } else { "MOCK fallback" }
Write-Host ("  [INFO] on-device engine: " + $mode) -ForegroundColor Cyan

# 2. static endpoints
Check "index page (200, non-trivial)" {
    $r = Invoke-WebRequest "$Base/" -TimeoutSec 8 -UseBasicParsing
    Assert ($r.StatusCode -eq 200) "status $($r.StatusCode)"
    Assert ($r.Content.Length -gt 5000) "index too small"
}
Check "/api/fleet (18 devices, Zava Health campus + 123k scale)" {
    $f = Invoke-RestMethod "$Base/api/fleet" -TimeoutSec 8
    Assert ($f.summary.total -eq 18) "total=$($f.summary.total)"
    Assert ($f.devices.Count -eq 18) "devices=$($f.devices.Count)"
    Assert ($f.campus.lake.label -eq "Cedar Lake") "lake=$($f.campus.lake.label)"
    Assert ($f.scale.total_endpoints -eq 123000) "scale=$($f.scale.total_endpoints)"
}
Check "/api/ladder (3 tiers)" {
    $l = Invoke-RestMethod "$Base/api/ladder" -TimeoutSec 8
    Assert ($l.tiers.Count -eq 3) "tiers=$($l.tiers.Count)"
    Assert ($l.dimensions.Count -eq $l.tiers[0].rows.Count) "dimension/row mismatch"
}
Check "/api/blade (kpis + alerts)" {
    $b = Invoke-RestMethod "$Base/api/blade" -TimeoutSec 8
    Assert ($b.kpis.Count -ge 4) "kpis=$($b.kpis.Count)"
    Assert ($b.alerts.Count -ge 1) "alerts=$($b.alerts.Count)"
}
Check "/api/surface (Surface Mgmt Portal: kpis + inventory + insights)" {
    $s = Invoke-RestMethod "$Base/api/surface" -TimeoutSec 8
    Assert ($s.breadcrumb[0] -eq "Microsoft Surface Management Portal") "breadcrumb=$($s.breadcrumb[0])"
    Assert ($s.kpis.Count -ge 4) "kpis=$($s.kpis.Count)"
    Assert ($s.devices.Count -ge 4) "devices=$($s.devices.Count)"
    Assert ($s.insights.Count -ge 3) "insights=$($s.insights.Count)"
}
Check "/api/forces (8 forces)" {
    $x = Invoke-RestMethod "$Base/api/forces" -TimeoutSec 8
    Assert ($x.forces.Count -eq 8) "forces=$($x.forces.Count)"
    Assert ($x.top_three.Count -eq 3) "top_three=$($x.top_three.Count)"
}
Check "/api/benefits (>=6)" {
    $b = Invoke-RestMethod "$Base/api/benefits" -TimeoutSec 8
    Assert ($b.Count -ge 6) "benefits=$($b.Count)"
}
Check "/api/predict (3 devices w/ candidates)" {
    $p = Invoke-RestMethod "$Base/api/predict" -TimeoutSec 8
    $keys = @($p.PSObject.Properties.Name)
    Assert ($keys.Count -ge 3) "predict keys=$($keys.Count)"
    Assert ($p.'INT-3302'.candidates.Count -ge 3) "INT-3302 candidates missing"
}
Check "/api/redact (POST strips PII)" {
    $body = @{ text = "Patient Maria Delgado (MRN 00447162) seen by Dr. A. Rivera, call 407-555-0148" } | ConvertTo-Json -Compress
    $r = Invoke-RestMethod -Method Post -Uri "$Base/api/redact" -ContentType "application/json" -Body $body -TimeoutSec 8
    Assert ($r.removed_count -ge 3) "removed=$($r.removed_count)"
    Assert ($r.redacted -notmatch "Maria Delgado") "name leaked"
    Assert ($r.redacted -match "\[MRN\]") "MRN not tokenized"
}
Check "/api/servicenow (4 tickets, before->after)" {
    $s = Invoke-RestMethod "$Base/api/servicenow" -TimeoutSec 8
    Assert ($s.tickets.Count -ge 4) "tickets=$($s.tickets.Count)"
    Assert ($null -ne $s.tickets[0].loc_after) "no resolved location"
}
Check "/api/utilization (underused candidates + savings)" {
    $u = Invoke-RestMethod "$Base/api/utilization" -TimeoutSec 8
    Assert ($u.candidates.Count -ge 1) "candidates=$($u.candidates.Count)"
    Assert ($u.summary.fleet_underused_est -gt 0) "no fleet estimate"
}

# 3. the demo presets stream + route correctly (mock path also asserts the routed header)
$presets = @(
    @{ q = "Which devices left a lakeside building after 18:00?";                  needle = "On-device fleet answer" },
    @{ q = "Where is the missing Coding-Tab-08 most likely right now?";            needle = "Predicted location" },
    @{ q = "What leaves the device after redaction for a coding tablet?";          needle = "PII redaction" },
    @{ q = "Which underused devices can we reclaim, and where are they?";          needle = "Underused hardware" },
    @{ q = "Summarize the missing Coding-Tab-08 incident and recommend next steps."; needle = "Incident Summary" },
    @{ q = "Triage my highest-risk WFH laptops right now.";                        needle = "risk triage" }
)
foreach ($p in $presets) {
    Check ("preset streams: '" + $p.q.Substring(0, [Math]::Min(38, $p.q.Length)) + "...'") {
        $ans = Ask $p.q
        Assert ($ans.Length -gt 60) "empty/short answer"
        if (-not $live) { Assert ($ans -match [regex]::Escape($p.needle)) "routing: missing '$($p.needle)'" }
    }
}

Write-Host ""
if ($fail.Count -eq 0) {
    Write-Host "READY - all checks passed. Open $Base and full-screen the Fleet Map tab." -ForegroundColor Green
    if (-not $live) { Write-Host "(engine is in MOCK mode - that's fine for the demo; start Foundry Local for the live NPU path.)" -ForegroundColor DarkGray }
    exit 0
} else {
    Write-Host ("NOT READY - " + $fail.Count + " check(s) failed: " + ($fail -join ", ")) -ForegroundColor Red
    exit 1
}
