# ADR-0002: Write the tool in Python (standard library only) with a small Bash starter

- **Status:** accepted
- **Date:** 2026-10-25
- **Type (ISO/IEC/IEEE 14764):** initial
- **Decided by:** Giovanni (language choice, 2026-10-25: "python + bash")

## Context

The tool must run on a computer that has just been installed, before anything of Giovanni's exists on it. A fresh
Ubuntu has `bash` and `python3`, but no `pip` packages, no Rust, no Node.

## Decision

- `bootstrap.sh` (Bash) only installs the few programs the tool itself needs (`git`, `python3`, `rclone`, `rsync`,
  `gnupg`, `curl`) and starts `python3 -m mb restore`.
- Everything else is Python using **only the standard library** (no `pip install`), so there is nothing to install
  first and nothing that can disappear from a package index.
- Tests use `unittest` (also standard library).

## Alternatives considered

- **All Bash** — fine for ten lines, but the plan/dry-run/idempotence logic needs real data structures and tests.
- **Ansible or Nix** — powerful, but a large new thing to learn and to keep working, and it needs installing first.
- **Rust** — would need a toolchain on the machine that is being rebuilt.

## Consequences

Slightly more code written by hand. In return: one `git clone` and one command on a bare system. A fitness check
(`max_file_lines`) keeps modules small; `tests/` must never touch the real system (a runner is always injected).
