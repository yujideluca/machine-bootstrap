"""What the machine looks like right now. The only module (with plan.execute) that talks to the system."""
import os
import subprocess
from pathlib import Path


class Facts:
    """Interface; the filesystem helpers have real defaults so a fake only overrides what it fakes."""
    home = Path.home()
    is_root = os.geteuid() == 0

    def apt_installed(self): raise NotImplementedError
    def apt_available(self, names): raise NotImplementedError
    def snaps(self): raise NotImplementedError
    def flatpaks(self): raise NotImplementedError
    def check(self, command): raise NotImplementedError

    def read(self, path):
        try:
            return Path(path).read_bytes()
        except OSError:
            return None

    def exists(self, path):
        return os.path.lexists(path)

    def readlink(self, path):
        try:
            return os.readlink(path)
        except OSError:
            return None

    def git_remote(self, path):
        return None


def _out(argv):
    """Output of a command, or "" if it fails or is not installed (a fresh system has no snap, flatpak ...)."""
    try:
        r = subprocess.run(argv, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return r.stdout if r.returncode == 0 else ""


class RealFacts(Facts):
    def apt_installed(self):
        return {l.strip() for l in _out(["apt-mark", "showmanual"]).splitlines() if l.strip()}

    def apt_available(self, names):
        names, ok = sorted(names), set()
        for i in range(0, len(names), 200):
            chunk = names[i:i + 200]
            current = None
            for line in _out(["apt-cache", "policy", *chunk]).splitlines():
                if line and not line[0].isspace() and line.endswith(":"):
                    current = line[:-1]
                elif current and line.strip().startswith("Candidate:") and "(none)" not in line:
                    ok.add(current)
        return ok

    def snaps(self):
        found = set()
        for line in _out(["snap", "list"]).splitlines()[1:]:
            cols = line.split()
            if len(cols) < 6 or cols[-1] in ("base", "snapd"):
                continue
            found.add(f"{cols[0]} classic" if "classic" in cols[-1] else cols[0])
        return found

    def flatpaks(self):
        return {l.strip() for l in _out(["flatpak", "list", "--app", "--system", "--columns=application"]).splitlines()
                if l.strip()}

    def check(self, command):
        env = dict(os.environ, PATH=f"{Path.home()}/.local/bin:{os.environ.get('PATH', '')}")
        try:
            return subprocess.run(["bash", "-c", command], env=env, capture_output=True, timeout=30).returncode == 0
        except subprocess.TimeoutExpired:
            return False

    def git_remote(self, path):
        out = _out(["git", "-C", str(path), "remote", "get-url", "origin"]).strip()
        return out or None
