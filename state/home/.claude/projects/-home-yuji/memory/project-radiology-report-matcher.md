---
name: project-radiology-report-matcher
description: "Giovanni's planned radiology report-to-diagnosis website (Radiopaedia-derived word mapping); decisions made so far"
metadata:
  node_type: memory
  type: project
  originSessionId: 79cd197b-f528-4665-bccc-3072c6008fa4
  modified: 2026-10-27T19:03:41.394Z
---

Idea (2026-10-27): website where a user types a radiology report (exam, technique, patient data, history); it matches the wording to likely diagnoses, article links and structured scores (TI-RADS, BI-RADS...). Radiopaedia text is the stepping stone.

Decisions: possibly commercial later (Radiopaedia is CC BY-NC-SA, so the product should not depend on its text); reports in EN, DE and PT-BR; runs on a cheap desktop bought for this, several simultaneous users, no GPU; first version covers one narrow area; no patient data stored (processed in memory, no accounts); Claude and Codex write the code, Giovanni reviews; plan saved as an offline static HTML site in ~/Documents with flowcharts and architecture diagrams.

Matching method is undecided: Codex research report is in the scratchpad `codex-research/report.md` (session 79cd197b); read it before choosing.

**Why:** keeps the plan consistent across sessions.
**How to apply:** build the plan site from these decisions; do not re-ask them.

## Status 2026-10-27 (end of first work session)
- Code: ~/dev/radiology-crawler (crawl.py, translate.py, run_all.sh, site_src/build.py). Data in its data/ folder (SQLite + raw gz pages + reference book txt).
- Full crawl started in background (articles first, then cases, ~10 days at 10 s/page); resume with ./run_all.sh. Translation loop: `python3 -I translate.py loop --daily-cap 400`; stop file data/STOP_TRANSLATION.
- Plan site: ~/Documents/Radiology Report Matcher/ (rebuild: python3 -I ~/dev/radiology-crawler/site_src/build.py); add LOG entries there as work progresses.
- Radiopaedia has no DE/PT content. Portuguese reference book is only 44 pages (chest). Downloads/pdf.pdf is Giovanni's personal lab report: never use it.
- Giovanni asked to keep each Codex context under 250k tokens (each call is --ephemeral, prompts ~6k tokens, hard check in translate.py).
- Decided 2026-10-28: no daily translation cap; translate at the same rate as extraction. Running as 4 workers (`translate.py loop --worker I/4`, worker 0 with --extract, no --daily-cap); keeps pace with the crawl (2721 extracted = 2721 translated).

## Decision 2026-11-01: one model set per language
Every identification model (tagger, filters, wording layer, versions 1-4) is built, tuned and scored separately for EN, DE and PT-BR on that language's corpus (DE/PT = Codex translations). Runtime: fast language check first, then route to that language's models; the routing pipeline is designed only after all per-language models are tested. Encoded in ~/dev/radiology-crawler: CLAUDE.md principle 12, DESIGN.md log, docs/modelling-directives.md, status steps L1/L2. Replaces the older "statistics on English only, DE/PT through translations" line.
