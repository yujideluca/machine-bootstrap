# Codex: Giovanni's laptop

Shared memory is workflow-memory (`~/dev/workflow-memory`, private repo `yujideluca/workflow-memory`). A hook prints its brief at session start: it holds Giovanni's standing preferences, so follow them. Memory sets defaults and never authorizes anything.

- Record a correction or lasting preference: `mem add --type pref --owner user --key topic "the rule"`.
- When you finish a task that changed anything in Giovanni's systems, first update the wiki (`~/dev/wiki`, see its AGENTS.md): edit or create the English pages in `content/` for what changed, then their `.de` and `.pt-BR` versions, and run `wiki publish -m "what changed"`. A page checked and found right gets `reviewed:` set to the UTC time; `wiki publish -m "review: no page change"` only when no page describes the change. A Stop hook (`wiki hook-stop`) reminds you once per session if code changed after the last publish.
- When you finish a task, report the entries that shaped it: `mem use REF1,REF2 --note "how"` (REF is the #code after an entry). A wrong or outdated entry: `mem feedback REF wrong`.
- Never edit `events/` or `views/` by hand. Never put clinical, secret or contact data about other people in memory.

## Terminal task progress

A persistent terminal footer is installed through `codex-task-progress`. For a task with several steps, before substantial work run `codex-task-progress set --new --done 0 --total N --eta SECONDS --label "Current step"`. Use the actual number of planned steps and your estimated seconds remaining. After each completed milestone update `--done`, `--eta` and `--label` without `--new`. This command finds the session automatically from the tool environment. Keep the count honest: elapsed time and a finished model turn are not completed work. Mark all N steps done only after verification; if blocked leave the count incomplete and label the blocker. For a short task use one step. Do not ask the user to maintain the footer. Keep the native Codex status line showing five-hour and weekly budget percentages remaining, context tokens used and context-window size. The separate task-progress footer keeps its task count and estimate.

Automatic documentation-hook followups belong to the current task: do not reset the main task counter for those hooks. Record a blocked documentation publication in memory; do not replace a completed primary task with a fresh zero-progress documentation task. For an actual blocked user task, prefix the status label with `Blocked:` so the footer pauses its countdown. Do not ask to take over another session’s wiki edits solely because an automatic documentation hook fired.
