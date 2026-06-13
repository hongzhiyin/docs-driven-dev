#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: $0 <project> [docdev init options]" >&2
  echo "Example: $0 /path/to/project --write-config" >&2
}

if [ $# -lt 1 ]; then
  usage
  exit 2
fi

PROJECT=$1
shift

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
DOCDEV="$PROJECT_DIR/.venv/bin/docdev"
DOCS_DIR=""

for arg in "$@"; do
  case "$arg" in
    --docs-dir=*)
      DOCS_DIR=${arg#--docs-dir=}
      ;;
  esac
done

prev=""
for arg in "$@"; do
  if [ "$prev" = "--docs-dir" ]; then
    DOCS_DIR=$arg
    break
  fi
  prev=$arg
done

"$PROJECT_DIR/scripts/install_cli.sh"
sh "$DOCDEV" doctor
sh "$DOCDEV" init "$PROJECT" "$@"

if [ -n "$DOCS_DIR" ]; then
  sh "$DOCDEV" audit "$PROJECT" --docs-dir "$DOCS_DIR" --write-report
else
  sh "$DOCDEV" audit "$PROJECT" --write-report
fi
