[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

function Set-DocdevUtf8Console {
    $Utf8NoBom = New-Object System.Text.UTF8Encoding -ArgumentList $false
    $script:OutputEncoding = $Utf8NoBom
    $env:PYTHONUTF8 = "1"
    $env:PYTHONIOENCODING = "utf-8"
    try {
        [Console]::InputEncoding = $Utf8NoBom
        [Console]::OutputEncoding = $Utf8NoBom
    } catch {
        # Some non-interactive hosts do not expose mutable console encoding.
    }
}

Set-DocdevUtf8Console

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$SrcDir = Join-Path $ProjectDir "src"
$BinDir = Join-Path $ProjectDir ".venv\Scripts"
$PsBin = Join-Path $BinDir "docdev.ps1"
$CmdBin = Join-Path $BinDir "docdev.cmd"

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

$EscapedProjectDir = $ProjectDir.Replace("'", "''")
$PowerShellUtf8Prelude = @'
$ErrorActionPreference = 'Stop'
$Utf8NoBom = New-Object System.Text.UTF8Encoding -ArgumentList $false
$OutputEncoding = $Utf8NoBom
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
try {
    [Console]::InputEncoding = $Utf8NoBom
    [Console]::OutputEncoding = $Utf8NoBom
} catch {
}
'@
$PsContent = @"
$PowerShellUtf8Prelude
`$env:DOCDEV_PROJECT_DIR = '$EscapedProjectDir'
`$env:PYTHONPATH = '$($SrcDir.Replace("'", "''"))'
python -m docs_driven_dev.cli @args
exit `$LASTEXITCODE
"@
Set-Content -Path $PsBin -Value $PsContent -Encoding UTF8

$CmdContent = @"
@echo off
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "DOCDEV_PROJECT_DIR=$ProjectDir"
set "PYTHONPATH=$SrcDir"
python -m docs_driven_dev.cli %*
"@
Set-Content -Path $CmdBin -Value $CmdContent -Encoding ASCII

Write-Host "Installed docdev PowerShell wrapper at $PsBin"
Write-Host "Installed docdev CMD wrapper at $CmdBin"
Write-Host "Try: $PsBin doctor"
