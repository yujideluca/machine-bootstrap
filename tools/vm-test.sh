#!/usr/bin/env bash
# Proof on a clean machine (MB-15): boots a fresh Ubuntu cloud image in QEMU, copies this repo in, runs
# bootstrap.sh the way a real reinstall would, and checks the result. Nothing touches the real system.
#   tools/vm-test.sh            full run (about 30-60 minutes: it installs the whole desktop)
# Needs: qemu-system-x86_64 with KVM, genisoimage, ssh, the image in ~/.cache/machine-bootstrap-vm (see below).
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$PWD
CACHE=${MB_VM_CACHE:-$HOME/.cache/machine-bootstrap-vm}
IMG=$CACHE/resolute-server-cloudimg-amd64.img
PORT=${MB_VM_PORT:-2222}
EVIDENCE=$ROOT/build/vm-proof/$(date +%Y-%m-%d_%H%M)
WORK=$(mktemp -d "$CACHE/run.XXXXXX")
mkdir -p "$EVIDENCE"

[ -f "$IMG" ] || { echo "missing $IMG: download it from https://cloud-images.ubuntu.com/resolute/current/ and check SHA256SUMS"; exit 2; }
ssh_vm() { ssh -q -i "$WORK/key" -p "$PORT" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -o ServerAliveInterval=30 -o ConnectTimeout=5 tester@127.0.0.1 "$@"; }
# shellcheck disable=SC2329  # called through the EXIT trap
cleanup() {
  ssh_vm 'sudo poweroff' >/dev/null 2>&1 || true
  sleep 5
  [ -f "$WORK/pid" ] && kill "$(cat "$WORK/pid")" 2>/dev/null || true
  cp "$WORK/console.log" "$EVIDENCE/console.log" 2>/dev/null || true
  rm -rf "$WORK"
}
trap cleanup EXIT

ssh-keygen -q -t ed25519 -N "" -f "$WORK/key"
cat > "$WORK/user-data" <<EOT
#cloud-config
users:
  - name: tester
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
    ssh_authorized_keys:
      - $(cat "$WORK/key.pub")
EOT
printf 'instance-id: mb-test\nlocal-hostname: mb-test\n' > "$WORK/meta-data"
genisoimage -quiet -output "$WORK/seed.iso" -volid cidata -joliet -rock "$WORK/user-data" "$WORK/meta-data"
qemu-img create -q -f qcow2 -b "$IMG" -F qcow2 "$WORK/disk.qcow2" 60G

qemu-system-x86_64 -enable-kvm -cpu host -m "${MB_VM_RAM:-6G}" -smp "${MB_VM_CPUS:-6}" \
  -drive file="$WORK/disk.qcow2",if=virtio -drive file="$WORK/seed.iso",if=virtio,format=raw,readonly=on \
  -netdev user,id=n0,hostfwd=tcp:127.0.0.1:"$PORT"-:22 -device virtio-net-pci,netdev=n0 \
  -display none -serial file:"$WORK/console.log" -daemonize -pidfile "$WORK/pid"

echo "waiting for the VM to boot..."
for _ in $(seq 1 90); do ssh_vm true 2>/dev/null && break; sleep 5; done
ssh_vm 'cloud-init status --wait' >/dev/null || true
ssh_vm 'cat /etc/os-release | head -2' | tee "$EVIDENCE/vm-os.txt"

echo "copying the project into the VM..."
tar --exclude=.git --exclude=build --exclude=__pycache__ -c . | ssh_vm 'mkdir -p ~/mb && tar -x -C ~/mb'

run_in_vm() {   # name, command: runs detached so a dropped connection cannot kill an hour of installing
  local name=$1; shift
  ssh_vm "nohup bash -c 'cd ~/mb && $* > ~/$name.log 2>&1; echo \$? > ~/$name.exit' >/dev/null 2>&1 &"
  until ssh_vm "test -f ~/$name.exit" 2>/dev/null; do sleep 20; done
  ssh_vm "cat ~/$name.log" > "$EVIDENCE/$name.log"
  ssh_vm "cat ~/$name.exit"
}

echo "1/4 dry run (must change nothing but prerequisites)"
run_in_vm dryrun './bootstrap.sh'
echo "2/4 apply (public repositories over https: the private ones need the restored SSH key)"
# set through the environment: the restored ~/.gitconfig replaces any git config file written beforehand
GIT_HTTPS='GIT_TERMINAL_PROMPT=0 GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=url.https://github.com/.insteadOf GIT_CONFIG_VALUE_0=git@github.com:'
apply_exit=$(run_in_vm apply "$GIT_HTTPS ./bootstrap.sh --apply --profile new")
echo "apply exit code: $apply_exit"
echo "3/4 second run (idempotence: nothing may be pending except the known private clones)"
run_in_vm second "$GIT_HTTPS python3 -m mb restore --profile new"
echo "4/4 assertions inside the VM"
code=$(run_in_vm assert "python3 tools/vm_assert.py ~/second.log")
cat "$EVIDENCE/assert.log"
echo "evidence saved in $EVIDENCE"
exit "$code"
