[CmdletBinding()]
param(
    [string]$Targets = $env:DOCDEV_INSTALL_TARGETS,
    [switch]$NoForce
)

$ErrorActionPreference = "Stop"

function Write-DocdevInstallLog {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[docdev install][$Timestamp] $Message"
}

if ([string]::IsNullOrEmpty($Targets)) {
    $Targets = "codex,cursor,agents,claude"
}

$UpdateScript = Join-Path $PSScriptRoot "update_cli.ps1"
Write-DocdevInstallLog "start: targets=$Targets force=$(-not $NoForce)"
Write-DocdevInstallLog "delegate: $UpdateScript"
if ($NoForce) {
    & $UpdateScript -Targets $Targets
} else {
    & $UpdateScript -Targets $Targets -Force
}
$ExitCode = if ($null -eq $LASTEXITCODE) { 0 } else { $LASTEXITCODE }
if ($ExitCode -ne 0) {
    Write-DocdevInstallLog "failed: update lifecycle exited with code $ExitCode"
    exit $ExitCode
}
Write-DocdevInstallLog "done"
exit 0
