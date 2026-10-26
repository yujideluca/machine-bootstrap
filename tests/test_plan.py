import tempfile
import unittest
from pathlib import Path

from mb.config import Config
from mb.plan import apply_plan, build_plan, execute, step_env
from tests.fakes import FakeFacts


def forbidden(step):
    raise AssertionError(f"this test must not run a command: {step.title}")


def cfg(**over):
    base = dict(
        home_files=[], home_dirs=[], etc_portable=["/etc/portable.conf"], etc_hardware=["/etc/hw.conf"],
        apt_sources=[], skip_globs=[], max_file_bytes=10**6, hardware_packages=["nvidia-*", "linux-*"], never_packages=[],
        repos_root="~/dev", tools=[],
    )
    base.update(over)
    return Config(**base)


class PlanTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.state = self.root / "state"
        (self.state / "home").mkdir(parents=True)
        (self.state / "etc/etc").mkdir(parents=True)

    def write_state(self, rel, text):
        p = self.state / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def plan(self, facts, profile="same", config=None):
        return build_plan(facts, config or cfg(), self.state, profile=profile)

    # REQ MB-4
    def test_dry_run_changes_nothing(self):
        self.write_state("apt-manual.txt", "git\n")
        self.write_state("home/.bashrc", "new\n")
        f = FakeFacts(self.home, apt=[])
        steps = self.plan(f)
        ran = []
        execute(steps, apply=False, runner=lambda s: ran.append(s.id), log=lambda m: None)
        self.assertEqual(ran, [])
        self.assertFalse((self.home / ".bashrc").exists())

    # REQ MB-5
    def test_done_steps_are_not_run_again(self):
        self.write_state("apt-manual.txt", "git\ncurl\n")
        f = FakeFacts(self.home, apt=["git", "curl"])
        steps = self.plan(f)
        self.assertFalse([s for s in steps if s.kind == "apt" and not s.done])

    # REQ MB-5
    def test_only_missing_packages_are_installed(self):
        self.write_state("apt-manual.txt", "git\ncurl\n")
        f = FakeFacts(self.home, apt=["git"])
        (apt,) = [s for s in self.plan(f) if s.kind == "apt"]
        self.assertFalse(apt.done)
        self.assertEqual(apt.argv[-1:], ["curl"])

    # REQ MB-5
    def test_packages_missing_in_the_repository_are_reported_not_fatal(self):
        self.write_state("apt-manual.txt", "git\nghostpkg\n")
        f = FakeFacts(self.home, apt=[], apt_available=["git"])
        steps = self.plan(f)
        (apt,) = [s for s in steps if s.kind == "apt"]
        self.assertEqual(apt.argv[-1:], ["git"])
        self.assertTrue(any("ghostpkg" in s.title for s in steps if s.kind == "note"))

    # REQ MB-6
    def test_root_only_where_needed(self):
        self.write_state("apt-manual.txt", "git\n")
        self.write_state("home/.bashrc", "x\n")
        self.write_state("repos.txt", "dev/app\tgit@github.com:u/app.git\n")
        steps = self.plan(FakeFacts(self.home))
        by_kind = {s.kind: s.root for s in steps if not s.done}
        self.assertTrue(by_kind["apt"])
        self.assertFalse(by_kind["file"])
        self.assertFalse(by_kind["clone"])

    # REQ MB-7
    def test_differing_file_is_backed_up_first(self):
        self.write_state("home/.bashrc", "from state\n")
        target = self.home / ".bashrc"
        target.write_text("local edit\n")
        f = FakeFacts(self.home, files={str(target): b"local edit\n"})
        steps = self.plan(f)
        execute(steps, apply=True, runner=forbidden, log=lambda m: None, now=lambda: "T1")
        self.assertEqual(target.read_text(), "from state\n")
        self.assertEqual((self.home / ".bashrc.mb-bak-T1").read_text(), "local edit\n")

    # REQ MB-7
    def test_identical_file_is_done_and_left_alone(self):
        self.write_state("home/.bashrc", "same\n")
        target = self.home / ".bashrc"
        target.write_text("same\n")
        f = FakeFacts(self.home, files={str(target): b"same\n"})
        (step,) = [s for s in self.plan(f) if s.kind == "file"]
        self.assertTrue(step.done)

    # REQ MB-5
    def test_applying_twice_second_run_has_nothing_pending(self):
        self.write_state("home/.config/x.conf", "a\n")
        f = FakeFacts(self.home)
        execute(self.plan(f), apply=True, runner=forbidden, log=lambda m: None)
        f.files[str(self.home / ".config/x.conf")] = (self.home / ".config/x.conf").read_bytes()
        again = [s for s in self.plan(f) if s.kind == "file" and not s.done]
        self.assertEqual(again, [])

    # REQ MB-8
    def test_missing_repos_are_cloned_existing_left(self):
        self.write_state("repos.txt", "dev/a\tgit@github.com:u/a.git\ndev/b\tgit@github.com:u/b.git\n")
        (self.home / "dev/a").mkdir(parents=True)
        f = FakeFacts(self.home, files={str(self.home / "dev/a/.git"): b""})
        clones = {s.title: s for s in self.plan(f) if s.kind == "clone"}
        done = {t.split()[-1]: s.done for t, s in clones.items()}
        self.assertTrue(done["dev/a"])
        self.assertFalse(done["dev/b"])
        (b,) = [s for s in clones.values() if not s.done]
        self.assertEqual(b.argv, ["git", "clone", "git@github.com:u/b.git", str(self.home / "dev/b")])

    # REQ MB-13
    def test_tool_recipe_runs_only_when_check_fails(self):
        recipes = cfg(tools=[{"id": "uv", "check": "uv --version", "install": "curl uv"}])
        f = FakeFacts(self.home, checks={"uv --version": False})
        (tool,) = [s for s in self.plan(f, config=recipes) if s.kind == "tool"]
        self.assertFalse(tool.done)
        self.assertEqual(tool.argv, ["bash", "-c", "curl uv"])
        f2 = FakeFacts(self.home, checks={"uv --version": True})
        (tool2,) = [s for s in self.plan(f2, config=recipes) if s.kind == "tool"]
        self.assertTrue(tool2.done)

    # REQ MB-13
    def test_early_recipes_run_before_snaps_and_flatpaks(self):
        self.write_state("flatpak.txt", "org.a\n")
        recipes = cfg(tools=[{"id": "late", "check": "x", "install": "x"},
                             {"id": "flathub", "check": "y", "install": "y", "stage": "after-apt"}])
        kinds = [(s.kind, s.title) for s in self.plan(FakeFacts(self.home), config=recipes)]
        order = [t for _, t in kinds]
        self.assertLess(order.index("tool flathub"), order.index("flatpak install org.a"))
        self.assertLess(order.index("flatpak install org.a"), order.index("tool late"))

    # REQ MB-5
    def test_settings_are_written_after_the_tool_installers_that_edit_them(self):
        self.write_state("home/.bashrc", "x\n")
        self.write_state("repos.txt", "dev/a\tgit@github.com:u/a.git\n")
        recipes = cfg(tools=[{"id": "uv", "check": "x", "install": "x"}])
        order = [s.kind for s in self.plan(FakeFacts(self.home), config=recipes)]
        self.assertLess(order.index("clone"), order.index("tool"))
        self.assertLess(order.index("tool"), order.index("file"))

    # REQ MB-5
    def test_packages_from_new_apt_sources_are_installed_in_a_second_pass(self):
        self.write_state("apt-manual.txt", "git\nchrome\n")
        self.write_state("etc/etc/apt/sources.list.d/chrome.sources", "deb x\n")
        f = FakeFacts(self.home, apt=["git"], apt_available=[])
        installed = []

        def runner(step):
            if step.title == "apt-get update":
                f._avail = {"chrome"}          # the new source makes the package visible
            if step.kind == "apt":
                installed.append(step.argv[-1])
            return 0

        steps = self.plan(f)
        self.assertTrue(any("will be retried" in s.title for s in steps if s.kind == "note"))
        result = apply_plan(f, cfg(), self.state, "same", runner, log=lambda m: None)
        self.assertTrue(result.ok)
        self.assertEqual(installed, ["chrome"])

    # REQ MB-13
    def test_recipes_run_with_the_user_bin_folders_on_the_path(self):
        env = step_env(self.home, {"PATH": "/usr/bin"})
        self.assertEqual(env["PATH"].split(":")[:2], [str(self.home / ".local/bin"), str(self.home / ".cargo/bin")])
        self.assertTrue(env["PATH"].endswith("/usr/bin"))

    # REQ MB-6
    def test_hardware_items_are_skipped_on_a_new_machine(self):
        self.write_state("apt-manual.txt", "git\nnvidia-driver-580\nlinux-image-generic\n")
        self.write_state("etc/etc/hw.conf", "hw\n")
        self.write_state("etc/etc/portable.conf", "p\n")
        f = FakeFacts(self.home)
        same = self.plan(f, profile="same")
        new = self.plan(f, profile="new")
        (apt_same,) = [s for s in same if s.kind == "apt"]
        (apt_new,) = [s for s in new if s.kind == "apt"]
        self.assertIn("nvidia-driver-580", apt_same.argv)
        self.assertNotIn("nvidia-driver-580", apt_new.argv)
        etc_new = [s.title for s in new if s.kind == "file"]
        self.assertTrue(any("portable.conf" in t for t in etc_new))
        self.assertFalse(any("hw.conf" in t for t in etc_new))

    # REQ MB-6
    def test_boot_loader_packages_are_never_installed_on_any_profile(self):
        self.write_state("apt-manual.txt", "git\ngrub-pc\ngrub-efi-amd64-signed\nshim-signed\n")
        config = cfg(never_packages=["grub*", "shim*"])
        for profile in ("same", "new"):
            (apt,) = [s for s in self.plan(FakeFacts(self.home), profile=profile, config=config) if s.kind == "apt"]
            self.assertEqual(apt.argv[-1:], ["git"], profile)
        notes = [s.title for s in self.plan(FakeFacts(self.home), config=config) if s.kind == "note"]
        self.assertEqual(len(notes), 3)

    # REQ MB-6
    def test_run_failure_stops_before_later_steps(self):
        self.write_state("apt-manual.txt", "git\n")
        self.write_state("home/.bashrc", "x\n")
        steps = self.plan(FakeFacts(self.home))
        seen = []

        def runner(step):
            seen.append(step.kind)
            return 1 if step.kind == "apt" else 0

        result = execute(steps, apply=True, runner=runner, log=lambda m: None, keep_going=False)
        self.assertFalse(result.ok)
        self.assertEqual(seen, ["apt"])

    # REQ MB-5
    def test_failed_step_is_reported_and_others_still_run_with_keep_going(self):
        self.write_state("apt-manual.txt", "git\n")
        self.write_state("home/.bashrc", "x\n")
        steps = self.plan(FakeFacts(self.home))
        result = execute(steps, apply=True, runner=lambda s: 1 if s.kind == "apt" else 0,
                         log=lambda m: None, keep_going=True)
        self.assertEqual([s.kind for s in result.failed], ["apt"])
        self.assertEqual((self.home / ".bashrc").read_text(), "x\n")


if __name__ == "__main__":
    unittest.main()
