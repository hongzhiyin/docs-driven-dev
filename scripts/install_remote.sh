#!/usr/bin/env sh
set -eu

DEFAULT_REPO=${DOCDEV_RELEASE_REPO:-hongzhiyin/docs-driven-dev}
VERSION=${DOCDEV_VERSION:-latest}
RELEASE_BASE_URL=${DOCDEV_RELEASE_BASE_URL:-}
INSTALL_ROOT=${DOCDEV_INSTALL_ROOT:-"$HOME/.local/share/docdev"}
BIN_DIR=${DOCDEV_BIN_DIR:-"$HOME/.local/bin"}
LOG_PREFIX=${DOCDEV_INSTALL_LOG_PREFIX:-"[docdev install]"}
SYNC_SKILL=0

usage() {
  cat <<'EOF'
Usage: scripts/install_remote.sh [options]

Options:
  --version VERSION          Install a specific version. Default: latest
  --release-base-url URL     Base URL or file:// directory containing manifest.json
  --install-root DIR         Install root. Default: ~/.local/share/docdev
  --bin-dir DIR              Launcher directory. Default: ~/.local/bin
  --sync-skill               Run docdev sync-skill after install

Environment:
  DOCDEV_RELEASE_REPO        GitHub repo, owner/name. Default: hongzhiyin/docs-driven-dev
  DOCDEV_RELEASE_BASE_URL    Override asset base URL
  DOCDEV_INSTALL_ROOT        Override install root
  DOCDEV_BIN_DIR             Override launcher directory
  GITHUB_TOKEN               Optional token for private GitHub release downloads
EOF
}

log() {
  printf '%s %s\n' "$LOG_PREFIX" "$*"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --version)
      VERSION=${2:?missing value for --version}
      shift 2
      ;;
    --release-base-url)
      RELEASE_BASE_URL=${2:?missing value for --release-base-url}
      shift 2
      ;;
    --install-root)
      INSTALL_ROOT=${2:?missing value for --install-root}
      shift 2
      ;;
    --bin-dir)
      BIN_DIR=${2:?missing value for --bin-dir}
      shift 2
      ;;
    --sync-skill)
      SYNC_SKILL=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'install_remote: unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [ -z "$RELEASE_BASE_URL" ]; then
  if [ "$VERSION" = "latest" ]; then
    RELEASE_BASE_URL="https://github.com/$DEFAULT_REPO/releases/latest/download"
  else
    RELEASE_BASE_URL="https://github.com/$DEFAULT_REPO/releases/download/v$VERSION"
  fi
fi

asset_url() {
  base=${RELEASE_BASE_URL%/}
  printf '%s/%s\n' "$base" "$1"
}

download() {
  url=$1
  dest=$2
  case "$url" in
    file://*)
      source_path=${url#file://}
      cp "$source_path" "$dest"
      ;;
    http://*|https://*)
      if ! command -v curl >/dev/null 2>&1; then
        printf 'install_remote: curl is required for %s\n' "$url" >&2
        exit 1
      fi
      if [ -n "${GITHUB_TOKEN:-}" ]; then
        curl --retry 3 --retry-delay 1 --retry-all-errors --connect-timeout 20 -fsSL -H "Authorization: Bearer $GITHUB_TOKEN" "$url" -o "$dest"
      else
        curl --retry 3 --retry-delay 1 --retry-all-errors --connect-timeout 20 -fsSL "$url" -o "$dest"
      fi
      ;;
    *)
      cp "$url" "$dest"
      ;;
  esac
}

sha256_file() {
  path=$1
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$path" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$path" | awk '{print $1}'
  else
    printf 'install_remote: need shasum or sha256sum\n' >&2
    exit 1
  fi
}

TMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/docdev-install.XXXXXX")
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT INT TERM

MANIFEST="$TMP_DIR/manifest.json"
log "download manifest: $(asset_url manifest.json)"
download "$(asset_url manifest.json)" "$MANIFEST"

MANIFEST_DATA=$(python3 - "$MANIFEST" <<'PY'
import json
import pathlib
import sys

payload = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
for key in ("version", "artifact", "sha256"):
    if not payload.get(key):
        raise SystemExit(f"manifest missing {key}")
print(payload["version"])
print(payload["artifact"])
print(payload["sha256"])
PY
)
MANIFEST_VERSION=$(printf '%s\n' "$MANIFEST_DATA" | sed -n '1p')
ARTIFACT=$(printf '%s\n' "$MANIFEST_DATA" | sed -n '2p')
EXPECTED_SHA256=$(printf '%s\n' "$MANIFEST_DATA" | sed -n '3p')

if [ "$VERSION" != "latest" ] && [ "$VERSION" != "$MANIFEST_VERSION" ]; then
  printf 'install_remote: requested version %s but manifest is %s\n' "$VERSION" "$MANIFEST_VERSION" >&2
  exit 1
fi

ARTIFACT_PATH="$TMP_DIR/$ARTIFACT"
log "download artifact: $(asset_url "$ARTIFACT")"
download "$(asset_url "$ARTIFACT")" "$ARTIFACT_PATH"

ACTUAL_SHA256=$(sha256_file "$ARTIFACT_PATH")
if [ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]; then
  printf 'install_remote: checksum mismatch for %s\nexpected: %s\nactual:   %s\n' "$ARTIFACT" "$EXPECTED_SHA256" "$ACTUAL_SHA256" >&2
  exit 1
fi
log "checksum ok: $ARTIFACT"

RELEASES_DIR="$INSTALL_ROOT/releases"
TARGET_DIR="$RELEASES_DIR/$MANIFEST_VERSION"
TMP_RELEASE="$RELEASES_DIR/.tmp-$MANIFEST_VERSION-$$"
mkdir -p "$RELEASES_DIR" "$BIN_DIR"
rm -rf "$TMP_RELEASE"
mkdir -p "$TMP_RELEASE"
tar -xzf "$ARTIFACT_PATH" -C "$TMP_RELEASE" --strip-components 1

if [ ! -d "$TMP_RELEASE/src/docs_driven_dev" ] || [ ! -f "$TMP_RELEASE/skill/SKILL.md" ]; then
  printf 'install_remote: artifact does not look like a docs-driven-dev release\n' >&2
  exit 1
fi

rm -rf "$TARGET_DIR"
mv "$TMP_RELEASE" "$TARGET_DIR"

CURRENT="$INSTALL_ROOT/current"
rm -rf "$CURRENT"
ln -s "$TARGET_DIR" "$CURRENT"

LAUNCHER="$BIN_DIR/docdev"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env sh
DOCDEV_PROJECT_DIR="$CURRENT" PYTHONPATH="$CURRENT/src\${PYTHONPATH:+:\$PYTHONPATH}" exec python3 -m docs_driven_dev.cli "\$@"
EOF
chmod +x "$LAUNCHER"

log "installed version $MANIFEST_VERSION at $TARGET_DIR"
log "launcher: $LAUNCHER"

"$LAUNCHER" doctor

case ":${PATH:-}:" in
  *":$BIN_DIR:"*) ;;
  *) log "warning: $BIN_DIR is not on PATH; run $LAUNCHER directly or add it manually" ;;
esac

if [ "$SYNC_SKILL" -eq 1 ]; then
  "$LAUNCHER" sync-skill --targets codex,cursor,agents,claude --force
fi
