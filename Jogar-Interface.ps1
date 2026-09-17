param([switch]$AllowUnvalidated)
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'Install-UI.ps1') -Launch -AllowUnvalidated:$AllowUnvalidated
