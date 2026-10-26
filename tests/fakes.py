"""Test doubles: a fake machine so plans and captures are tested without touching the real system."""
from pathlib import Path

from mb.facts import Facts


class FakeFacts(Facts):
    def __init__(self, home, apt=(), apt_available=None, snaps=(), flatpaks=(), files=None, checks=None):
        self.home = Path(home)
        self._apt = set(apt)
        self._avail = None if apt_available is None else set(apt_available)
        self._snaps = set(snaps)
        self._flatpaks = set(flatpaks)
        self.files = files or {}          # absolute path -> bytes (what is on the fake machine)
        self.checks = checks or {}        # shell check command -> bool
        self.is_root = False

    def apt_installed(self):
        return set(self._apt)

    def apt_available(self, names):
        return set(names) if self._avail is None else set(names) & self._avail

    def snaps(self):
        return set(self._snaps)

    def flatpaks(self):
        return set(self._flatpaks)

    def read(self, path):
        return self.files.get(str(path))

    def exists(self, path):
        return str(path) in self.files

    def check(self, command):
        return self.checks.get(command, False)
