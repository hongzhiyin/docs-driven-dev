[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$BinDir = Join-Path $ProjectDir ".venv\Scripts"
$PsBin = Join-Path $BinDir "docdev.ps1"
$CmdBin = Join-Path $BinDir "docdev.cmd"

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

$EscapedProjectDir = $ProjectDir.Replace("'", "''")
$PsContent = @"
`$ErrorActionPreference = 'Stop'
`$env:DOCDEV_PROJECT_DIR = '$EscapedProjectDir'
`$env:PYTHONPATH = '$EscapedProjectDir/src'
python -m docs_driven_dev.cli @args
exit `$LASTEXITCODE
"@
Set-Content -Path $PsBin -Value $PsContent -Encoding UTF8

$CmdContent = @"
@echo off
set "DOCDEV_PROJECT_DIR=$ProjectDir"
set "PYTHONPATH=$ProjectDir/src"
python -m docs_driven_dev.cli %*
"@
Set-Content -Path $CmdBin -Value $CmdContent -Encoding ASCII

Write-Host "Installed docdev PowerShell wrapper at $PsBin"
Write-Host "Installed docdev CMD wrapper at $CmdBin"
Write-Host "Try: $PsBin doctor"
