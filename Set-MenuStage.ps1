param(
    [ValidateSet('Original','Font','Menu')][string]$Stage = 'Font',
    [switch]$Launch
)
$ErrorActionPreference = 'Stop'
if (Get-Process pun -ErrorAction SilentlyContinue) { throw 'Close the game before changing stages.' }
$gameRoot = Split-Path -Parent $PSScriptRoot
$testRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'work/game'))
$packRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot 'work/menu-stage'))
$manifest = Get-Content -LiteralPath (Join-Path $packRoot 'manifest.json') -Raw | ConvertFrom-Json
$operations = @()
foreach ($item in $manifest.components) {
    $relative = $item.archive
    $original = [IO.Path]::GetFullPath((Join-Path $gameRoot $relative))
    $target = [IO.Path]::GetFullPath((Join-Path $testRoot $relative))
    if (-not $original.StartsWith($gameRoot+'\',[StringComparison]::OrdinalIgnoreCase) -or
        -not $target.StartsWith($testRoot+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid archive path.' }
    if ((Get-FileHash -LiteralPath $original).Hash.ToLowerInvariant() -ne $item.source_sha256) { throw "Source mismatch: $relative" }
    $active = $Stage -eq 'Menu' -or ($Stage -eq 'Font' -and $item.component -eq 'interface-font')
    $source = if ($active) { [IO.Path]::GetFullPath((Join-Path $packRoot $item.file)) } else { $original }
    if ($active -and -not $source.StartsWith($packRoot+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Invalid component path.' }
    $expected = if ($active) { $item.output_sha256 } else { $item.source_sha256 }
    if ((Get-FileHash -LiteralPath $source).Hash.ToLowerInvariant() -ne $expected) { throw "Component mismatch: $relative" }
    $current = (Get-FileHash -LiteralPath $target).Hash.ToLowerInvariant()
    if ($current -notin @($item.source_sha256,$item.output_sha256)) { throw "Unknown test archive; restore the integrated pack first: $relative" }
    $operations += @{source=$source;target=$target;hash=$expected}
}
# Preserve the previous stage so a partial copy can be rolled back.
$backupRoot = Join-Path $packRoot ('rollback-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $backupRoot | Out-Null
for ($i=0; $i -lt $operations.Count; $i++) {
    Copy-Item -LiteralPath $operations[$i].target -Destination (Join-Path $backupRoot "$i.vpp")
}
try {
    foreach ($op in $operations) {
        Copy-Item -LiteralPath $op.source -Destination $op.target -Force
        if ((Get-FileHash -LiteralPath $op.target).Hash.ToLowerInvariant() -ne $op.hash) { throw 'Copy verification failed.' }
    }
} catch {
    for ($i=0; $i -lt $operations.Count; $i++) {
        Copy-Item -LiteralPath (Join-Path $backupRoot "$i.vpp") -Destination $operations[$i].target -Force
    }
    throw
}
@{stage=$Stage;in_game_verified=$false;updated_at=(Get-Date).ToString('o')} |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'reports/menu-stage-installed.json') -Encoding utf8
Write-Output "Active menu stage: $Stage. No video, HUD, or executable changes were applied."
if ($Launch) { Start-Process -FilePath (Join-Path $testRoot 'pun.exe') -WorkingDirectory $testRoot }
