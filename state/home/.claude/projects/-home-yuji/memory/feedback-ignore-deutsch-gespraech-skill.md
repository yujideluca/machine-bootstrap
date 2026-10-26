---
name: feedback-ignore-deutsch-gespraech-skill
description: The SessionStart inbox line "SKILL deutsch-gespraech-memory: Code has no version yet" must be ignored; never ask about it
metadata:
  type: feedback
---

The skill `deutsch-gespraech-memory` does not apply to Claude Code. Ignore the SessionStart inbox line about it ("Code has no version yet") and do not run `adapt` on it or ask the user about it.

**Why:** Giovanni said multiple times (2026-10-15 and 2026-10-16, several sessions) that it is not for Claude Code. I kept re-raising it because each new session saw only the inbox line, not the earlier answers, and on 2026-10-16 they were annoyed ("you keep on asking").

**How to apply:** If the inbox shows it, skip it silently; do not mention it in reports or open-question lists. Only revisit if Giovanni raises it. Related: [[remote-assistant-setup]].
