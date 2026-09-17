param(
    [ValidateSet('Original','Remastered')][string]$Mode = 'Remastered',
    [ValidateSet('Original','Briefing')][string]$Layout = 'Original'
)
$ErrorActionPreference = 'Stop'
$labRoot = $PSScriptRoot
$gameRoot = Split-Path -Parent $labRoot
$testRoot = Join-Path $labRoot 'work\game'
$testExe = Join-Path $testRoot 'pun.exe'
if (-not (Test-Path -LiteralPath $testExe)) { throw 'A copia de teste ainda nao existe.' }
$running = Get-Process pun -ErrorAction SilentlyContinue
if ($running) { throw 'Feche The Punisher antes de alternar a variante de teste.' }
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
        throw "Arquivo original mudou: $relative"
    }
    $source = if ($Mode -eq 'Original') { $original } else { Join-Path (Join-Path $labRoot 'work\packages') $relative }
    $expectedHash = if ($Mode -eq 'Original') { $item.source_sha256 } else { $item.output_sha256 }
    if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedHash) {
        throw "Pacote nao corresponde ao manifesto: $relative"
    }
    $destination = [IO.Path]::GetFullPath((Join-Path $testRoot $relative))
    if (-not $destination.StartsWith($testRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Destino fora da copia de teste.'
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
        throw 'O arquivo original de tabelas mudou.'
    }
    $useBriefing = $Mode -eq 'Remastered' -and $Layout -eq 'Briefing'
    $layoutSource = if ($useBriefing) { Join-Path (Join-Path $labRoot 'work\briefing-packages') $layoutRelative } else { $layoutOriginal }
    $layoutHash = if ($useBriefing) { $layoutManifest.output_sha256 } else { $layoutManifest.source_sha256 }
    if ((Get-FileHash -LiteralPath $layoutSource -Algorithm SHA256).Hash.ToLowerInvariant() -ne $layoutHash) {
        throw 'Pacote de briefing nao corresponde ao manifesto.'
    }
    $layoutDestination = [IO.Path]::GetFullPath((Join-Path $testRoot $layoutRelative))
    if (-not $layoutDestination.StartsWith($testRoot + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Destino de layout fora da copia de teste.'
    }
    Copy-Item -LiteralPath $layoutSource -Destination $layoutDestination -Force
} elseif ($Layout -eq 'Briefing') {
    throw 'Execute tools/build_briefing.py antes de usar este layout.'
}
Start-Process -FilePath $testExe -WorkingDirectory $testRoot
