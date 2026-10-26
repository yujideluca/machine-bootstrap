---
name: project-german-quiz
description: "QuizApp (German B2 quiz, Kotlin/Compose) lives in ~/dev/QuizApp, GitHub yujideluca/german-quiz (private); DESIGN.md must be kept updated"
metadata:
  node_type: memory
  type: project
  originSessionId: 5eb97475-0a97-46c5-9963-33bd9c0edb98
  modified: 2026-10-22T15:10:51.756Z
---

Android app in `~/dev/QuizApp`, pushed 2026-10-15 to private repo `git@github.com:yujideluca/german-quiz.git` (branch main, no `gh` CLI; repo created via the GitHub connector). Env: `source ~/dev/env.sh`. Phone: Motorola edge 50 fusion over adb.

**Why:** Giovanni asked for `DESIGN.md` explaining design and development decisions, "updated periodically".
**How to apply:** update DESIGN.md (decision log + sections + "Last updated") in the same commit as any design-affecting change; repo `CLAUDE.md` says so too. See [[feedback-debug-after-coding]].

**Update feed + signing (2026-10-19):** public repo `yujideluca/german-quiz-releases` holds only `latest.json` + the newest signed release APK (clone at `~/dev/german-quiz-releases`). Publish with `tools/publish_apk.sh` after bumping versionCode/versionName (now 1.5 / 6). All builds are signed with `~/.android/german-quiz-release.jks` (props in `~/.android/german-quiz-signing.properties`, never in the repo); losing it means no in-place update; backed up to Giovanni's Google Drive (My Drive) on 2026-10-22, passwords kept by Giovanni. Progress backup from the key migration: `~/dev/quiz-backups/`. Play Protect shows "App scan recommended" for new APKs; the install-permission appop resets on uninstall.

**Feed caching gotcha (2026-10-19):** raw.githubusercontent.com caches 5 min and ignores query strings (random `?t=` still gave `x-cache: HIT`); a `?v=`/`?t=` "anti-cache" does nothing. The contents API (`api.github.com/repos/yujideluca/german-quiz-releases/contents/<file>` + `Accept: application/vnd.github.raw+json`) caches ≤60 s but allows 60 requests/h per IP. Client fix is in the working tree after v1.6 (see git log); publish needs a version bump to 1.7/8. Every new APK triggers a Play Protect "App scan recommended" tap on the phone.

**Release channels (2026-10-19):** feed repo has branches `main` (stable, user app `dev.yuji.quiz`) and `bleeding-edge` (beta app `dev.yuji.quiz.beta`, separate data, installed on the phone next to the real one). Flow: commit → `tools/publish_apk.sh beta` → test on the beta app → `tools/publish_apk.sh promote` ONLY when Giovanni says the beta is good (it refuses unless bleeding-edge holds that same commit). Source was at 1.8/9 (beta only) while stable stayed 1.7/8. Gradle tasks are flavored (`testStableDebugUnitTest`, `assembleBetaRelease`). Telegram: no tool/bot; sent APKs via the phone's Telegram app (adb push to Download → attach > File > Saved Messages), never to other chats.

**State 2026-10-19 10:36:** stable (`main`) and beta (`bleeding-edge`) are both 1.8/9 from commit c20aeae (promoted at Giovanni's request); phone runs stable 1.8 plus the beta app. Play Protect now scans the stable APK automatically and says "This app looks safe" (no more "App scan recommended" tap, only an Install tap). Commits e30a06f and c20aeae were not pushed to origin yet.

**Fehler finden mode (2026-10-19):** fifth mode, 121 forum/formal-mail sentences with one wrong chunk to tap (`tools/data/errors.tsv` -> `errors.json`), error types taken from Giovanni's corrected Schreiben texts (B2 Goethe doc on Drive + `~/Documents/06 Alemão/aufgabe/Minhas_redacoes_alemao.txt`). Version 2.0 (11), installed on the beta app on the phone, NOT committed or published yet (waits for Giovanni's go).

**Web version (2026-10-19):** PWA clone `~/dev/QuizWeb` (repo yujideluca/german-quiz-web, served by GitHub Pages at https://yujideluca.github.io/german-quiz-web/), port of the Android app. Giovanni's standing rule: every user-version update (promote) must also update the web version and report the link; `tools/check_web_sync.sh` (run by `promote`) exits 2 while it is behind. The service worker is network first since v6. The phone's stable app was still 1.8 until I installed 2.0 by adb (`install -r`, progress kept); a published release does not reach the phone until the app is restarted and the popup is tapped.
