import tempfile
import unittest
from pathlib import Path

from mb import databackup as db


class DataBackupTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        (self.home / "Documents").mkdir(parents=True)
        (self.home / "Documents/a.txt").write_text("hello")
        self.target = self.root / "ssd"
        self.target.mkdir()

    # REQ MB-11
    def test_refuses_a_target_that_is_not_a_mount_point(self):
        with self.assertRaises(db.DataBackupError) as cm:
            db.preflight(self.home, ["Documents"], self.target, is_mount=lambda p: False, free=lambda p: 10**12)
        self.assertIn("not a mounted", str(cm.exception))

    # REQ MB-11
    def test_refuses_when_free_space_is_too_small(self):
        with self.assertRaises(db.DataBackupError) as cm:
            db.preflight(self.home, ["Documents"], self.target, is_mount=lambda p: True, free=lambda p: 1)
        self.assertIn("space", str(cm.exception))

    # REQ MB-11
    def test_passes_with_room_and_a_mount(self):
        need = db.preflight(self.home, ["Documents"], self.target, is_mount=lambda p: True, free=lambda p: 10**9)
        self.assertGreaterEqual(need, 5)

    # REQ MB-11
    def test_rsync_command_never_deletes(self):
        argv = db.rsync_argv(self.home / "Documents", self.target / "machine-bootstrap/home")
        self.assertFalse([a for a in argv if a.startswith("--delete")])
        self.assertIn("--archive", argv)

    # REQ MB-11
    def test_destination_keeps_the_full_relative_path(self):
        (self.home / "dev/quiz-backups").mkdir(parents=True)
        self.assertEqual(db.dest_for(self.home, self.home / "dev/quiz-backups", self.target),
                         self.target / "machine-bootstrap/home/dev/quiz-backups")

    # REQ MB-11
    def test_verify_compares_by_checksum_and_changes_nothing(self):
        argv = db.verify_argv(self.home / "Documents", self.target / "x")
        self.assertIn("--dry-run", argv)
        self.assertIn("--checksum", argv)
        self.assertFalse([a for a in argv if a.startswith("--delete")])

    # REQ MB-11
    def test_missing_source_dirs_are_skipped_with_a_note(self):
        notes = []
        srcs = db.existing_sources(self.home, ["Documents", "Nope"], notes.append)
        self.assertEqual([p.name for p in srcs], ["Documents"])
        self.assertTrue(any("Nope" in n for n in notes))


if __name__ == "__main__":
    unittest.main()
