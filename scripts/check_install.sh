#!/usr/bin/env sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

DOCDEV_PROJECT_DIR="$PROJECT_DIR" PYTHONPATH="$PROJECT_DIR/src" \
  python3 -m docs_driven_dev.cli doctor

DOCDEV_PROJECT_DIR="$PROJECT_DIR" PYTHONPATH="$PROJECT_DIR/src" \
  python3 -m docs_driven_dev.cli audit "$PROJECT_DIR"
