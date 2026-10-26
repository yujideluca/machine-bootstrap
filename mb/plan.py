"""Turn state/ into an ordered list of steps, and run them. Building the plan changes nothing."""
import fnmatch
import os
import shlex
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Step:
    kind: str                 # apt, file, snap, flatpak, clone, tool, cmd, note
    title: str
    root: bool = False
    done: bool = False
    argv: list = field(default_factory=list)
    src: Path = None          # file steps run by Python: the state file
    dst: Path = None


@dataclass
class Result:
    ok: bool = True
    ran: list = field(default_factory=list)
    failed: list = field(default_factory=list)


def _lines(path):
    return [l for l in Path(path).read_text().splitlines() if l.strip()] if Path(path).exists() else []


def _matches(name, globs):
    return any(fnmatch.fnmatch(name, g) for g in globs)


def _is_hardware_pkg(name, config):
    return _matches(name, config.hardware_packages)


def _file_steps(facts, config, state, profile, ts):
    steps = []
    system = []
    etc_root = Path(state) / "etc"
    if etc_root.is_dir():
        for p in sorted(etc_root.rglob("*")):
            if p.is_file() or p.is_symlink():
                dst = Path("/") / p.relative_to(etc_root)
                if profile == "new" and str(dst) in config.etc_hardware:
                    continue
                system.append((p, dst, True))
    home_root = Path(state) / "home"
    user = []
    if home_root.is_dir():
        for p in sorted(home_root.rglob("*")):
            if p.is_file() or p.is_symlink():
                user.append((p, facts.home / p.relative_to(home_root), False))
    for src, dst, root in system + user:
        if src.is_symlink():
            done = facts.readlink(dst) == os.readlink(src)
        else:
            current = facts.read(dst)
            done = current is not None and current == src.read_bytes()
        shown = f"~/{dst.relative_to(facts.home)}" if not root else str(dst)
        step = Step("file", f"put {shown}", root=root, done=done, src=src, dst=dst)
        if root and not done:
            q = shlex.quote
            step.argv = ["sudo", "bash", "-c",
                         f"if [ -e {q(str(dst))} ] && ! cmp -s {q(str(src))} {q(str(dst))}; "
                         f"then cp -a {q(str(dst))} {q(str(dst))}.mb-bak-{ts}; fi; "
                         f"install -D -m {'644' if not os.access(src, os.X_OK) else '755'} {q(str(src))} {q(str(dst))}"]
        steps.append(step)
    return steps


def _recipe_steps(facts, config, early):
    """Recipes marked stage = "after-apt" run before snaps and flatpaks (they may add the store they need)."""
    return [Step("tool", f"tool {r['id']}", root=r.get("root", False), done=facts.check(r["check"]),
                 argv=["bash", "-c", r["install"]])
            for r in config.tools if (r.get("stage") == "after-apt") == early]


def build_plan(facts, config, state, profile="same"):
    state = Path(state)
    steps = []
    ts = time.strftime("%Y%m%d-%H%M%S")
    file_steps = _file_steps(facts, config, state, profile, ts)
    # package sources and keys first: apt needs them before it can find some packages
    sources = [s for s in file_steps if s.root and ("/apt/" in str(s.dst) or "/keyrings/" in str(s.dst))]
    steps += sources
    if any(not s.done for s in sources):
        steps.append(Step("cmd", "apt-get update", root=True, argv=["sudo", "apt-get", "update"]))

    wanted = _lines(state / "apt-manual.txt")
    for name in sorted(w for w in wanted if _matches(w, config.never_packages)):
        steps.append(Step("note", f"apt package skipped on purpose (the installer owns it): {name}", done=True))
    wanted = [w for w in wanted if not _matches(w, config.never_packages)]
    if profile == "new":
        wanted = [w for w in wanted if not _is_hardware_pkg(w, config)]
    installed = facts.apt_installed()
    missing = sorted(set(wanted) - installed)
    # a name the repositories no longer carry must not stop the others from installing
    available = facts.apt_available(missing) if missing else set()
    sources_pending = any(not s.done for s in sources)
    for name in sorted(set(missing) - available):
        why = ("not available yet, will be retried after the new apt sources are added"
               if sources_pending else "not available on this system, skipped")
        steps.append(Step("note", f"apt package {why}: {name}", done=True))
    todo = sorted(available)
    steps.append(Step("apt", f"apt install {len(todo)} package(s)" if todo else "apt packages", root=True,
                      done=not todo, argv=["sudo", "env", "DEBIAN_FRONTEND=noninteractive", "apt-get", "install", "-y", *todo] if todo else []))

    steps += _recipe_steps(facts, config, early=True)

    have_snaps = {s.split()[0] for s in facts.snaps()}
    for line in _lines(state / "snap.txt"):
        name, *flags = line.split()
        argv = ["sudo", "snap", "install", *(["--classic"] if "classic" in flags else []), name]
        steps.append(Step("snap", f"snap install {name}", root=True, done=name in have_snaps, argv=argv))
    have_flat = facts.flatpaks()
    for app in _lines(state / "flatpak.txt"):
        steps.append(Step("flatpak", f"flatpak install {app}", root=True, done=app in have_flat,
                          argv=["sudo", "flatpak", "install", "-y", "--noninteractive", "flathub", app]))

    for line in _lines(state / "repos.txt"):
        rel, url = line.split("\t")
        dst = facts.home / rel
        steps.append(Step("clone", f"clone {rel}", done=facts.exists(dst / ".git"),
                          argv=["git", "clone", url, str(dst)]))

    steps += _recipe_steps(facts, config, early=False)
    # settings last: installers (uv, rustup, claude) append to .bashrc/.profile, and the record must win
    user_files = [s for s in file_steps if s not in sources]
    steps += user_files
    if any(not s.done and ".config/systemd/user" in str(s.dst) for s in user_files):
        steps.append(Step("cmd", "systemctl --user daemon-reload", argv=["systemctl", "--user", "daemon-reload"]))
    return steps


def say(message):
    print(message, flush=True)   # flushed, so our lines and the installers' output stay in order in a log file


def step_env(home, base=None):
    """Environment for recipes: the user's own bin folders first, as a login shell would have them."""
    env = dict(os.environ if base is None else base)
    env["PATH"] = f"{home}/.local/bin:{home}/.cargo/bin:{env.get('PATH', '')}"
    return env


def run_step(step):
    return subprocess.run(step.argv, env=step_env(Path.home())).returncode


def apply_plan(facts, config, state, profile, runner, log=say, keep_going=True):
    """Build and run the plan. After new apt sources were added, build it again: packages from them are visible now."""
    result = execute(build_plan(facts, config, state, profile), True, runner, log, keep_going)
    if any(s.title == "apt-get update" for s in result.ran):
        log("-- second pass: the new apt sources are in place")
        second = execute(build_plan(facts, config, state, profile), True, runner, log, keep_going)
        result = Result(ok=second.ok, ran=result.ran + second.ran, failed=second.failed)
    return result


def _put_file(step, now):
    step.dst.parent.mkdir(parents=True, exist_ok=True)
    if os.path.lexists(step.dst):
        os.rename(step.dst, f"{step.dst}.mb-bak-{now()}")
    if step.src.is_symlink():
        step.dst.symlink_to(os.readlink(step.src))
    else:
        shutil.copy2(step.src, step.dst)


def execute(steps, apply, runner, log=say, keep_going=True, now=lambda: time.strftime("%Y%m%d-%H%M%S")):
    """runner(step) -> exit code is required: only the CLI passes the real one (run_step), tests pass fakes."""
    result = Result()
    for step in steps:
        if step.done:
            log(f"[done]  {step.title}")
            continue
        if not apply:
            log(f"[todo]  {step.title}{'  (needs root)' if step.root else ''}")
            continue
        log(f"[run]   {step.title}")
        if step.kind == "file" and not step.root:
            _put_file(step, now)
            code = 0
        else:
            if step.kind == "clone":
                Path(step.argv[-1]).parent.mkdir(parents=True, exist_ok=True)
            code = runner(step)
        if code == 0:
            result.ran.append(step)
        else:
            result.failed.append(step)
            result.ok = False
            log(f"[FAIL]  {step.title} (exit {code})")
            if not keep_going:
                break
    return result
