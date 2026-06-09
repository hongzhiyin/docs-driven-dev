[CmdletBinding()]
param(
    [string]$Targets = $env:DOCDEV_INSTALL_TARGETS,
    [switch]$NoForce
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrEmpty($Targets)) {
    $Targets = "codex,cursor,agents,claude"
}

$Args = @("-Targets", $Targets)
if (-not $NoForce) {
    $Args += "-Force"
}

& (Join-Path $PSScriptRoot "update_cli.ps1") @Args
exit $LASTEXITCODE
