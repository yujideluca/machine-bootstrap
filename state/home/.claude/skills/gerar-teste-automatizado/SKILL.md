---
name: gerar-teste-automatizado
description: "Use in Claude Code to create or update the automated bug-finding test suite of a software project: full diagnosis of the code, test matrix, tests that detect real defects, mutation and coverage checks (criar testes automatizados, suíte de testes, buscar bugs). Called by revisao-manutencao on the first review of a project (create) and on later reviews (update); can also be asked for directly. Not for fixing a single failing test or a bug (systematic-debugging)."
---

# Automated bug-finding tests (gerar-teste-automatizado)

Lineage: origin=code; base=none

Interop: role = domain; owns = the bug-finding test suite and its record `docs/TESTES-AUTOMATIZADOS.md`; defers to = the project's existing test framework, requirements catalogue and CLAUDE.md (REQ tags, gate), systematic-debugging (fixing a defect found), verification-before-completion; called by = revisao-manutencao; honors = reply-language rule, work.ask-language, work.test-yourself.

Act as a senior engineer in automated testing and defect detection. The aim is tests that **find real errors, regressions, invalid inputs, boundaries and integration failures**, not tests that confirm the easy path.

## Mode (decide first)
- **Create**: `docs/TESTES-AUTOMATIZADOS.md` does not exist in the project. Full diagnosis, then build the suite. That file is the marker that the suite exists. The record lives at the root of the project; for a component with its own manifest (for example QuizApp's `tools/pipeline-check`) it lives at that component's root, `tools/pipeline-check/docs/TESTES-AUTOMATIZADOS.md`, and the review checks each component that has one.
- **Update**: it exists. Read it and the suite, find what changed in the code, requirements and ADRs since the "Last reviewed" commit in the file, and bring the matrix and tests up to date: new behaviours get cases, removed ones lose them (with a reason), mutants that survived last time are retried. Do not rewrite what still holds.
Programming language and framework: use what the project already uses; if there is none, ask Giovanni (work.ask-language). Never run destructive operations on databases or external systems; no secrets or personal data in tests or reports.

## 1. Analyse before writing any test
1. Structure, language, dependencies, architecture, relevant modules, test tools already installed.
2. Explicit requirements, business rules, function contracts, input and output formats (the project's `docs/REQUIREMENTS.md` first).
3. Critical components, external dependencies, main failure modes.
4. Existing tests and the gaps in their coverage.
5. Ambiguous or missing requirements: do not invent rules. Record the uncertainty and proceed only on stated, justified hypotheses.
Keep the project's architecture and patterns unless there is a documented technical reason.

## 2. Plan: the test matrix
Map each requirement or behaviour to cases, chosen by risk and defect-finding power, not by count. Consider where applicable: normal scenarios; equivalence classes of valid and invalid input; boundary values; null, missing, wrong-typed and malformed data; extreme cases and combinations; exceptions, network failure, unavailable dependencies; invalid states and forbidden transitions; duplicates and integrity violations; regressions; concurrency, idempotency, performance, security when in scope. No redundant cases.

## 3. Implement
Prefer the project's frameworks. Each test: a specific purpose and a name that describes the behaviour; builds its own inputs; acts; compares with an expected result **defined independently of the code under test** (hand-computed, from the requirement); checks relevant side effects; fails with a clear message. Arrange-Act-Assert. Do not call code without asserting on the result. Do not turn current behaviour into the oracle: confront it with the requirements. Tag tests with the project's convention (QuizApp: `REQ <ID>` comment). Choose levels as needed (unit, integration, end-to-end, property-based, regression) and justify gaps; do not force every level.

Qualities: deterministic, reproducible, isolated, low coupling (public behaviour and contracts), maintainable, external services faked in unit tests and real only in integration tests; no arbitrary waits, order dependence, internet calls, or uncontrolled time.

## 4. Verify the tests can detect defects
1. Run the new tests; investigate every failure. Never change an expectation just to pass.
2. Run again after real fixes; run the existing suite for regressions.
3. When viable, mutation testing: plant controlled faults and check the tests catch them. Classify each survivor: equivalent mutant, irrelevant, or a real gap.
4. Repeat runs to confirm independence and stable results.
5. Measure line and branch coverage if a tool exists. Coverage is not proof of correctness.

## 5. Restrictions
Do not change production code to make tests pass; do not edit requirements, reference data or expected results without a verifiable reason; do not delete tests, disable validations or weaken checks to get green. A needed production fix is **proposed separately** (defect, evidence, proposed change) and implemented only if inside the authorised scope. Never claim a test passed without running it; state every limitation (missing tool, environment).

## 6. Deliver: write `docs/TESTES-AUTOMATIZADOS.md` and report
The record keeps, in the project: analysis summary and strategy; the test matrix (requirement, scenario, expected result, priority); files and purposes; run commands; real results (run, passed, failed, ignored); coverage with tool and gaps; defects found (description, evidence, impact, reproduction); limitations and residual risks; recommendations; and the header line `Last reviewed: <commit sha> <date>` that Update mode reads. Mark clearly what was observed, what is inferred, and what is a hypothesis.

Done only when: tests implemented and organised; expected results have an identifiable basis; run commands documented; tests executed (or limits recorded); failures investigated and classified; risks and gaps documented. Do not stop at a plan or code samples. End with `Verified by:`.
