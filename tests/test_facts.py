import unittest

from mb import facts


class RealFactsOnABareSystemTest(unittest.TestCase):
    # REQ MB-14
    def test_a_missing_command_means_nothing_installed_not_a_crash(self):
        self.assertEqual(facts._out(["definitely-not-an-installed-command-xyz"]), "")

    # REQ MB-14
    def test_missing_snap_and_flatpak_give_empty_sets(self):
        real = facts.RealFacts()
        original = facts._out
        facts._out = lambda argv: original(["definitely-not-an-installed-command-xyz"])
        self.addCleanup(setattr, facts, "_out", original)
        self.assertEqual(real.snaps(), set())
        self.assertEqual(real.flatpaks(), set())
        self.assertEqual(real.apt_available(["git"]), set())


if __name__ == "__main__":
    unittest.main()
