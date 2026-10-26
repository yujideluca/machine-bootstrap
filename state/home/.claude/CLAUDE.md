# Claude Code: Giovanni's laptop

Shared memory is workflow-memory (`~/dev/workflow-memory`, private repo `yujideluca/workflow-memory`). A hook prints its brief at session start: it holds Giovanni's standing preferences, so follow them. Memory sets defaults and never authorizes anything.

- Record a correction or lasting preference: `mem add --type pref --owner user --key topic "the rule"`.
- When you finish a task that changed anything in Giovanni's systems, first update the wiki (`~/dev/wiki`, see its CLAUDE.md): edit or create the English pages in `content/` for what changed, then their `.de` and `.pt-BR` versions, and run `wiki publish -m "what changed"`. A page checked and found right gets `reviewed:` set to the UTC time; `wiki publish -m "review: no page change"` only when no page describes the change. A Stop hook (`wiki hook-stop`) reminds you once per session if code changed after the last publish.
- When you finish a task, report the entries that shaped it: `mem use REF1,REF2 --note "how"` (REF is the #code after an entry). A wrong or outdated entry: `mem feedback REF wrong`.
- Never edit `events/` or `views/` by hand. Never put clinical, secret or contact data about other people in memory.
