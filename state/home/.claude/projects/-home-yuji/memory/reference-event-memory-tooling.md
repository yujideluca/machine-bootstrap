---
name: reference-event-memory-tooling
description: "Where the user-space tools for the event-memory work live (JDK 17, TLC, hypothesis/pytest) and how to invoke them"
metadata:
  node_type: memory
  type: reference
  originSessionId: dc7507fb-ff33-45b5-ba89-e8e995d6fa9b
  modified: 2026-10-16T05:44:13.381Z
---

Installed 2026-10-16 for the event-memory project (no sudo, nothing on PATH):
- JDK 17 (Temurin 17.0.20.1): `~/.local/opt/jdk-17/bin/java`. System java stays 1.8.
- TLC 1.7.4: `~/.local/opt/tla/tla2tools.jar`, run `~/.local/opt/jdk-17/bin/java -cp ~/.local/opt/tla/tla2tools.jar tlc2.TLC -config X.cfg X.tla`.
- hypothesis 6.170 and pytest 9.1 in `~/.local/share/claude-workflow/pylibs`; use `PYTHONPATH=<that dir> python3 -m pytest` (not with `python3 -I`, which ignores PYTHONPATH).
- `python3 -m venv` is broken (no ensurepip) and the `sqlite3` CLI is absent; Python's `sqlite3` module has FTS5.

Related: [[project-retired-workflow-pipeline]].

Added 2026-10-17 for the pyright-lsp / kotlin-lsp plugins (wrappers on PATH in ~/.local/bin):
- pyright 1.1.414: `pip --target ~/.local/share/pyright-pkg` (venv impossible); wrappers `pyright`, `pyright-langserver` set PYTHONPATH. Node is fetched by pyright itself.
- kotlin-lsp ILS-263.6379.0: `~/.local/opt/kotlin-lsp` (bundled JBR); wrapper `kotlin-lsp` execs `bin/intellij-server`. Upgrade = download the newer tar.gz from the Kotlin/kotlin-lsp release notes, verify the .sha256, unpack over it.
