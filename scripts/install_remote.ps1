param(
    [string]$Version = $(if ($env:DOCDEV_VERSION) { $env:DOCDEV_VERSION } else { "latest" }),
    [string]$ReleaseBaseUrl = $env:DOCDEV_RELEASE_BASE_URL,
    [string]$InstallRoot = $(if ($env:DOCDEV_INSTALL_ROOT) { $env:DOCDEV_INSTALL_ROOT } else { Join-Path $HOME ".local\share\docdev" }),
    [string]$BinDir = $(if ($env:DOCDEV_BIN_DIR) { $env:DOCDEV_BIN_DIR } else { Join-Path $HOME ".local\bin" }),
    [switch]$SyncSkill,
    [switch]$NoSyncSkill
)

$ErrorActionPreference = "Stop"
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
    @"
`$env:DOCDEV_PROJECT_DIR = '$Current'
`$env:PYTHONPATH = '$Current\src'
python -m docs_driven_dev.cli @args
exit `$LASTEXITCODE
"@ | Set-Content -Encoding UTF8 -Path $Launcher

    Write-DocdevInstallLog "installed version $($Manifest.version) at $TargetDir"
    Write-DocdevInstallLog "launcher: $Launcher"
    & $Launcher doctor
    if (-not $NoSyncSkill) {
        & $Launcher sync-skill --targets codex,cursor,agents,claude --force
    }
} finally {
    if (Test-Path $TempDir) {
        Remove-Item -Recurse -Force $TempDir
    }
}
