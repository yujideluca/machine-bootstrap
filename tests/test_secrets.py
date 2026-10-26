import os
import shutil
import tempfile
import unittest
from pathlib import Path

from mb import secrets_backup as sb


PW = "test-passphrase-123"


@unittest.skipUnless(shutil.which("gpg"), "gpg not installed")
class SecretsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        (self.home / ".ssh").mkdir(parents=True)
        (self.home / ".ssh/id_ed25519").write_text("PRIVATE-KEY-BODY-123\n")
        (self.home / ".ssh/id_ed25519").chmod(0o600)
        (self.home / ".config/gh").mkdir(parents=True)
        (self.home / ".config/gh/hosts.yml").write_text("oauth_token: zzz-secret-token\n")
        self.dest = self.root / "dest"
        self.dest.mkdir()
        self.gnupg = self.root / "gnupghome"
        self.gnupg.mkdir(mode=0o700)
        os.environ["GNUPGHOME"] = str(self.gnupg)
        self.addCleanup(os.environ.pop, "GNUPGHOME", None)

    paths = [".ssh", ".config/gh", ".missing-thing"]

    # REQ MB-9
    def test_archive_is_encrypted_and_round_trips(self):
        out = sb.create(self.home, self.paths, [self.dest], PW)
        archive = out[0]
        raw = archive.read_bytes()
        self.assertNotIn(b"PRIVATE-KEY-BODY", raw)
        self.assertNotIn(b"zzz-secret-token", raw)
        self.assertFalse(list(self.dest.glob("*.tar")), "no plaintext archive may be left behind")
        names = sb.list_members(archive, PW)
        self.assertIn(".ssh/id_ed25519", names)
        self.assertIn(".config/gh/hosts.yml", names)

    # REQ MB-9
    def test_missing_paths_are_reported_not_fatal(self):
        out = sb.create(self.home, self.paths, [self.dest], PW)
        self.assertEqual(out.missing, [".missing-thing"])
        self.assertTrue(out[0].exists())

    # REQ MB-9
    def test_wrong_passphrase_fails_and_target_must_exist(self):
        archive = sb.create(self.home, self.paths, [self.dest], PW)[0]
        with self.assertRaises(sb.SecretsError):
            sb.list_members(archive, "a-wrong-passphrase")
        with self.assertRaises(sb.SecretsError):
            sb.create(self.home, self.paths, [self.root / "no-such-dir"], PW)

    # REQ MB-9
    def test_short_passphrase_is_refused(self):
        with self.assertRaises(sb.SecretsError):
            sb.create(self.home, self.paths, [self.dest], "short")
        self.assertEqual(list(self.dest.iterdir()), [])

    # REQ MB-9
    def test_copies_are_identical_in_every_target(self):
        d2 = self.root / "dest2"
        d2.mkdir()
        a, b = sb.create(self.home, self.paths, [self.dest, d2], PW)
        self.assertEqual(a.read_bytes(), b.read_bytes())

    # REQ MB-10
    def test_restore_sets_owner_only_permissions(self):
        archive = sb.create(self.home, self.paths, [self.dest], PW)[0]
        new_home = self.root / "newhome"
        new_home.mkdir()
        sb.restore(archive, PW, new_home)
        self.assertEqual((new_home / ".ssh").stat().st_mode & 0o777, 0o700)
        self.assertEqual((new_home / ".ssh/id_ed25519").stat().st_mode & 0o777, 0o600)
        self.assertEqual((new_home / ".ssh/id_ed25519").read_text(), "PRIVATE-KEY-BODY-123\n")
        self.assertEqual((new_home / ".config/gh/hosts.yml").stat().st_mode & 0o077, 0)

    # REQ MB-10
    def test_restore_refuses_to_overwrite_unless_asked(self):
        archive = sb.create(self.home, self.paths, [self.dest], PW)[0]
        new_home = self.root / "newhome"
        (new_home / ".ssh").mkdir(parents=True)
        (new_home / ".ssh/id_ed25519").write_text("existing\n")
        with self.assertRaises(sb.SecretsError):
            sb.restore(archive, PW, new_home)
        self.assertEqual((new_home / ".ssh/id_ed25519").read_text(), "existing\n")
        sb.restore(archive, PW, new_home, force=True)
        self.assertEqual((new_home / ".ssh/id_ed25519").read_text(), "PRIVATE-KEY-BODY-123\n")
        self.assertTrue(list((new_home / ".ssh").glob("id_ed25519.mb-bak-*")))

    # REQ MB-10
    def test_unsafe_member_names_are_rejected(self):
        self.assertFalse(sb.safe_member("../evil"))
        self.assertFalse(sb.safe_member("/etc/passwd"))
        self.assertTrue(sb.safe_member(".ssh/id_ed25519"))


if __name__ == "__main__":
    unittest.main()
