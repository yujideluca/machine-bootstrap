# Requirements

Every promise the software makes, with an ID. A test that checks it carries the tag `REQ <ID>` in a comment;
`tools/pipeline-check.sh --traceability` fails when a requirement has no test or a tag names an unknown requirement.
Source: G = stated by Giovanni, D = derived by Claude Code and accepted.

| ID | Requirement | Source |
|---|---|---|
| MB-1 | `capture` records the manually installed apt packages, the snaps and the flatpaks in sorted, stable text files under `state/`, so two captures of the same machine are identical | G |
| MB-2 | `capture` copies only files named in the allow-list of `mb.toml`; a file that is not listed is never copied | D |
| MB-3 | No file under `state/` may contain secret material; `capture` refuses to copy a file the scanner flags, and the quality gate fails if `state/` holds one | G |
| MB-4 | `restore` without `--apply` only prints the plan and changes nothing on the machine | D |
| MB-5 | `restore` is idempotent: a step whose result is already present is reported as done and is not run again | D |
| MB-6 | `restore` asks for root only for steps that need it, and runs everything else as the normal user | G |
| MB-7 | `restore` never overwrites a differing file without first saving a timestamped `.mb-bak` copy next to it | D |
| MB-8 | `restore` clones every repository listed in `state/repos.txt` that is missing, and leaves existing folders untouched | G |
| MB-9 | `secrets-backup` writes only an encrypted archive (passphrase typed by Giovanni, never stored), checks it by decrypting it again, and refuses to run if the target is not an existing folder | G |
| MB-10 | `secrets-restore` puts the files back with owner-only permissions (`~/.ssh` and `~/.gnupg` 700, keys 600) and refuses to overwrite an existing file unless asked | D |
| MB-11 | `data-backup` refuses to run when the target is not a mounted drive or has less free space than the data needs, and never deletes anything on the target | G |
| MB-12 | `status` lists what differs between the machine and `state/` (new or removed packages, changed allow-listed files), so the record cannot go stale unnoticed | D |
| MB-13 | `restore` installs the user-space tools (node, claude, codex, uv, JDK, gradle, Android SDK, ...) from recipes in `tools.toml`, each with a check that decides if it is already installed | G |
| MB-14 | `bootstrap.sh` works on a fresh install that has only the base system: it installs what `mb` itself needs (git, python3, rclone) and then runs `mb restore` | G |
| MB-15 | The whole restore has been proven on a clean virtual machine, and the proof (date, what was checked) is recorded in `DESIGN.md` | G |
| MB-16 | `status --notify` shows one desktop notification when `state/` has drifted from the machine (with the count and the first changes) and none when it is current; a weekly user timer runs it | G |
