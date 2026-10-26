"""Command line: capture, status, restore, secrets-backup, secrets-restore, data-backup, scan."""
import argparse
import getpass
import os
import subprocess
import sys
from pathlib import Path

from mb import capture as cap, config as cfgmod, databackup, notify, plan, secrets_backup
from mb.facts import RealFacts
from mb.scan import find_secrets

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "state"


def _ssd_mount(config):
    out = subprocess.run(["findmnt", "-n", "-o", "TARGET", "-S", f"UUID={config.ssd_uuid}"],
                         capture_output=True, text=True).stdout.strip()
    if not out:
        sys.exit(f"The backup drive (UUID {config.ssd_uuid}) is not mounted. Plug it in and try again.")
    return Path(out.splitlines()[0])


def cmd_capture(a, config):
    r = cap.capture(RealFacts(), config, STATE)
    print(f"copied {len(r.copied)} files into state/")
    for label, items in (("SKIPPED", r.skipped), ("REFUSED (secret found)", r.refused),
                         ("NOT SAFE: no git remote", r.local_only)):
        for i in items:
            print(f"  {label}: {i}")
    return 1 if r.refused or r.local_only else 0


def cmd_status(a, config):
    diffs = cap.drift(RealFacts(), config, STATE)
    print("\n".join(diffs) if diffs else "state/ is current")
    if a.notify and (msg := notify.message(diffs)):
        notify.send(*msg)
    return 1 if diffs else 0


def cmd_install_timer(a, config):
    service, timer = notify.timer_units(str(ROOT))
    unit_dir = Path.home() / ".config/systemd/user"
    unit_dir.mkdir(parents=True, exist_ok=True)
    (unit_dir / "mb-status.service").write_text(service)
    (unit_dir / "mb-status.timer").write_text(timer)
    subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "--user", "enable", "--now", "mb-status.timer"], check=True)
    print("weekly check enabled: systemctl --user list-timers mb-status.timer")
    return 0


def cmd_restore(a, config):
    facts = RealFacts()
    steps = plan.build_plan(facts, config, STATE, profile=a.profile)
    pending_root = [s for s in steps if s.root and not s.done]
    if a.apply and pending_root and not facts.is_root:
        print("Some steps need root: asking for your password once.")
        if subprocess.run(["sudo", "-v"]).returncode != 0:
            return 1
    if a.apply:
        result = plan.apply_plan(facts, config, STATE, a.profile, plan.run_step, keep_going=not a.stop_on_error)
        steps = plan.build_plan(facts, config, STATE, profile=a.profile)
    else:
        result = plan.execute(steps, False, plan.run_step)
    pending = [s for s in steps if not s.done]
    print(f"\n{len(steps) - len(pending)} done, {len(pending)} {'failed or pending' if a.apply else 'to do'}")
    if not a.apply:
        print("Nothing was changed. Run again with --apply to do it.")
    print("Still manual: `python3 -m mb secrets-restore ARCHIVE` (your passphrase), then `gh auth status`; "
          "personal files come back from the drive with `rsync -a DRIVE/machine-bootstrap/home/ ~/`.")
    return 0 if result.ok else 1


def _passphrase(confirm):
    first = getpass.getpass("Passphrase: ")
    if confirm and getpass.getpass("Again: ") != first:
        sys.exit("The two passphrases differ. Nothing was written.")
    return first


def cmd_secrets_backup(a, config):
    dests, remotes = [], []
    for t in a.to or ["ssd", "gdrive"]:
        if t == "ssd":
            d = _ssd_mount(config) / "machine-bootstrap" / "secrets"
            d.mkdir(parents=True, exist_ok=True)
            dests.append(d)
        elif t == "gdrive":
            remotes.append(config.gdrive_path)
        elif ":" in t:
            remotes.append(t)
        else:
            dests.append(Path(t))
    staging = None
    if not dests:
        staging = ROOT / "build" / "secrets-staging"
        staging.mkdir(parents=True, exist_ok=True)
        dests.append(staging)
    out = secrets_backup.create(Path.home(), config.secrets_paths, dests, _passphrase(True))
    for p in out:
        print(f"written and verified: {p}")
    for rel in out.missing:
        print(f"  not found, nothing saved for: {rel}")
    for remote in remotes:
        if subprocess.run(["rclone", "copyto", str(out[0]), f"{remote}/{out[0].name}"]).returncode != 0 or \
           subprocess.run(["rclone", "check", str(out[0].parent), remote, "--one-way", "--include", out[0].name]).returncode != 0:
            print(f"UPLOAD FAILED: {remote}")
            return 1
        print(f"uploaded and compared: {remote}/{out[0].name}")
    if staging:
        for p in out:
            p.unlink()
    return 0


def cmd_secrets_restore(a, config):
    names = secrets_backup.restore(Path(a.archive), _passphrase(False), Path.home(), force=a.force)
    print(f"restored {len(names)} entries with owner-only permissions")
    return 0


def cmd_data_backup(a, config):
    target = _ssd_mount(config) if a.to == "ssd" else Path(a.to)
    dirs = config.data_dirs + (config.bulk_dirs if a.bulk else [])
    databackup.run(Path.home(), dirs, target, verify=a.verify)
    if a.verify:
        print("every file on the drive matches the original (checksums)")
    return 0


def cmd_scan(a, config):
    bad = 0
    for p in sorted(STATE.rglob("*")):
        if p.is_file() and not p.is_symlink():
            for hit in find_secrets(p.read_text(errors="replace")):
                print(f"{p.relative_to(ROOT)}: {hit}")
                bad += 1
    print("state/ is clean" if not bad else f"{bad} secret(s) found")
    return 1 if bad else 0


def main(argv=None):
    p = argparse.ArgumentParser(prog="mb", description=__doc__)
    p.add_argument("--config", default=str(ROOT / "mb.toml"))
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("capture", help="record this machine into state/").set_defaults(fn=cmd_capture)
    st = sub.add_parser("status", help="what differs between the machine and state/")
    st.add_argument("--notify", action="store_true", help="also show a desktop notification when it differs")
    st.set_defaults(fn=cmd_status)
    sub.add_parser("install-timer", help="weekly drift check as a user timer").set_defaults(fn=cmd_install_timer)
    r = sub.add_parser("restore", help="rebuild from state/ (dry run unless --apply)")
    r.add_argument("--apply", action="store_true")
    r.add_argument("--profile", choices=["same", "new"], default="same",
                   help="'new' skips drivers, kernels and settings tied to this laptop's hardware")
    r.add_argument("--stop-on-error", action="store_true")
    r.set_defaults(fn=cmd_restore)
    s = sub.add_parser("secrets-backup", help="encrypted copy of keys and logins")
    s.add_argument("--to", action="append", help="ssd, gdrive, a folder, or remote:path (repeatable)")
    s.set_defaults(fn=cmd_secrets_backup)
    s = sub.add_parser("secrets-restore", help="put keys and logins back")
    s.add_argument("archive")
    s.add_argument("--force", action="store_true")
    s.set_defaults(fn=cmd_secrets_restore)
    d = sub.add_parser("data-backup", help="copy personal folders to the drive")
    d.add_argument("--to", default="ssd")
    d.add_argument("--bulk", action="store_true", help="also Anime, Videos, Games")
    d.add_argument("--verify", action="store_true", help="only compare the copy with the originals by checksum")
    d.set_defaults(fn=cmd_data_backup)
    sub.add_parser("scan", help="fail if state/ holds secret material").set_defaults(fn=cmd_scan)
    a = p.parse_args(argv)
    try:
        return a.fn(a, cfgmod.load(a.config))
    except (secrets_backup.SecretsError, databackup.DataBackupError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
