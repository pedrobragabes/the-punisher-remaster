param([switch]$Restore,[switch]$Launch,[switch]$AllowUnvalidated)
$ErrorActionPreference='Stop'
if (-not $Restore -and -not $AllowUnvalidated) {
    throw 'The integrated pack has a known startup failure. Use -AllowUnvalidated only for controlled diagnostics. See docs/STATUS.md.'
}
$labRoot=[IO.Path]::GetFullPath($PSScriptRoot)
$gameRoot=Split-Path -Parent $labRoot
$testRoot=Join-Path $labRoot 'work\game'
if (Get-Process pun -ErrorAction SilentlyContinue) { throw 'Close the game before applying the UI pack.' }
$ui=Get-Content -LiteralPath (Join-Path $labRoot 'reports\ui-pack-manifest.json') -Raw | ConvertFrom-Json
$video=Get-Content -LiteralPath (Join-Path $labRoot 'reports\ui-video-manifest.json') -Raw | ConvertFrom-Json
if (-not $video.complete) { throw 'Video conversion has not finished.' }
$items=@($ui.packages)+@($video.videos)
$exeManifest=Get-Content -LiteralPath (Join-Path $labRoot 'reports\ui-exe-manifest.json') -Raw | ConvertFrom-Json
$items+=@($exeManifest)
$operations=@()
# Validate every path and hash before copying any files.
foreach ($item in $items) {
    $relative=$item.archive.Replace('/','\')
    $original=[IO.Path]::GetFullPath((Join-Path $gameRoot $relative))
    $target=[IO.Path]::GetFullPath((Join-Path $testRoot $relative))
    if (-not $original.StartsWith($gameRoot+'\',[StringComparison]::OrdinalIgnoreCase) -or -not $target.StartsWith($testRoot+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Path is outside the expected directory.' }
    if ((Get-FileHash -LiteralPath $original -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.source_sha256) { throw "Source file changed: $relative" }
    $source=if ($Restore) { $original } else { Join-Path (Join-Path $labRoot 'work\ui-pack') $relative }
    $expected=if ($Restore) { $item.source_sha256 } else { $item.output_sha256 }
    if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) { throw "Invalid package: $relative" }
    $operations+=@{source=$source;target=$target;hash=$expected}
}
foreach ($op in $operations) {
    Copy-Item -LiteralPath $op.source -Destination $op.target -Force
    if ((Get-FileHash -LiteralPath $op.target -Algorithm SHA256).Hash.ToLowerInvariant() -ne $op.hash) { throw "Copy verification failed: $($op.target)" }
}
$state=@{installed=(-not $Restore);files=$operations.Count;verified_at=(Get-Date).ToString('o');in_game_verified=$false}
$state | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $labRoot 'reports\ui-installed.json') -Encoding utf8
Write-Output "Interface: $($operations.Count) files copied and verified in the test copy."
if ($Launch) { Start-Process -FilePath (Join-Path $testRoot 'pun.exe') -WorkingDirectory $testRoot }
