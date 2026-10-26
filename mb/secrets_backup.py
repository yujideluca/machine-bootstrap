"""Encrypted backup of keys and logins. The passphrase is typed by Giovanni and never stored or put on a command line."""
import hashlib
import io
import os
import shutil
import subprocess
import tarfile
import time
from pathlib import Path, PurePosixPath


class SecretsError(Exception):
    pass


class Written(list):
    """The archive paths written; .missing lists configured paths that did not exist."""
    missing = ()


def safe_member(name):
    p = PurePosixPath(name)
    return bool(name) and not p.is_absolute() and ".." not in p.parts


def _gpg(args, data, passphrase):
    r_fd, w_fd = os.pipe()
    os.write(w_fd, passphrase.encode() + b"\n")
    os.close(w_fd)
    try:
        proc = subprocess.run(
            ["gpg", "--batch", "--yes", "--quiet", "--pinentry-mode", "loopback", "--passphrase-fd", str(r_fd), *args],
            input=data, capture_output=True, pass_fds=(r_fd,))
    finally:
        os.close(r_fd)
    if proc.returncode != 0:
        raise SecretsError("gpg failed (wrong passphrase or damaged file): " + proc.stderr.decode(errors="replace").strip())
    return proc.stdout


def _tar_bytes(home, paths):
    buf, missing = io.BytesIO(), []
    with tarfile.open(fileobj=buf, mode="w") as tar:
        for rel in paths:
            if os.path.lexists(home / rel):
                tar.add(home / rel, arcname=rel)
            else:
                missing.append(rel)
    return buf.getvalue(), missing


def _decrypt(archive, passphrase):
    return _gpg(["--decrypt", str(archive)], None, passphrase)


def list_members(archive, passphrase):
    with tarfile.open(fileobj=io.BytesIO(_decrypt(archive, passphrase))) as tar:
        return [m.name for m in tar.getmembers()]


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _verify(archive, passphrase, home, tar_names):
    """Decrypt again and compare every file with the original, so a bad backup is found now, not on the day it is needed."""
    with tarfile.open(fileobj=io.BytesIO(_decrypt(archive, passphrase))) as tar:
        members = tar.getmembers()
        if sorted(m.name for m in members) != sorted(tar_names):
            raise SecretsError("verification failed: the archive does not list the files that were saved")
        for m in members:
            if m.isfile() and tar.extractfile(m).read() != (home / m.name).read_bytes():
                raise SecretsError(f"verification failed: {m.name} differs from the original")


def create(home, paths, dests, passphrase, now=lambda: time.strftime("%Y%m%d-%H%M%S")):
    home = Path(home)
    dests = [Path(d) for d in dests]
    if not dests:
        raise SecretsError("no target given")
    for d in dests:
        if not d.is_dir():
            raise SecretsError(f"target folder does not exist: {d}")
    if len(passphrase) < 12:
        raise SecretsError("passphrase must have at least 12 characters")
    data, missing = _tar_bytes(home, paths)
    tar_names = [m.name for m in tarfile.open(fileobj=io.BytesIO(data)).getmembers()]
    sealed = _gpg(["--symmetric", "--cipher-algo", "AES256", "--s2k-mode", "3", "--s2k-count", "65011712",
                   "--s2k-digest-algo", "SHA512", "--compress-algo", "none", "--output", "-"], data, passphrase)
    name = f"mb-secrets-{now()}.tar.gpg"
    out = Written()
    for d in dests:
        partial = d / (name + ".partial")
        partial.write_bytes(sealed)
        os.replace(partial, d / name)
        out.append(d / name)
    _verify(out[0], passphrase, home, tar_names)
    for other in out[1:]:
        if _sha(other) != _sha(out[0]):
            raise SecretsError(f"copy differs from the first archive: {other}")
    out.missing = missing
    return out


def restore(archive, passphrase, home, force=False, now=lambda: time.strftime("%Y%m%d-%H%M%S")):
    home = Path(home)
    with tarfile.open(fileobj=io.BytesIO(_decrypt(archive, passphrase))) as tar:
        members = tar.getmembers()
        for m in members:
            if not safe_member(m.name) or not (m.isfile() or m.isdir()):
                raise SecretsError(f"unsafe entry in archive: {m.name}")
        clash = [m.name for m in members if m.isfile() and os.path.lexists(home / m.name)]
        if clash and not force:
            raise SecretsError("would overwrite existing files (use --force to keep .mb-bak copies): " + ", ".join(clash))
        for m in members:
            target = home / m.name
            if m.isdir():
                target.mkdir(parents=True, exist_ok=True)
                target.chmod(m.mode & 0o700 or 0o700)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if os.path.lexists(target):
                os.rename(target, f"{target}.mb-bak-{now()}")
            target.write_bytes(tar.extractfile(m).read())
            target.chmod(m.mode & 0o700)
        for top in {PurePosixPath(m.name).parts[0] for m in members}:
            if top in (".ssh", ".gnupg") and (home / top).is_dir():
                (home / top).chmod(0o700)
    return [m.name for m in members]
