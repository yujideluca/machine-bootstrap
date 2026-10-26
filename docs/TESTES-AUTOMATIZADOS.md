# Automated bug-finding tests: project-template

Last reviewed: 715d6eb 2026-10-24
Created by the skill `gerar-teste-automatizado` (create mode).

## Analysis summary
The template is scaffolding: a requirements catalogue, a gate script, a traceability script, a CI workflow, a pre-push hook and the runner of the shared `pipeline-check`. It has no behaviour of its own except `tools/pipeline-check.sh --traceability` (43 lines, copied into every project). The program it used to carry now lives in `yujideluca/pipeline-check` with its own suite and record.

## Test matrix
No new tests were written. The example test (`tests/example_test.py`, tag `REQ XX-1`) keeps the traceability gate honest in a fresh project. The traceability script has no tests of its own.

## Results (observed, 2026-10-24)
`tools/pipeline-check.sh --mode local` passes on the template (gate, traceability over 1 requirement).

## Defects found
None in the scaffold. Finding: `check_traceability.py` is copied into six repositories and each copy has been edited (different test folders and extensions), the same duplication that was removed for `pipeline-check` (ADR-0003 there). Proposed debt P2: make it part of the shared program or its own tested script.

## Limitations and residual risks
The requirement-id pattern (`[A-Z]{2}-\d+`) allows only two-letter prefixes; a three-letter prefix is silently ignored.

## Recommendations
1. Move the traceability check into `pipeline-check` (config: test folders, extensions) and test it there.
2. Until then, copy new versions of the script deliberately and list the six copies in this file.
