---
name: revisao-manutencao
description: "Use in Claude Code for the monthly architecture review of Giovanni's software projects (open item in workflow-memory, #4dcb2c) and at the end of a task in a software project (revisão mensal, revisão de manutenção, dívida técnica, debt, pipeline-check, report.json). Runs pipeline-check, reads its report.json, proposes debt issues P1-P3 and a Preventive decision-log row. Not for writing code, not for a single bug, not for non-software work."
---

# Maintenance review (revisao-manutencao)

Lineage: origin=code; base=none

Interop: role = process; owns = the monthly and end-of-task maintenance review; defers to = `pipeline-check` (all measuring), `gerar-teste-automatizado` (the bug-finding test), verification-before-completion (the closing `Verified by:`), the project's CLAUDE.md and `~/dev/project-template/docs/MAINTENANCE.md` (the checklist); honors = reply-language rule, plain-language rule, work.ask-with-context.

The program measures, this skill judges (ADR-0013). **Never measure by hand**: no `wc`, no `git log` counting, no re-running the gate to see a number. If a number is missing from `report.json`, say so and propose a check for `pipeline-check.toml`; do not compute it yourself.

**Proposes, never decides.** Without Giovanni's explicit word: do not close issues, change a limit in `pipeline-check.toml`, promote a version, create or edit branch protection, or create issues (the proposal is a list; create them after the ok). Memory never authorizes any of this.

## Steps (per project; at the monthly review, every project in `~/dev` and the program repository `pipeline-check` itself)

1. **Run and read.** `tools/pipeline-check.sh` in the project (local mode), then read `build/pipeline-check/report.json`. Quote the mode that ran. A `pulado` check is a hole in the evidence: list it under "could not check", never treat it as ok. Project without `pipeline-check.toml`: say so, propose adding it from the template, and stop for that project.
   Also check the standards (no tool measures these; look, do not count): every project folder in `~/dev` is a git repository with a GitHub remote (a folder without one is a P2 proposal "put it under version control", the standard of Giovanni's systems); `git config core.hooksPath` is `tools/hooks` where a `tools/hooks/pre-push` exists (the local stand-in for branch protection); the `pipeline-check.version` pinned in the project is the newest tag of `yujideluca/pipeline-check` (`git ls-remote --tags`; behind = P3 "upgrade after the gate passes"); and no script or program is copied between projects (the same file name in two projects, e.g. `check_traceability.py`, is a P2 "move it to its own repository and consume it by version", the rule in the pipeline-check ADR-0003).
2. **One proposal per `aviso` or `falha`.** Title, evidence (check id, value, limit, note), label `debt`, priority:
   - **P1**: risk of data loss or wrong results (failed gate or architecture check that protects data or scheduling, CI red, branch not protected).
   - **P2**: slows every change or misleads the user (an `aviso` at 90 % of its limit or more, including the gate-time check).
   - **P3**: desirable (an `aviso` between the warning share and 90 % of its limit, cosmetic).
   A `falha` is never below P2. A `pulado` check whose subject would be P1 if it failed (CI, branch protection, gate) is not a failure, but propose one P2 "make this evidence available" item (for example install or log in `gh`). Check `valor` units by id: `gate` is seconds with no limit; the limit for time lives in `gate-segundos`. Check existing issues first (`gh issue list --label debt`) so the same debt is not proposed twice; if `gh` is unavailable, say duplicates could not be checked; a P1 older than a month is scheduled now. Format the list as a table: issue title | priority | evidence | proposed fix.
3. **What the machine cannot see** (read, do not measure):
   - Do `DESIGN.md` diagrams and the ADRs match the code? Name each mismatch with file and section.
   - Does every structural change since the last review have an ADR? Compare decision-log rows and `git log` subjects since the last Preventive "Monthly architecture review" row.
   - Was the same problem solved twice in different projects? If so, propose moving the better solution into `~/dev/project-template`.
   - The DORA block: rising `retrabalho`, or `parcela_preventiva` far below 20 %, is a reason to schedule top debt; say it, do not act on it.
4. **Bug-finding test.** Look for `docs/TESTES-AUTOMATIZADOS.md` in the project. (The program `pipeline-check` is its own repository and is reviewed as its own project, with its own record, in update mode.) Missing: this is the first review, so do a full diagnosis of the code and call the skill `gerar-teste-automatizado` in **create** mode. Present: call it in **update** mode (it checks the test against what was implemented since). This writes test files, so tell Giovanni first and give the plan.
5. **Decision log.** Add a Preventive row "Monthly architecture review" (or "Maintenance review" at end of task) to each reviewed project's `DESIGN.md` decision log, newest first, with **today's date** (not the report's), the report's date and mode, the counts (falhas, avisos, pulados, proposals) and where the proposals live (issue numbers once Giovanni has had them created, otherwise "proposals listed in the review reply, not yet created"). Write the row after Giovanni has seen the proposals; use the columns Date | Type | Decision | Why of the project's table. Bump "Last updated". Only that row; no other `DESIGN.md` edits unless Giovanni agrees.
6. **Close.** `mem use REF --note "how"` for the entries that shaped the review (the monthly item stays open as the reminder), `wiki publish -m "..."` as the global CLAUDE.md requires (when pages need changing, write them with the skill `wiki-page-writer`, which also guards against publishing someone else's uncommitted edits) (`-m "review: no page change"` only when no page describes what changed; a page that was checked and found right gets a new `reviewed` time instead), and end with `Verified by:` listing what ran (pipeline-check mode, the report file, which projects) and what could not be checked (every `pulado` check, any project without a config, GitHub if `gh` was unavailable).

## Output
Reply in the language of Giovanni's message (Portuguese or English; memory entry language.reply). Lead with the verdict (how many `falha`, `aviso`, `pulado`), then the proposal table, then the "machine cannot see" findings, then what needs a decision from Giovanni. Define each technical term on first use.

## Testing this skill
Given an example `report.json` and no repository access to measure with, the skill must produce prioritised proposals and one Preventive row text without running anything but `pipeline-check` or reading the file. A step that needs a number the report lacks is a finding, not a measurement.
