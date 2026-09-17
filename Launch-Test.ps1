param(
    [ValidateSet('Original','Remastered')][string]$Mode = 'Remastered',
    [ValidateSet('Original','Briefing')][string]$Layout = 'Original'
)
$ErrorActionPreference = 'Stop'
$labRoot = $PSScriptRoot
$gameRoot = Split-Path -Parent $labRoot
$testRoot = Join-Path $labRoot 'work\game'
$testExe = Join-Path $testRoot 'pun.exe'
if (-not (Test-Path -LiteralPath $testExe)) { throw 'The test copy does not exist yet.' }
$running = Get-Process pun -ErrorAction SilentlyContinue
if ($running) { throw 'Close The Punisher before switching test variants.' }
# A full UI installation must not be silently overwritten by the old prototype.
$uiStatePath = Join-Path $labRoot 'reports\ui-installed.json'
if (Test-Path -LiteralPath $uiStatePath) {
    $uiState = Get-Content -LiteralPath $uiStatePath -Raw | ConvertFrom-Json
    if ($uiState.installed) {
        if ($Mode -eq 'Original') {
            & (Join-Path $labRoot 'Install-UI.ps1') -Restore
        } else {
            Start-Process -FilePath $testExe -WorkingDirectory $testRoot
            return
        }
    }
}
$manifest = Get-Content -LiteralPath (Join-Path $labRoot 'reports\poc-manifest.json') -Raw | ConvertFrom-Json
foreach ($item in $manifest) {
    $relative = $item.archive.Replace('/', '\')
    $original = Join-Path $gameRoot $relative
    if ((Get-FileHash -LiteralPath $original -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.source_sha256) {
        throw "Source file changed: $relative"
    }
    $source = if ($Mode -eq 'Original') { $original } else { Join-Path (Join-Path $labRoot 'work\packages') $relative }
    $expectedHash = if ($Mode -eq 'Original') { $item.source_sha256 } else { $item.output_sha256 }
    if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) {
        throw "Package does not match its manifest: $relative"
    }
    $destination = [IO.Path]::GetFullPath((Join-Path $testRoot $relative))
    if (-not $destination.StartsWith($testRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Destination is outside the test copy.'
    }
    Copy-Item -LiteralPath $source -Destination $destination -Force
}
# Always restore the original table when the layout experiment is disabled.
$layoutManifestPath = Join-Path $labRoot 'reports\briefing-manifest.json'
if (Test-Path -LiteralPath $layoutManifestPath) {
    $layoutManifest = Get-Content -LiteralPath $layoutManifestPath -Raw | ConvertFrom-Json
    $layoutRelative = $layoutManifest.archive.Replace('/', '\')
    $layoutOriginal = Join-Path $gameRoot $layoutRelative
    if ((Get-FileHash -LiteralPath $layoutOriginal -Algorithm SHA256).Hash.ToLowerInvariant() -ne $layoutManifest.source_sha256) {
        throw 'The original table archive has changed.'
    }
    $useBriefing = $Mode -eq 'Remastered' -and $Layout -eq 'Briefing'
    $layoutSource = if ($useBriefing) { Join-Path (Join-Path $labRoot 'work\briefing-packages') $layoutRelative } else { $layoutOriginal }
    $layoutHash = if ($useBriefing) { $layoutManifest.output_sha256 } else { $layoutManifest.source_sha256 }
    if ((Get-FileHash -LiteralPath $layoutSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne $layoutHash) {
        throw 'Briefing package does not match its manifest.'
    }
    $layoutDestination = [IO.Path]::GetFullPath((Join-Path $testRoot $layoutRelative))
    if (-not $layoutDestination.StartsWith($testRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Layout destination is outside the test copy.'
    }
    Copy-Item -LiteralPath $layoutSource -Destination $layoutDestination -Force
} elseif ($Layout -eq 'Briefing') {
    throw 'Run tools/build_briefing.py before using this layout.'
}
Start-Process -FilePath $testExe -WorkingDirectory $testRoot
