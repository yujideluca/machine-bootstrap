import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class VmProofTest(unittest.TestCase):
    # REQ MB-15
    def test_design_log_records_a_vm_proof_with_a_date_and_a_result(self):
        design = (ROOT / "DESIGN.md").read_text()
        rows = [l for l in design.splitlines() if l.startswith("|") and "VM proof" in l]
        self.assertTrue(rows, "no 'VM proof' row in the DESIGN.md decision log: run tools/vm-test.sh and record it")
        self.assertRegex(rows[0], r"\d{4}-\d{2}-\d{2}")
        self.assertIn("ALL CHECKS PASSED", rows[0])

    # REQ MB-15
    def test_the_vm_assertions_are_valid_python(self):
        compile((ROOT / "tools/vm_assert.py").read_text(), "vm_assert.py", "exec")   # a typo here costs an hour

    # REQ MB-15
    def test_the_harness_and_its_assertions_exist(self):
        self.assertTrue((ROOT / "tools/vm-test.sh").is_file())
        self.assertTrue((ROOT / "tools/vm_assert.py").is_file())
        text = (ROOT / "tools/vm_assert.py").read_text()
        for needed in ("secrets_backup", "data-backup", "second run", "claude --version"):
            self.assertIn(needed, text)


if __name__ == "__main__":
    unittest.main()
