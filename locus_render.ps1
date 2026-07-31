# locus_render.ps1 — render each slide of the deck to PNG via PowerPoint COM (visual QA)
$ErrorActionPreference = "Stop"
$dir = $PSScriptRoot
$pptx = Join-Path $dir "locus_onepager.pptx"
$out = Join-Path $dir "render"
if (Test-Path $out) { Remove-Item $out -Recurse -Force }
New-Item -ItemType Directory -Path $out | Out-Null

$pp = New-Object -ComObject PowerPoint.Application
try {
    $pres = $pp.Presentations.Open($pptx, $true, $false, $false)   # ReadOnly, Untitled, WithWindow=false
    foreach ($sl in $pres.Slides) {
        $n = "{0:d2}" -f $sl.SlideIndex
        $sl.Export((Join-Path $out "slide-$n.png"), "PNG", 1600, 900)
    }
    $slideCount = $pres.Slides.Count
    $pres.Close()
    "OK: exported $slideCount slides -> $out"
} finally {
    $pp.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp) | Out-Null
}
Get-ChildItem $out | Select-Object Name, Length
