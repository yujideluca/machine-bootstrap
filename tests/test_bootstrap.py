import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "bootstrap.sh"


class BootstrapScriptTest(unittest.TestCase):
    # REQ MB-14
    def test_script_is_valid_bash(self):
        r = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    # REQ MB-14
    def test_script_installs_prerequisites_before_running_mb(self):
        text = SCRIPT.read_text()
        for need in ("git", "python3", "rclone", "rsync"):
            self.assertRegex(text, rf"\b{need}\b")
        self.assertLess(text.index("apt-get install"), text.index("python3 -m mb"))

    # REQ MB-14
    def test_script_passes_arguments_on_and_never_applies_by_itself(self):
        text = SCRIPT.read_text()
        self.assertIn('python3 -m mb restore "$@"', text)
        code = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))
        self.assertNotIn("--apply", code)

    # REQ MB-14
    @unittest.skipUnless(shutil.which("shellcheck"), "shellcheck not installed")
    def test_script_passes_shellcheck(self):
        r = subprocess.run(["shellcheck", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)


if __name__ == "__main__":
    unittest.main()
