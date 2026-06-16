param(
    [string]$Version = $(if ($env:DOCDEV_VERSION) { $env:DOCDEV_VERSION } else { "latest" }),
    [string]$ReleaseBaseUrl = $env:DOCDEV_RELEASE_BASE_URL,
    [string]$InstallRoot = $(if ($env:DOCDEV_INSTALL_ROOT) { $env:DOCDEV_INSTALL_ROOT } else { Join-Path $HOME ".local\share\docdev" }),
    [string]$BinDir = $(if ($env:DOCDEV_BIN_DIR) { $env:DOCDEV_BIN_DIR } else { Join-Path $HOME ".local\bin" }),
    [switch]$SyncSkill,
    [switch]$NoSyncSkill,
    [switch]$NoModifyPath
)

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

$Repo = if ($env:DOCDEV_RELEASE_REPO) { $env:DOCDEV_RELEASE_REPO } else { "hongzhiyin/docs-driven-dev" }
$LogPrefix = if ($env:DOCDEV_INSTALL_LOG_PREFIX) { $env:DOCDEV_INSTALL_LOG_PREFIX } else { "[docdev install]" }
if (-not $ReleaseBaseUrl) {
    if ($Version -eq "latest") {
        $ReleaseBaseUrl = "https://github.com/$Repo/releases/latest/download"
    } else {
        $ReleaseBaseUrl = "https://github.com/$Repo/releases/download/v$Version"
    }
}

function Write-DocdevInstallLog {
    param([string]$Message)
    Write-Host "$LogPrefix $Message"
}

function Join-AssetUrl {
    param([string]$Name)
    return ($ReleaseBaseUrl.TrimEnd("/") + "/" + $Name)
}

function Receive-DocdevAsset {
    param([string]$Url, [string]$Destination)
    if ($Url.StartsWith("file://")) {
        Copy-Item -LiteralPath $Url.Substring(7) -Destination $Destination -Force
    } elseif ($Url.StartsWith("http://") -or $Url.StartsWith("https://")) {
        $Headers = @{}
        if ($env:GITHUB_TOKEN) {
            $Headers["Authorization"] = "Bearer $env:GITHUB_TOKEN"
        }
        Invoke-WebRequest -Uri $Url -OutFile $Destination -Headers $Headers
    } else {
        Copy-Item -LiteralPath $Url -Destination $Destination -Force
    }
}

function Normalize-DocdevPathEntry {
    param([string]$Value)
    if ([string]::IsNullOrWhiteSpace($Value)) {
        return ""
    }
    $Expanded = [Environment]::ExpandEnvironmentVariables($Value.Trim().Trim('"'))
    if ([string]::IsNullOrWhiteSpace($Expanded)) {
        return ""
    }
    try {
        return ([System.IO.Path]::GetFullPath($Expanded)).TrimEnd([char[]]("\\/"))
    } catch {
        return $Expanded.TrimEnd([char[]]("\\/"))
    }
}

function Test-DocdevPathContains {
    param([string]$PathValue, [string]$Entry)
    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return $false
    }
    $Needle = Normalize-DocdevPathEntry $Entry
    if (-not $Needle) {
        return $false
    }
    foreach ($Item in ($PathValue -split [System.IO.Path]::PathSeparator)) {
        if ((Normalize-DocdevPathEntry $Item).Equals($Needle, [System.StringComparison]::OrdinalIgnoreCase)) {
            return $true
        }
    }
    return $false
}

function Add-DocdevPathEntry {
    param([string]$PathValue, [string]$Entry)
    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return $Entry
    }
    return $PathValue.TrimEnd([System.IO.Path]::PathSeparator) + [System.IO.Path]::PathSeparator + $Entry
}

function Enable-DocdevCommandOnPath {
    param([string]$Directory)
    $ResolvedDir = [System.IO.Path]::GetFullPath($Directory)
    $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if (-not (Test-DocdevPathContains -PathValue $UserPath -Entry $ResolvedDir)) {
        [Environment]::SetEnvironmentVariable("Path", (Add-DocdevPathEntry -PathValue $UserPath -Entry $ResolvedDir), "User")
        $UpdatedUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
        if (Test-DocdevPathContains -PathValue $UpdatedUserPath -Entry $ResolvedDir) {
            Write-DocdevInstallLog "added to user PATH: $ResolvedDir"
        } else {
            Write-DocdevInstallLog "warning: attempted to add to user PATH but could not verify persistence: $ResolvedDir"
        }
    } else {
        Write-DocdevInstallLog "user PATH already contains: $ResolvedDir"
    }

    if (-not (Test-DocdevPathContains -PathValue $env:Path -Entry $ResolvedDir)) {
        $env:Path = Add-DocdevPathEntry -PathValue $env:Path -Entry $ResolvedDir
        if (Test-DocdevPathContains -PathValue $env:Path -Entry $ResolvedDir) {
            Write-DocdevInstallLog "added to current process PATH: $ResolvedDir"
        } else {
            Write-DocdevInstallLog "warning: attempted to add to current process PATH but could not verify it: $ResolvedDir"
        }
    }
}

$TempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("docdev-install-" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $TempDir | Out-Null
try {
    $ManifestPath = Join-Path $TempDir "manifest.json"
    Write-DocdevInstallLog "download manifest: $(Join-AssetUrl 'manifest.json')"
    Receive-DocdevAsset -Url (Join-AssetUrl "manifest.json") -Destination $ManifestPath
    $Manifest = Get-Content -Raw -Path $ManifestPath | ConvertFrom-Json
    if (-not $Manifest.version -or -not $Manifest.artifact -or -not $Manifest.sha256) {
        throw "manifest missing version, artifact, or sha256"
    }
    if ($Version -ne "latest" -and $Version -ne $Manifest.version) {
        throw "requested version $Version but manifest is $($Manifest.version)"
    }

    $ArtifactPath = Join-Path $TempDir $Manifest.artifact
    Write-DocdevInstallLog "download artifact: $(Join-AssetUrl $Manifest.artifact)"
    Receive-DocdevAsset -Url (Join-AssetUrl $Manifest.artifact) -Destination $ArtifactPath
    $ActualHash = (Get-FileHash -Algorithm SHA256 -Path $ArtifactPath).Hash.ToLowerInvariant()
    if ($ActualHash -ne $Manifest.sha256.ToLowerInvariant()) {
        throw "checksum mismatch for $($Manifest.artifact)"
    }

    $ReleasesDir = Join-Path $InstallRoot "releases"
    $TargetDir = Join-Path $ReleasesDir $Manifest.version
    $TmpRelease = Join-Path $ReleasesDir (".tmp-" + $Manifest.version + "-" + $PID)
    New-Item -ItemType Directory -Force -Path $ReleasesDir, $BinDir, $TmpRelease | Out-Null
    tar -xzf $ArtifactPath -C $TmpRelease --strip-components 1
    if (-not (Test-Path (Join-Path $TmpRelease "src\docs_driven_dev")) -or -not (Test-Path (Join-Path $TmpRelease "skill\SKILL.md"))) {
        throw "artifact does not look like a docs-driven-dev release"
    }
    if (Test-Path $TargetDir) {
        Remove-Item -Recurse -Force $TargetDir
    }
    Move-Item -Path $TmpRelease -Destination $TargetDir

    $Current = Join-Path $InstallRoot "current"
    if (Test-Path $Current) {
        Remove-Item -Recurse -Force $Current
    }
    New-Item -ItemType Junction -Path $Current -Target $TargetDir | Out-Null

    $Launcher = Join-Path $BinDir "docdev.ps1"
    $CmdLauncher = Join-Path $BinDir "docdev.cmd"
    $EscapedCurrent = $Current.Replace("'", "''")
    $EscapedSrc = (Join-Path $Current "src").Replace("'", "''")
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
    @"
$PowerShellUtf8Prelude
`$env:DOCDEV_PROJECT_DIR = '$EscapedCurrent'
`$env:PYTHONPATH = '$EscapedSrc'
python -m docs_driven_dev.cli @args
exit `$LASTEXITCODE
"@ | Set-Content -Encoding UTF8 -Path $Launcher
    $CmdCurrent = $Current.Replace("%", "%%")
    $CmdSrc = (Join-Path $Current "src").Replace("%", "%%")
    @"
@echo off
chcp 65001 >nul
set "PYTHONUTF8=1"
set "PYTHONIOENCODING=utf-8"
set "DOCDEV_PROJECT_DIR=$CmdCurrent"
set "PYTHONPATH=$CmdSrc"
python -m docs_driven_dev.cli %*
"@ | Set-Content -Encoding ASCII -Path $CmdLauncher

    Write-DocdevInstallLog "installed version $($Manifest.version) at $TargetDir"
    Write-DocdevInstallLog "launcher: $Launcher"
    Write-DocdevInstallLog "command: $CmdLauncher"
    if (-not $NoModifyPath) {
        Enable-DocdevCommandOnPath -Directory $BinDir
    } else {
        Write-DocdevInstallLog "skipped PATH update because -NoModifyPath was set"
    }
    & $Launcher doctor
    if (-not $NoSyncSkill) {
        & $Launcher sync-skill --targets "codex,cursor,agents,claude" --force
    }
} finally {
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
    }
}
