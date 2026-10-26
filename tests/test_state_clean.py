import unittest
from pathlib import Path

from mb.scan import find_secrets

STATE = Path(__file__).resolve().parent.parent / "state"


class StateIsCleanTest(unittest.TestCase):
    # REQ MB-3
    def test_no_secret_material_in_state(self):
        bad = []
        for p in STATE.rglob("*"):
            if p.is_file() and not p.is_symlink():
                hits = find_secrets(p.read_text(errors="replace"))
                if hits:
                    bad.append(f"{p.relative_to(STATE)}: {hits}")
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
