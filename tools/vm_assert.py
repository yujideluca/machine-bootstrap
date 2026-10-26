"""Runs INSIDE the test VM after a restore. Exit 0 only if the restored machine matches state/ (MB-15)."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME = Path.home()
PRIVATE = {"dev/codex-pbar", "dev/project-template"}   # cloning these needs the SSH key from secrets-restore
failures = []


def check(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        failures.append(what)


def sh(cmd):
    env = dict(os.environ, PATH=f"{HOME}/.local/bin:{HOME}/.cargo/bin:{os.environ['PATH']}")
    return subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, env=env)


# 1. every allow-listed home file is on the machine and equal to state/ (the old skeleton .bashrc was backed up)
state_home = ROOT / "state" / "home"
wrong = [str(p.relative_to(state_home)) for p in state_home.rglob("*")
         if p.is_file() and not p.is_symlink() and (HOME / p.relative_to(state_home)).read_bytes() != p.read_bytes()]
check(not wrong, f"all {sum(1 for p in state_home.rglob('*') if p.is_file())} captured home files restored identically {wrong[:3]}")
check(any(HOME.glob(".bashrc.mb-bak-*")), "the pre-existing .bashrc was backed up before being replaced (MB-7)")

# 2. what the second run still wants to do is exactly the private clones
log = Path(sys.argv[1] if len(sys.argv) > 1 else HOME / "second.log")
log = log if log.is_absolute() else HOME / log
todo = [l for l in log.read_text().splitlines() if l.startswith(("[todo]", "[FAIL]"))]
unexpected = [l for l in todo if not any(f"clone {r}" in l for r in PRIVATE)]
check(not unexpected, f"second run has nothing pending except private clones (MB-5) {unexpected[:5]}")

# 3. public repositories were cloned, private ones were not
for rel in ("dev/QuizApp", "dev/wiki", "dev/workflow-memory", "dev/pipeline-check"):
    check((HOME / rel / ".git").is_dir(), f"{rel} cloned (MB-8)")

# 4. packages and tools
# google-chrome-stable and tailscale come from third-party sources: they prove the second pass
CHECKED = ("git", "tmux", "gh", "curl", "flatpak", "google-chrome-stable", "tailscale")
apt = [l for l in (ROOT / "state" / "apt-manual.txt").read_text().split() if l in CHECKED]
for pkg in apt:
    check(sh(f"dpkg -s {pkg} >/dev/null 2>&1").returncode == 0, f"apt package {pkg} installed")
for name, cmd in (("uv", "uv --version"), ("node", "node --version"), ("claude", "claude --version"),
                  ("codex", "codex --version"), ("rust", "cargo --version"), ("elm", "elm --version"),
                  ("jdk", "source ~/dev/env.sh && java -version"), ("gradle", "source ~/dev/env.sh && gradle --version"),
                  ("android sdk", "source ~/dev/env.sh && sdkmanager --list_installed")):
    r = sh(cmd)
    check(r.returncode == 0, f"tool {name} works (MB-13) {r.stderr.strip()[:80]}")

check(sh('test "$(elm --version)" = 0.19.1').returncode == 0, "Elm is the version the wiki needs (0.19.1)")
check((HOME / "dev/wiki/site/index.html").exists() and (HOME / "dev/wiki/server/_build/prod/rel/wiki/bin/wiki").exists(),
      "the wiki server and its site are built")
check(sh("pyright --version").returncode == 0, "pyright works")

# 5. the services are in place
check((HOME / ".config/systemd/user/claude-assistant.service").exists(), "systemd user units restored")
check(sh("loginctl show-user $USER -p Linger | grep -q yes").returncode == 0, "linger enabled (services start without login)")

# 6. the encrypted secrets round trip works with this machine's gpg
sys.path.insert(0, str(ROOT))
from mb import secrets_backup as sb  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    t = Path(tmp)
    (t / "h/.ssh").mkdir(parents=True)
    (t / "h/.ssh/id_test").write_text("fake-key-material\n")
    (t / "d").mkdir()
    archive = sb.create(t / "h", [".ssh"], [t / "d"], "a-test-passphrase")[0]
    (t / "n").mkdir()
    sb.restore(archive, "a-test-passphrase", t / "n")
    check((t / "n/.ssh/id_test").read_text() == "fake-key-material\n"
          and (t / "n/.ssh").stat().st_mode & 0o777 == 0o700, "secrets-backup and secrets-restore round trip (MB-9, MB-10)")

# 7. the unmounted-drive guard works here too
r = subprocess.run([sys.executable, "-m", "mb", "data-backup", "--to", str(HOME)], capture_output=True, text=True, cwd=ROOT)
check(r.returncode != 0 and "not a mounted drive" in r.stderr, "data-backup refuses a target that is not a mounted drive (MB-11)")

print(f"\n{'ALL CHECKS PASSED' if not failures else str(len(failures)) + ' CHECK(S) FAILED'}")
sys.exit(1 if failures else 0)
