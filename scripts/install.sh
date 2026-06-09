#!/usr/bin/env sh
set -eu

usage() {
  echo "Usage: $0 [--targets codex,cursor,agents,claude] [--no-force]" >&2
}

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TARGETS=${DOCDEV_INSTALL_TARGETS:-codex,cursor,agents,claude}
FORCE=1

log() {
  printf '[docdev install] %s\n' "$*"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --targets)
      if [ $# -lt 2 ]; then
        usage
        exit 2
      fi
      TARGETS=$2
      shift 2
      ;;
    --targets=*)
      TARGETS=${1#--targets=}
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --no-force)
      FORCE=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

log "start: targets=$TARGETS force=$FORCE"
if [ "$FORCE" -eq 1 ]; then
  log "delegate: $PROJECT_DIR/scripts/update_cli.sh --targets $TARGETS --force"
  "$PROJECT_DIR/scripts/update_cli.sh" --targets "$TARGETS" --force
else
  log "delegate: $PROJECT_DIR/scripts/update_cli.sh --targets $TARGETS"
  "$PROJECT_DIR/scripts/update_cli.sh" --targets "$TARGETS"
fi
log "done"
