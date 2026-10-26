# Runbook: moving to a new computer, or after a reinstall

Written for the day it is needed, possibly months from now. Read it top to bottom; nothing here assumes you remember
how the tool works. **The complete manual, with every step explained, the failure table and the disaster plans, is
[`MANUAL.md`](MANUAL.md)** (give it to any AI assistant that helps you).

## What you need in hand

1. The **external SSD** (it holds the encrypted keys archive and your personal files).
2. The **passphrase** you typed when you ran `secrets-backup` (not stored anywhere on any computer).
3. A freshly installed Kubuntu/Ubuntu with internet, and a user account that can use `sudo`.

## A. Get the tool

```bash
sudo apt-get update && sudo apt-get install -y git          # only if git is missing
git clone https://github.com/yujideluca/machine-bootstrap     # public repository: no login needed
# otherwise copy it from the SSD: rsync -a /run/media/$USER/<drive>/machine-bootstrap/tool/ machine-bootstrap/
cd machine-bootstrap
```

## B. Keys and logins first (needs the SSD and the passphrase)

Do this **before** the restore: the private repositories (`codex-pbar`, `project-template`) need the SSH key, and the
wiki needs its sign-in files. It needs only Python and `gpg`, which every Ubuntu has.

```bash
ls /run/media/$USER/*/machine-bootstrap/secrets/        # newest mb-secrets-*.tar.gpg
python3 -m mb secrets-restore /run/media/$USER/<drive>/machine-bootstrap/secrets/<newest file>
```

(If the SSD is not at hand, the same file is on Google Drive in `machine-bootstrap/`: download it in a browser.)
Then check: `ssh -T git@github.com` greets you by name.

## C. Restore the setup

```bash
./bootstrap.sh                          # dry run: shows what would happen, changes nothing but the prerequisites
```

Read the list: `[done]` is already fine, `[todo]` would be done. Then:

```bash
./bootstrap.sh --apply                  # SAME laptop (Acer Nitro), a reinstall
./bootstrap.sh --apply --profile new    # a DIFFERENT computer: skips Nvidia drivers, kernels, this laptop's keyboard/GPU files
```

It asks for your password once. It installs packages, snaps and flatpaks, clones your repositories, installs the
tools (Node, uv, Claude Code, Codex, JDK, Gradle, Android SDK, Rust tools, the wiki) and finally puts your settings
back (a file you already have is first saved as `name.mb-bak-DATE`). The boot loader is never touched. Running it
again is safe: finished steps say `[done]`.

## D. Personal files

```bash
rsync -a --info=progress2 /run/media/$USER/<drive>/machine-bootstrap/home/ ~/
```

## E. Checks that it worked

`python3 -m mb status` (no differences), `claude --version`, `gh auth status`, open QuizApp and run `tools/quality_gate.sh`.
The wiki service and the Claude assistant start by themselves after login (`systemctl --user status wiki claude-assistant`).

## Keeping the record fresh (do this, or the record is a photo of the past)

| When | Command |
|---|---|
| Every month (and when you install or remove software) | `python3 -m mb status`, then `python3 -m mb capture`, review, commit and push |
| After changing an SSH/GPG key, a login, or the Android signing key | `python3 -m mb secrets-backup` (SSD plugged in, Drive connected) |
| Every month with the SSD plugged in | `python3 -m mb data-backup` (add `--bulk` for Anime, Videos, Games) |

## If something fails

- `mb restore` prints `[FAIL] step (exit N)` and carries on with the rest; fix the cause and run it again.
- `apt package not available on this system, skipped: X` — the new Ubuntu release no longer has it; install an
  alternative by hand if you still need it.
- A tool recipe fails (a download URL moved): edit that `[[recipe]]` in `mb.toml`, run again.

## Not covered (known gaps)

Browser profiles (Chrome sync restores them), the Android phone's own settings, Steam and Lutris game installs (only
the apps), and the packages that exist only on this laptop (`vesktop`, `utility-birdid`, a Claude desktop build: the
restore lists them as "not available" and skips them).
