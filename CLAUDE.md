# machine-bootstrap: working notes for Claude Code

Records how Giovanni's laptop (Acer Nitro, Kubuntu, X11, Nvidia) is set up and rebuilds it on a fresh install or another
computer (`bootstrap.sh`, `python3 -m mb ...`). Runs on a bare system, so Python standard library only. Giovanni called it
"the bridge to another setup": treat a wrong restore, a leaked secret or an untested recipe as serious.

## Principles (each one is checked by something)

1. **Requirement, then test, then code**: a behaviour Giovanni states becomes a row in `docs/REQUIREMENTS.md`, then a
   test tagged `REQ <ID>`, then code. Checked by `tools/pipeline-check.sh --traceability` in the gate.
2. **Planning is pure, the system is touched in one place**: `build_plan` only reads (through `Facts`); only `execute` with a
   runner changes anything, and the runner is a required argument. Checked by the tests (they pass a runner that fails the test).
3. **Nothing secret in git**: capture is an allow-list (`mb.toml`) plus a scanner; the gate runs `python3 -m mb scan` over
   `state/`. Secrets only go through `secrets-backup` (encrypted). Never print a secret's value, only its kind.
4. **The gate decides**: `tools/quality_gate.sh` is the only definition of passing; CI runs it through `tools/pipeline-check`
   on every push (limits in `pipeline-check.toml`; a `falha` fails the build; ADR-0003).
5. **Unit tests prove logic, only the VM proves a restore**: after changing a recipe, `plan.py` or `bootstrap.sh`, run
   `tools/vm-test.sh` (about an hour, background) and record the result in the decision log (MB-15).
6. **A tool used by more than one project lives once, in its own repository, and is consumed by pinned version, never copied** (example: `pipeline-check`).
7. **Decisions are written where the code is**: decision-log row with its Type in `DESIGN.md`, an ADR for structural ones.

## Working rules

- Build and test: `tools/quality_gate.sh`; the full measurement is `tools/pipeline-check.sh`. After pushing, the CI run must be green.
- Tests never run real commands, never read the real home: use `FakeFacts` and temp dirs. `mb capture` writes `state/`; commit it
  only after `mb scan` is clean and the diff looks right.
- Never run `secrets-backup` with a passphrase of your own: only Giovanni types it. Never read `~/.ssh`, `~/.gnupg` or the secrets paths.
- Do not touch the SSD's existing folders; `data-backup` writes only under `machine-bootstrap/` there.
- Monthly review and end of a task: run the skill `revisao-manutencao` (reads `report.json`, proposes `debt` issues; it never closes issues or changes limits).
- After coding anything, do a first-line debug pass before reporting done: build, tests, run the changed flow for real.
- Keep `DESIGN.md` current in the same commit as any design change: decision-log row (newest first, with Type:
  Corrective, Adaptive, Perfective, Preventive), fix stale sections, bump "Last updated". A structural change (module,
  dependency direction, release flow, storage format, a rule with real alternatives) also gets an ADR.
- Technical debt (`docs/MAINTENANCE.md`): a limitation found while working becomes a GitHub Issue labelled `debt` with a
  priority in the same session. About one session in five goes to debt or prevention: when the last four sessions were
  all features, say so and propose the top `debt` issue; Giovanni decides.
- At the end of every task, update this project's pages in the wiki (`~/dev/wiki`, `wiki publish`), then `mem use`.
- Never force-push. Ask Giovanni before anything outward-facing or destructive.
