[CmdletBinding()]
param(
    [string]$Targets = "codex,cursor,agents,claude",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-DocdevUpdateLog {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[docdev update][$Timestamp] $Message"
}

function Invoke-DocdevNativeStep {
    param(
        [int]$Number,
        [int]$Total,
        [string]$Name,
        [scriptblock]$Command
    )

    Write-DocdevUpdateLog "step $Number/$Total start: $Name"
    try {
        & $Command
    } catch {
        Write-DocdevUpdateLog "step $Number/$Total failed: $Name"
        Write-DocdevUpdateLog "error: $($_.Exception.Message)"
        exit 1
    }
    $ExitCode = if ($null -eq $LASTEXITCODE) { 0 } else { $LASTEXITCODE }
    if ($ExitCode -ne 0) {
        Write-DocdevUpdateLog "step $Number/$Total failed with exit code ${ExitCode}: $Name"
        exit $ExitCode
    }
    Write-DocdevUpdateLog "step $Number/$Total done: $Name"
}

function Invoke-DocdevPowerShellStep {
    param(
        [int]$Number,
        [int]$Total,
        [string]$Name,
        [scriptblock]$Command
    )

    Write-DocdevUpdateLog "step $Number/$Total start: $Name"
    try {
        & $Command
    } catch {
        Write-DocdevUpdateLog "step $Number/$Total failed: $Name"
        Write-DocdevUpdateLog "error: $($_.Exception.Message)"
        exit 1
    }
    if (-not $?) {
        Write-DocdevUpdateLog "step $Number/$Total failed: $Name"
        exit 1
    }
    Write-DocdevUpdateLog "step $Number/$Total done: $Name"
}

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$PathSeparator = [System.IO.Path]::PathSeparator
$OldPythonPath = $env:PYTHONPATH
if ([string]::IsNullOrEmpty($OldPythonPath)) {
    $env:PYTHONPATH = Join-Path $ProjectDir "src"
} else {
    $env:PYTHONPATH = (Join-Path $ProjectDir "src") + $PathSeparator + $OldPythonPath
}
$env:DOCDEV_PROJECT_DIR = $ProjectDir

Write-DocdevUpdateLog "start: project=$ProjectDir targets=$Targets force=$Force"
Invoke-DocdevPowerShellStep 1 7 "install local CLI wrapper" {
    & (Join-Path $PSScriptRoot "install_cli.ps1")
}

if (Test-Path (Join-Path $ProjectDir "tests")) {
    Invoke-DocdevNativeStep 2 7 "run unit tests" {
        python -m unittest discover -s (Join-Path $ProjectDir "tests")
    }
} else {
    Write-DocdevUpdateLog "step 2/7 skipped: tests directory missing"
}

Invoke-DocdevNativeStep 3 7 "doctor before sync" {
    python -m docs_driven_dev.cli doctor
}

$SyncArgs = @("sync-skill", "--targets", $Targets)
if ($Force) {
    $SyncArgs += "--force"
}
Write-DocdevUpdateLog "sync args: $($SyncArgs -join ' ')"
Invoke-DocdevNativeStep 4 7 "sync skill targets" {
    python -m docs_driven_dev.cli @SyncArgs
}

Invoke-DocdevNativeStep 5 7 "doctor after sync" {
    python -m docs_driven_dev.cli doctor
}

Invoke-DocdevNativeStep 6 7 "audit source checkout" {
    python -m docs_driven_dev.cli audit $ProjectDir
}

Invoke-DocdevNativeStep 7 7 "status source checkout" {
    python -m docs_driven_dev.cli status $ProjectDir
}

Write-DocdevUpdateLog "done"
exit 0
