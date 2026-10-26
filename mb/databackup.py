"""Copy personal folders to the external drive. Refuses unsafe targets and never deletes anything there."""
import os
import shutil
import sys
import subprocess
import time
from pathlib import Path


class DataBackupError(Exception):
    pass


def tree_size(path):
    total = 0
    for dirpath, _, files in os.walk(path):
        for f in files:
            try:
                total += os.lstat(os.path.join(dirpath, f)).st_size
            except OSError:
                pass
    return total


def existing_sources(home, dirs, note):
    found = []
    for d in dirs:
        p = Path(home) / d
        if p.is_dir():
            found.append(p)
        else:
            note(f"skipped (not found): {d}")
    return found


def preflight(home, dirs, target, is_mount=os.path.ismount, free=lambda p: shutil.disk_usage(p).free):
    if not is_mount(str(target)):
        raise DataBackupError(f"{target} is not a mounted drive; plug it in (a plain folder would fill the system disk)")
    need = sum(tree_size(p) for p in existing_sources(home, dirs, lambda _: None))
    room = free(str(target))
    if room < need + need // 100 + 1:
        raise DataBackupError(f"not enough free space on {target}: need {need} bytes, have {room}")
    return need


def dest_for(home, src, target):
    return Path(target) / "machine-bootstrap" / "home" / Path(src).relative_to(home)


def verify_argv(src, dst):
    """Dry run with checksums: lists every file that differs between the folder and its copy."""
    return ["rsync", "--archive", "--dry-run", "--checksum", "--itemize-changes", f"{src}/", f"{dst}/"]


def rsync_argv(src, dst, backup_dir=None):
    argv = ["rsync", "--archive", "--partial", "--human-readable", "--info=stats1" + (",progress2" if sys.stdout.isatty() else "")]
    if backup_dir:
        argv += ["--backup", f"--backup-dir={backup_dir}"]   # an overwritten file keeps its old version
    return argv + [f"{src}/", f"{dst}/"]


def run(home, dirs, target, log=print, verify=False):
    need = preflight(home, dirs, target)
    log(f"{need / 1e9:.1f} GB to check; free space is enough")
    base = Path(target) / "machine-bootstrap"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    failed = []
    for src in existing_sources(home, dirs, log):
        dst = dest_for(home, src, target)
        log(f"== {src.relative_to(home)}")
        if verify:
            out = subprocess.run(verify_argv(src, dst), capture_output=True, text=True)
            changed = [l for l in out.stdout.splitlines() if l.strip()]
            if out.returncode != 0 or changed:
                failed.append(str(src.relative_to(home)))
                log(f"   DIFFERS: {len(changed)} item(s), e.g. {changed[:3]}")
            continue
        dst.mkdir(parents=True, exist_ok=True)
        if subprocess.run(rsync_argv(src, dst, base / "versions" / stamp / src.relative_to(home))).returncode != 0:
            failed.append(str(src.relative_to(home)))
    if failed:
        raise DataBackupError(("copy differs from the original in: " if verify else "rsync reported errors in: ")
                              + ", ".join(failed))
