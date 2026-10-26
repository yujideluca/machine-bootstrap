"""Record the machine into state/. Only allow-listed files are copied, and never one the scanner flags."""
import fnmatch
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from mb.scan import find_secrets


@dataclass
class Report:
    copied: list = field(default_factory=list)
    skipped: list = field(default_factory=list)
    refused: list = field(default_factory=list)
    local_only: list = field(default_factory=list)   # repositories with no remote: not safe anywhere else


def _write_list(path, items):
    path.write_text("".join(f"{i}\n" for i in sorted(items)))


def _skipped_name(name, config):
    return any(fnmatch.fnmatch(name, g) for g in config.skip_globs)


def _copy_one(src, dst, rel, config, report):
    if src.is_symlink():
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.symlink_to(os.readlink(src))
        report.copied.append(rel)
        return
    try:
        size = src.stat().st_size
        if size > config.max_file_bytes:
            report.skipped.append(f"{rel}: larger than {config.max_file_bytes} bytes (belongs in data-backup)")
            return
        data = src.read_bytes()
    except OSError as e:
        report.skipped.append(f"{rel}: {e.strerror}")
        return
    hits = find_secrets(data.decode("utf-8", "replace"))
    if hits:
        report.refused.append(f"{rel}: {', '.join(hits)} (goes in secrets-backup instead)")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    shutil.copymode(src, dst)
    report.copied.append(rel)


def _copy_tree(root, rel, out_root, config, report):
    src = root / rel
    if not os.path.lexists(src):
        return
    if src.is_dir() and not src.is_symlink():
        for dirpath, dirnames, filenames in os.walk(src):
            dirnames[:] = [d for d in dirnames if not _skipped_name(d, config)]
            for d in list(dirnames):
                p = Path(dirpath) / d
                if p.is_symlink():
                    dirnames.remove(d)
                    _copy_one(p, out_root / p.relative_to(root), str(p.relative_to(root)), config, report)
            for f in filenames:
                if _skipped_name(f, config):
                    continue
                p = Path(dirpath) / f
                _copy_one(p, out_root / p.relative_to(root), str(p.relative_to(root)), config, report)
    elif not _skipped_name(src.name, config):
        _copy_one(src, out_root / rel, str(rel), config, report)


def capture(facts, config, state):
    state = Path(state)
    state.mkdir(parents=True, exist_ok=True)
    report = Report()
    _write_list(state / "apt-manual.txt", facts.apt_installed())
    _write_list(state / "snap.txt", facts.snaps())
    _write_list(state / "flatpak.txt", facts.flatpaks())

    for sub in ("home", "etc"):
        shutil.rmtree(state / sub, ignore_errors=True)
    for rel in list(config.home_files) + list(config.home_dirs):
        _copy_tree(facts.home, Path(rel), state / "home", config, report)
    for path in config.system_files:
        _copy_tree(Path("/"), Path(path.lstrip("/")), state / "etc", config, report)

    repos = []
    root = facts.home / config.repos_root.removeprefix("~/")
    if root.is_dir():
        for d in sorted(p for p in root.iterdir() if (p / ".git").is_dir()):   # a .git file is a worktree of another repo
            url = facts.git_remote(d)
            if url:
                repos.append(f"{d.relative_to(facts.home)}\t{url}")
            else:
                report.local_only.append(str(d.relative_to(facts.home)))
    _write_list(state / "repos.txt", repos)
    return report


def _tree(root):
    out = {}
    root = Path(root)
    if root.is_dir():
        for p in root.rglob("*"):
            if p.is_symlink():
                out[str(p.relative_to(root))] = ("link", os.readlink(p))
            elif p.is_file():
                out[str(p.relative_to(root))] = ("file", p.read_bytes())
    return out


def drift(facts, config, state):
    """Differences between the machine now and what state/ holds. Empty list = state is current."""
    state = Path(state)
    with tempfile.TemporaryDirectory() as tmp:
        capture(facts, config, tmp)
        diffs = []
        for name, label in (("apt-manual.txt", "apt"), ("snap.txt", "snap"), ("flatpak.txt", "flatpak"),
                            ("repos.txt", "repo")):
            old = set((state / name).read_text().split("\n")) if (state / name).exists() else set()
            new = set((Path(tmp) / name).read_text().split("\n"))
            old.discard(""), new.discard("")
            diffs += [f"{label} + {x}" for x in sorted(new - old)]
            diffs += [f"{label} - {x}" for x in sorted(old - new)]
        for sub, prefix in (("home", ""), ("etc", "/")):
            old, new = _tree(state / sub), _tree(Path(tmp) / sub)
            for k in sorted(new.keys() - old.keys()):
                diffs.append(f"new {prefix}{k}")
            for k in sorted(old.keys() - new.keys()):
                diffs.append(f"removed {prefix}{k}")
            for k in sorted(old.keys() & new.keys()):
                if old[k] != new[k]:
                    diffs.append(f"changed {prefix}{k}")
    return diffs
