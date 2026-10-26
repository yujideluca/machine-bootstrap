# machine-bootstrap

Rebuild Giovanni's computer setup after a reinstall or on a new machine.

Public repository: https://github.com/yujideluca/machine-bootstrap. Captured settings and package lists are public; encrypted archives and credentials are excluded.

```bash
python3 -m mb capture            # record packages, settings, repos into state/
python3 -m mb status             # what changed on the machine since the last capture
python3 -m mb restore            # dry run: show what a restore would do
python3 -m mb restore --apply    # do it (add --profile new on a different computer)
python3 -m mb secrets-backup     # encrypted keys/logins -> SSD + Google Drive (asks for your passphrase)
python3 -m mb secrets-restore FILE
python3 -m mb data-backup        # personal folders -> SSD (add --bulk for Anime, Videos, Games)
```

On a fresh install: `git clone`, then `./bootstrap.sh`. **Read `docs/RESTORE.md` first** (the step-by-step runbook).

| Where | What |
|---|---|
| `mb.toml` | the allow-lists and tool recipes: the only place that decides what is captured |
| `state/` | generated record of the machine (no secrets: the gate scans it) |
| `docs/RESTORE.md` | one-page runbook for moving to a new computer |
| `docs/MANUAL.md` | the complete manual (humans and AI assistants): checklist, steps, failures, disasters |
| `docs/REQUIREMENTS.md`, `DESIGN.md`, `docs/adr/` | what it promises, how it is built, why |
| `tools/quality_gate.sh` | the one definition of "passing" |
| `tools/vm-test.sh` | proof on a clean virtual machine (about an hour) |

Python standard library only, plus Bash and the tools already on a fresh Ubuntu (`git`, `gpg`, `rsync`, `rclone`).
