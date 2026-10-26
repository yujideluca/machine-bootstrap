import unittest
from pathlib import Path

from mb import config

ROOT = Path(__file__).resolve().parent.parent


class ConfigFileTest(unittest.TestCase):
    def setUp(self):
        self.cfg = config.load(ROOT / "mb.toml")

    # REQ MB-13
    def test_every_recipe_has_an_id_a_check_and_an_install_and_ids_are_unique(self):
        ids = [r["id"] for r in self.cfg.tools]
        self.assertEqual(len(ids), len(set(ids)))
        for r in self.cfg.tools:
            self.assertTrue(r.get("check") and r.get("install"), r["id"])

    # REQ MB-13
    def test_elm_is_pinned_to_the_version_the_wiki_needs(self):
        (elm,) = [r for r in self.cfg.tools if r["id"] == "node-global-tools"]
        self.assertIn("elm@0.19.1-6", elm["install"])
        self.assertIn("0.19.1", elm["check"])

    # REQ MB-13
    def test_wiki_recipe_is_done_only_when_the_site_is_built_too(self):
        (wiki,) = [r for r in self.cfg.tools if r["id"] == "wiki"]
        self.assertIn("site/index.html", wiki["check"])

    # REQ MB-6
    def test_the_boot_loader_is_on_the_never_list(self):
        for name in ("grub-pc", "grub-efi-amd64-signed", "shim-signed", "efibootmgr"):
            self.assertTrue(any(__import__("fnmatch").fnmatch(name, g) for g in self.cfg.never_packages), name)

    # REQ MB-3
    def test_no_secret_path_is_also_in_the_capture_allow_list(self):
        captured = set(self.cfg.home_files) | set(self.cfg.home_dirs)
        self.assertEqual(captured & set(self.cfg.secrets_paths), set())


if __name__ == "__main__":
    unittest.main()
