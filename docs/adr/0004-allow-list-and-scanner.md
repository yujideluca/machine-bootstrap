# ADR-0004: Capture by allow-list, and refuse anything the secret scanner flags

- **Status:** accepted
- **Date:** 2026-10-25
- **Type (ISO/IEC/IEEE 14764):** initial
- **Decided by:** Giovanni ("should be taken very seriously"); design proposed by Claude Code

## Context

The record of the machine (`state/`) is meant to live in a git repository. A home folder holds keys, tokens and
logins next to harmless settings, and new files appear all the time. A rule of the form "copy everything except
the secrets" fails the first time a new secret file has a name nobody thought of.

## Decision

1. `mb.toml` lists exactly which files and folders may be captured. Everything else is never read.
2. Each candidate file is scanned (private-key blocks, known token shapes, literal `password = value`
   assignments); a flagged file is refused and reported by name, never by content.
3. The quality gate scans `state/` again, so a secret that reaches `state/` by any other route fails the build.
4. Secrets travel only through `secrets-backup` (ADR-0005), encrypted.

## Alternatives considered

- **Deny-list** — breaks silently, see above.
- **Back up the whole home with a generic tool** — also copies caches, browser data and tokens into one place.

## Consequences

A new setting is not captured until someone adds it to `mb.toml` (visible in `mb status` as nothing, so the
monthly review should skim `~/.config` for new files). The scanner may flag a harmless file; that is the safe side
of the error, and the pattern can be tightened with a test (it was, once, for documentation text).
