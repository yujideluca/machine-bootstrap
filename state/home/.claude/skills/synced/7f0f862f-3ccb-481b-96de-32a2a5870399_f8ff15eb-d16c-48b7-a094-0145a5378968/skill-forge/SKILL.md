---
name: "skill-forge"
description: "Full skill pipeline for Giovanni: three competing versions, tests, compatibility checks with his other skills, then validation and packaging through skill-creator. Use when he asks to create, rebuild, optimize or forge a skill, turn a rule or workflow into a new skill, or wants tested or compared versions. For small changes to one skill (fix a line, rename, change the description, add an example) or just packaging a skill file, skill-creator alone is enough."
---

# Skill Forge (knowledge engineering / design science)

Philosophy: a skill is codified expert knowledge. Understand the domain and the user deeply, design an explicit architecture, then evaluate the artifact against requirements (build -> evaluate -> refine, as in design-science research).

## 0. Mode (pick before anything else)
| Request | Mode |
|---|---|
| New skill, rebuild, "optimize", "forge", "test/compare versions", a change that alters triggers or interop with other skills | **Full pipeline:** steps 1-6 here, then skill-creator for validation and packaging (step 6) |
| Small edit to one skill (a line, an example, wording, rename), "just write it", packaging an existing SKILL.md | **skill-creator only**, unchanged; then the compatibility mini-check: re-read the interop header and run 4c steps 3 and 6 only if the edit touches triggers, format or cross-references |
His explicit wording wins ("full forge" or "quick" decides). If unsure, state the assumed mode in one line and proceed.

## 1. Requirements analysis
- Purpose, user, trigger situations, inputs, outputs, failure modes that matter most (rank by cost of error).
- Existing assets: the user's saved preferences, memory notes, other skills that overlap (avoid duplicates; decide what belongs in settings vs skill).
- Domain knowledge: the expert procedure as a step list; the decisions in it; the facts or tables it needs.

## 2. Architecture
Choose the structure from the knowledge type:
- procedure with fragile steps -> exact steps or script;
- judgment -> decision table or ordered checklist;
- reference knowledge -> compact lookup table;
- style/format -> template plus one example.
Write a short design note: modules, order, what is in SKILL.md vs references.

## 3. Three versions
- **V1, V2:** two different design philosophies relevant to this problem (state each and why it fits).
- **V3:** literature review of the domain and of skill/prompt design; write the evidence-based version, including any mathematical or algorithmic optimization of its logic (ordering of checks, short-circuiting, lookup structures, minimal token use).

## 4. Two evaluations
- **Self-built:** a scenario set covering the requirements and the ranked failure modes, scored with a rubric (correctness, adherence to steps, output format, token cost).
- **Pre-existing:** find through research a published benchmark or standard checklist that fits the purpose; apply it unchanged.

## 4b. Unreproducible results (gap resolution)
When an output disagrees with an expected answer, label, verifier or the user's own example and you cannot explain why, do not record it as a "known gap" yet:
1. **Pin the gap:** state exactly what differs (your value vs expected, which case, which step) and list 2-3 hypotheses for the missing information (a definition, filter, convention, data source, version, or an error in the reference).
2. **Ask for complementary explanations:** ask the user targeted questions with AskUserQuestion, one round, at most 3 questions, offering your hypotheses as options (e.g. "Is 'stock' meant to exclude ADRs and class B shares?"; "Where did the expected value come from?"; "Which guideline or version defines this?"). Ask only what the user can plausibly know; never ask him to do the research for you.
3. **Research in parallel:** while waiting, search for the source of the expected answer (reference code, dataset documentation, guideline text, benchmark repository) and try to reproduce it.
4. **Resolve:** encode the explanation that reproduces the result, labelled with its source ("per user", "per <doc, year>", or "reproduces a quirk/bug in <reference>"). If the user's explanation conflicts with the evidence, show both and let him decide.
5. **If still unresolved** (or the session is unattended): keep the most defensible behavior, flag the gap explicitly in the skill and the report, and list the open question for him.

## 4c. Compatibility layer (run on the winning version, before delivery)
Goal: a new or changed skill must not collide with his other skills, settings or scheduled tasks, and every affected skill gets an update proposal.

1. **Inventory.** Read the project's `claude/skill-registry.md` (create it if missing). Then read every one of his skills in full (synced skills folder, or the skill list), his saved preferences/settings rules, and scheduled tasks that invoke a skill (list_triggers). Also read work that is not live yet: open requests in the repo's STATUS.md and both logbooks, skills staged under `docs/` in claude-workflow-backup, and the instructions of the claude.ai Project the skill targets (backed up under `docs/<project>/`). A pending skill or a project instruction set counts as existing: extend it instead of building a parallel one.
2. **Interop header.** Give the new skill one line under its title: `Interop: role = domain | cross-cutting; owns = <format / workflow / facts>; defers to = <skills>; honors = language rule, flags !! *** ...`. Domain skills own the format of their answers; cross-cutting skills (e.g. bias-risk-triage, browser-automacao-segura) only set minimums or safety rules and never dictate format.
3. **Conflict matrix.** Compare the new skill against each overlapping skill on these axes and record any clash:
   - trigger overlap (would both load for the same prompt?);
   - reply language and document language;
   - depth flags `!!` `***` `...` and answer length;
   - output format and structure;
   - evidence/sourcing depth and date-checking;
   - tools and environment (built-in browser vs Claude in Chrome, connectors, file locations);
   - safety and destructive actions;
   - cross-references (skills named inside other skills must exist with the exact name);
   - duplication of always-on rules that belong in settings.
4. **Resolve by precedence, not by copying rules:** domain skill > cross-cutting skill for format; stricter rule wins for safety and sourcing; the user's explicit flag or message beats any skill default. Write the precedence line into whichever skill needs it.
5. **Routing regression.** Re-run a routing check with the full, current skill list (including Anthropic's built-in skills such as skill-creator, docs, pdf): about 10 prompts that should trigger the new skill, 10 that should trigger neighbours, 5 that should trigger none. Fix descriptions until each prompt lands on exactly one intended skill.
6. **Impact proposals.** For every existing skill the change affects, prepare a complete updated SKILL.md (read the whole current file first). Deliver them with the step 6 chain, the most critical first, and list the rest as pending. Built-in Anthropic skills cannot be edited: add the precedence line to his own skill instead, or give him a one-line settings text to paste. Changes to settings or scheduled-task prompts are suggested as exact text, never applied silently.
7. **Registry.** Update `claude/skill-registry.md` in the project: one row per skill (name, role, owns, defers to, trigger summary, last changed, known conflicts resolved). The next forge run starts from it.

## 5. Synthesis
Compare versions per requirement. Pick the best; merge clearly superior elements from the others if they do not conflict. Re-check the merged version against the self-built scenarios, then run 4c.

## 6. Deliver (hand-off to skill-creator)
1. **Validate:** copy each final skill folder to a writable path and run skill-creator's `scripts/quick_validate.py` on it; fix every error. Keep the original skill name for updates.
2. **Save card, first available route:**
   - `propose_skills` tool present (desktop app / Cowork sessions): propose the complete SKILL.md, at most 3 per call.
   - Otherwise package with skill-creator's `python -m scripts.package_skill <folder> <outdir>` and present each `.skill` file (`present_files`, or `SendUserFile` in Cowork remote). The `.skill` file card shows **Save skill**. Never present a `.zip` as the deliverable: zips get no save button.
   - No file tool at all: give the full SKILL.md text and say which route is missing.
3. **Records:** save the design note, evaluation results and compatibility report to the project (or present them as files); list limitations, open gaps from 4b and pending impact proposals from 4c.
4. **Optional, Claude Code or Cowork only:** skill-creator's description optimizer (`run_loop.py`, needs `claude -p`) on the final description after he approves the skill.