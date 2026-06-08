#!/usr/bin/env sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

"$PROJECT_DIR/scripts/install_cli.sh"

if [ -d "$PROJECT_DIR/tests" ]; then
  PYTHONPATH="$PROJECT_DIR/src${PYTHONPATH:+:$PYTHONPATH}" \
    python3 -m unittest discover -s "$PROJECT_DIR/tests"
fi

"$PROJECT_DIR/scripts/check_install.sh"
"$PROJECT_DIR/scripts/sync_skill.sh" "$@"
"$PROJECT_DIR/scripts/check_install.sh"
