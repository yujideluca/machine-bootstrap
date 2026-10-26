#!/usr/bin/env bash
# Quality gate: the one definition of "passing". Releases run it; CI runs it on every push.
# Fill in the steps for this project; keep each one a command that exits non-zero on failure.
set -euo pipefail
cd "$(dirname "$0")/.."
MAX_GATE_SECONDS=1200   # fitness function: a slow gate gets skipped; speed up or split tests instead
SECONDS=0
step() { printf '\n== %s\n' "$1"; }

step "1 build and tests"
python3 -m unittest discover -s tests -t .
shellcheck bootstrap.sh
python3 -m mb scan

step "2 requirement traceability"
tools/pipeline-check.sh --traceability
git diff --quiet -- docs/TRACEABILITY.md || { echo "docs/TRACEABILITY.md changed: commit the regenerated matrix"; exit 1; }

step "3 fitness functions (limits in pipeline-check.toml)"
tools/pipeline-check.sh --measure-only

[ "$SECONDS" -le "$MAX_GATE_SECONDS" ] || { echo "FAIL gate took ${SECONDS}s (> ${MAX_GATE_SECONDS}s)"; exit 1; }
printf '\nquality gate passed (%ss)\n' "$SECONDS"
