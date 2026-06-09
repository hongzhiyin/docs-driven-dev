[CmdletBinding()]
param(
    [string]$Targets = $env:DOCDEV_INSTALL_TARGETS,
    [switch]$NoForce
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrEmpty($Targets)) {
    $Targets = "codex,cursor,agents,claude"
}

$UpdateScript = Join-Path $PSScriptRoot "update_cli.ps1"
if ($NoForce) {
    & $UpdateScript -Targets $Targets
} else {
    & $UpdateScript -Targets $Targets -Force
}
exit $LASTEXITCODE
