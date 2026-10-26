import tempfile
import unittest
from pathlib import Path

from mb.capture import capture, drift
from mb.config import Config
from tests.fakes import FakeFacts


def make_config(**over):
    base = dict(
        home_files=[".bashrc", ".gitconfig"], home_dirs=[".config/autostart"],
        etc_portable=["/etc/hostname-x"], etc_hardware=["/etc/modprobe.d/nvidia.conf"],
        apt_sources=[], skip_globs=["*.bak*", "*.pre-*"], max_file_bytes=1000,
        hardware_packages=["nvidia-*", "linux-*"], repos_root="~/dev",
    )
    base.update(over)
    return Config(**base)


class CaptureTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name) / "home"
        self.home.mkdir()
        self.state = Path(self.tmp.name) / "state"

    def facts(self, **kw):
        return FakeFacts(self.home, **kw)

    def put(self, rel, text):
        p = self.home / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    # REQ MB-1
    def test_package_lists_are_sorted_and_stable(self):
        f = self.facts(apt=["zsh", "git", "curl"], snaps=["spotify", "code"], flatpaks=["org.b", "org.a"])
        capture(f, make_config(), self.state)
        first = {p.name: p.read_text() for p in self.state.iterdir() if p.is_file()}
        self.assertEqual(first["apt-manual.txt"].split(), ["curl", "git", "zsh"])
        self.assertEqual(first["snap.txt"].split(), ["code", "spotify"])
        self.assertEqual(first["flatpak.txt"].split(), ["org.a", "org.b"])
        capture(f, make_config(), self.state)
        second = {p.name: p.read_text() for p in self.state.iterdir() if p.is_file()}
        self.assertEqual(first, second)

    # REQ MB-2
    def test_only_allow_listed_files_are_copied(self):
        self.put(".bashrc", "alias x=y\n")
        self.put(".not_listed", "private\n")
        self.put(".config/autostart/a.desktop", "[Desktop Entry]\n")
        self.put(".config/other/b", "x")
        capture(self.facts(), make_config(), self.state)
        copied = sorted(str(p.relative_to(self.state / "home")) for p in (self.state / "home").rglob("*") if p.is_file())
        self.assertEqual(copied, [".bashrc", ".config/autostart/a.desktop"])

    # REQ MB-2
    def test_skip_globs_and_size_cap(self):
        self.put(".config/autostart/a.desktop", "ok")
        self.put(".config/autostart/a.desktop.bak-1", "old")
        self.put(".config/autostart/big", "x" * 5000)
        report = capture(self.facts(), make_config(), self.state)
        names = sorted(p.name for p in (self.state / "home" / ".config/autostart").iterdir())
        self.assertEqual(names, ["a.desktop"])
        self.assertTrue(any("big" in s for s in report.skipped))

    # REQ MB-3
    def test_file_with_a_secret_is_refused(self):
        self.put(".bashrc", "export GH=ghp_" + "c" * 36 + "\n")
        self.put(".gitconfig", "[user]\nname = x\n")
        report = capture(self.facts(), make_config(), self.state)
        self.assertFalse((self.state / "home" / ".bashrc").exists())
        self.assertTrue((self.state / "home" / ".gitconfig").exists())
        self.assertEqual([r.split(":")[0] for r in report.refused], [".bashrc"])
        for p in self.state.rglob("*"):
            if p.is_file():
                self.assertNotIn("ghp_", p.read_text(errors="replace"))

    # REQ MB-2
    def test_removed_file_disappears_from_state(self):
        self.put(".bashrc", "a")
        capture(self.facts(), make_config(), self.state)
        (self.home / ".bashrc").unlink()
        capture(self.facts(), make_config(), self.state)
        self.assertFalse((self.state / "home" / ".bashrc").exists())

    # REQ MB-12
    def test_drift_reports_new_removed_and_changed(self):
        self.put(".bashrc", "v1")
        capture(self.facts(apt=["git", "curl"]), make_config(), self.state)
        (self.home / ".bashrc").write_text("v2")
        d = drift(self.facts(apt=["git", "vim"]), make_config(), self.state)
        self.assertIn("apt + vim", d)
        self.assertIn("apt - curl", d)
        self.assertIn("changed .bashrc", d)

    # REQ MB-12
    def test_no_drift_right_after_capture(self):
        self.put(".bashrc", "v1")
        capture(self.facts(apt=["git"]), make_config(), self.state)
        self.assertEqual(drift(self.facts(apt=["git"]), make_config(), self.state), [])

    # REQ MB-2
    def test_symlinks_are_kept_as_links_not_followed(self):
        d = self.home / ".config/autostart"
        d.mkdir(parents=True)
        (d / "link").symlink_to("/etc/passwd")
        capture(self.facts(), make_config(), self.state)
        copied = self.state / "home" / ".config/autostart/link"
        self.assertTrue(copied.is_symlink())
        self.assertEqual(str(copied.readlink()), "/etc/passwd")


if __name__ == "__main__":
    unittest.main()
