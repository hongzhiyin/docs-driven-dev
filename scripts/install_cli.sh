#!/usr/bin/env sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
BIN_DIR="$PROJECT_DIR/.venv/bin"
BIN="$BIN_DIR/docdev"

mkdir -p "$BIN_DIR"
cat > "$BIN" <<EOF
#!/usr/bin/env sh
DOCDEV_PROJECT_DIR="$PROJECT_DIR" PYTHONPATH="$PROJECT_DIR/src" exec python3 -m docs_driven_dev.cli "\$@"
EOF
chmod +x "$BIN"

echo "Installed docdev wrapper at $BIN"
echo "Try: $BIN doctor"
