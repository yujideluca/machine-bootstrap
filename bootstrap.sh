#!/usr/bin/env bash
# Start here on a fresh Ubuntu/Kubuntu install:
#   git clone https://github.com/yujideluca/machine-bootstrap && cd machine-bootstrap && ./bootstrap.sh
# Installs what `mb` itself needs, then shows the restore plan. Add --apply to really do it.
#   ./bootstrap.sh                     dry run, changes nothing except the prerequisites
#   ./bootstrap.sh --apply             restore this machine's setup
#   ./bootstrap.sh --apply --profile new   skip drivers/kernels tied to the old laptop
set -euo pipefail
cd "$(dirname "$0")"

missing=()
for tool in git python3 rclone rsync gpg curl; do
  command -v "$tool" >/dev/null 2>&1 || missing+=("$tool")
done
if [ "${#missing[@]}" -gt 0 ]; then
  echo "Installing prerequisites: ${missing[*]}"
  sudo apt-get update
  sudo apt-get install -y "${missing[@]/gpg/gnupg}"
fi

exec python3 -m mb restore "$@"
