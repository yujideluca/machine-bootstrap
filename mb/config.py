"""The allow-lists and recipes, read from mb.toml. Anything not named there is never captured."""
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    home_files: list = field(default_factory=list)
    home_dirs: list = field(default_factory=list)
    etc_portable: list = field(default_factory=list)   # absolute paths that make sense on any machine
    etc_hardware: list = field(default_factory=list)   # absolute paths tied to this machine's hardware
    apt_sources: list = field(default_factory=list)
    skip_globs: list = field(default_factory=list)
    max_file_bytes: int = 1_000_000
    hardware_packages: list = field(default_factory=list)
    never_packages: list = field(default_factory=list)   # boot loader etc.: never installed by restore, on any profile
    repos_root: str = "~/dev"
    tools: list = field(default_factory=list)          # recipes: id, check, install, root
    secrets_paths: list = field(default_factory=list)
    data_dirs: list = field(default_factory=list)
    bulk_dirs: list = field(default_factory=list)
    ssd_uuid: str = ""
    gdrive_path: str = ""

    @property
    def system_files(self):
        return list(self.etc_portable) + list(self.etc_hardware)


def load(path):
    raw = tomllib.loads(Path(path).read_text())
    cap, res = raw.get("capture", {}), raw.get("restore", {})
    sec, data = raw.get("secrets", {}), raw.get("data", {})
    return Config(
        home_files=cap.get("home_files", []),
        home_dirs=cap.get("home_dirs", []),
        etc_portable=cap.get("system_files_portable", []),
        etc_hardware=cap.get("system_files_hardware", []),
        skip_globs=cap.get("skip_globs", []),
        max_file_bytes=cap.get("max_file_bytes", 1_000_000),
        repos_root=cap.get("repos_root", "~/dev"),
        hardware_packages=res.get("hardware_packages", []),
        never_packages=res.get("never_packages", []),
        tools=raw.get("recipe", []),
        secrets_paths=sec.get("paths", []),
        gdrive_path=sec.get("gdrive_path", ""),
        data_dirs=data.get("dirs", []),
        bulk_dirs=data.get("bulk_dirs", []),
        ssd_uuid=data.get("ssd_uuid", ""),
    )
