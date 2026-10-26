---
name: feedback-debug-after-coding
description: "After coding or changing anything, always do a first-line debug pass before reporting done (Giovanni's standing rule, 2026-10-15)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: e46b5d15-d4f3-461c-8133-5590d5df66e1
  modified: 2026-10-15T23:59:46.422Z
---

After coding something, always do a first line of debugging before saying it is done: build, run tests, and for QuizApp install on the phone, launch it, exercise the changed flow and check `adb logcat` for crashes/exceptions.

**Why:** Giovanni asked for this explicitly (2026-10-15) after I installed the Settings/removed-questions change without launching it or checking logs.
**How to apply:** report what the debug pass covered and what it could not (e.g. phone not connected). QuizApp env: `source ~/dev/env.sh`; project `~/dev/QuizApp`. See [[remote-assistant-setup]] for the other standing setup.
