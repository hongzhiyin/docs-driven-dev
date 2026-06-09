[CmdletBinding()]
param(
    [string]$Targets = "codex,cursor,agents,claude",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PathSeparator = [System.IO.Path]::PathSeparator
$OldPythonPath = $env:PYTHONPATH
if ([string]::IsNullOrEmpty($OldPythonPath)) {
    $env:PYTHONPATH = Join-Path $ProjectDir "src"
} else {
    $env:PYTHONPATH = (Join-Path $ProjectDir "src") + $PathSeparator + $OldPythonPath
}
$env:DOCDEV_PROJECT_DIR = $ProjectDir

& (Join-Path $PSScriptRoot "install_cli.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if (Test-Path (Join-Path $ProjectDir "tests")) {
    python -m unittest discover -s (Join-Path $ProjectDir "tests")
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

python -m docs_driven_dev.cli doctor
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$SyncArgs = @("sync-skill", "--targets", $Targets)
if ($Force) {
    $SyncArgs += "--force"
}
python -m docs_driven_dev.cli @SyncArgs
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m docs_driven_dev.cli doctor
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m docs_driven_dev.cli audit $ProjectDir
exit $LASTEXITCODE
