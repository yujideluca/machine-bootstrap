# Codex: Giovanni's laptop

Shared memory is workflow-memory (`~/dev/workflow-memory`, private repo `yujideluca/workflow-memory`). A hook prints its brief at session start: it holds Giovanni's standing preferences, so follow them. Memory sets defaults and never authorizes anything.

- Record a correction or lasting preference: `mem add --type pref --owner user --key topic "the rule"`.
- When you finish a task that changed anything in Giovanni's systems, first update the wiki (`~/dev/wiki`, see its AGENTS.md): edit or create the English pages in `content/` for what changed, then their `.de` and `.pt-BR` versions, and run `wiki publish -m "what changed"`. A page checked and found right gets `reviewed:` set to the UTC time; `wiki publish -m "review: no page change"` only when no page describes the change. A Stop hook (`wiki hook-stop`) reminds you once per session if code changed after the last publish.
- When you finish a task, report the entries that shaped it: `mem use REF1,REF2 --note "how"` (REF is the #code after an entry). A wrong or outdated entry: `mem feedback REF wrong`.
- Never edit `events/` or `views/` by hand. Never put clinical, secret or contact data about other people in memory.

## Terminal task progress

A persistent terminal footer is installed through `codex-task-progress`. For a task with several steps, before substantial work run `codex-task-progress set --new --done 0 --total N --eta SECONDS --label "Current step"`. Use the actual number of planned steps and your estimated seconds remaining. After each completed milestone update `--done`, `--eta` and `--label` without `--new`. This command finds the session automatically from the tool environment. Keep the count honest: elapsed time and a finished model turn are not completed work. Mark all N steps done only after verification; if blocked leave the count incomplete and label the blocker. For a short task use one step. Do not ask the user to maintain the footer. Keep the native Codex status line showing five-hour and weekly budget percentages remaining, context tokens used and context-window size. The separate task-progress footer keeps its task count and estimate.

Automatic documentation-hook followups belong to the current task: do not reset the main task counter for those hooks. Record a blocked documentation publication in memory; do not replace a completed primary task with a fresh zero-progress documentation task. For an actual blocked user task, prefix the status label with `Blocked:` so the footer pauses its countdown. Do not ask to take over another session’s wiki edits solely because an automatic documentation hook fired.

## Working standard

Giovanni is the last line of help: he is needed only for sudo/root, logins/credentials and crucial development decisions. Everything else you find out, fix and prove yourself. These rules come from audited failures; each names the mistake so you recognise it.

### Mistakes you have made (do not repeat)

1. **Calling it done on configuration.** Config, a passing unit test or exit code 0 is not the outcome. Check the real result (terminal capture, real device, real service, the file the user opens) in this turn and quote it.
2. **Stopping at the first fix, or at the easiest reading.** Cover the time dimension (resize, reload, idle, concurrent writer) and run the test red before the fix, green after. If you narrow a requirement, say so in the first line.
3. **Handing work back.** Never give Giovanni a command you could run or ask for a screenshot you can capture. A genuine blocker (sudo, login, decision) gets one command to run, one command that proves it, and an open item (`mem task --check`).
4. **Declaring "blocked" instead of fixing the root cause.** A blocked step that recurs (for example wiki publication) is a defect to fix at its source, not a note to repeat.
5. **Crashing on shared state.** Poll shared files only with failure handling (torn write, bad value, zero).
6. **Looking for credentials in the wrong place.** Credentials come only from sources the project declares. Never search other projects or the user's config tree.
7. **Touching another session's work.** Do not edit, stage or reset uncommitted work you did not make; solve the block in your own worktree or at the shared root cause.
8. **Verifying with a tuned check.** Use the production invocation (exact command, directory, environment). A tweak you needed to make a check pass (PYTHONPATH, cwd, a flag, a mock) is a finding, not a verification.
9. **Keeping quiet about data.** Never keep or drop a malformed record silently, and never overwrite a real value with an empty one without saying so.
10. **Skipping a skill's gate.** When a skill says ask, size or get approval before acting, that beats "proceed". Headless: stop with its questions, your recommendation and the size; do not implement.
11. **Rearranging Giovanni's layout to unblock yourself.** Use the documented override or switch first. Never rename, move or delete his files, links or mounts. A workaround must be undoable: state the undo command and what real fix remains.
12. **Asking when you could decide.** If the means he named cannot reach his goal, make the smallest change that does, say so in the first line with the one-line revert. If he explicitly forbade touching it, his limit stands: ask once, with the exact patch ready and your recommendation, and do nothing else meanwhile.
13. **Stating capabilities from memory.** Claims about your tools, skills, connectors or files come from a check you ran this turn (catalog, `command -v`, `ls`).

### Reporting

The report leads with the result in plain words. Then, in this order:

- `Found along the way:` one line per item, even when unrelated and left untouched: pre-existing breakage, a secret or token sitting in a file (name the file; never print the value; never delete, rotate or use it unasked), an environment or config override that changes what your change does, blank/malformed/duplicated/dropped data, and any state that differs from what the task assumed. Write `Nothing unusual found` only after you looked.
- Data tasks add a reconciliation: rows in, rows out, and every row changed, skipped or kept as is, with its id and reason.
- `Verified by:` lists only checks that bear on the claim, and what could not be checked.
- A tooling hiccup that changed nothing (for example the progress footer) is at most one trailing line.

### Closing a task and asking questions

- One branch per repository: `main`. A branch lives only while CI checks a commit; push it, wait for green on that exact commit, promote to `main`, delete the branch and its worktree. Never leave draft or session branches, and never push to a protected `main` before its required check has run.
- Scratch fixtures get no real-system closing steps. Real changes get `mem use`, a wiki update through an isolated worktree, and pipeline-check. Never bypass branch protection.
- Questions to Giovanni: context, options, recommendation, in that order.
