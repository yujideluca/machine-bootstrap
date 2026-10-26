---
name: remote-assistant-setup
description: "Always-on Claude Code \"personal assistant\" reachable from Giovanni's phone via Remote Control (systemd + tmux), set up 2026-10-10"
metadata:
  node_type: memory
  type: project
  originSessionId: beb08a2d-6b55-4403-a993-859115130f45
  modified: 2026-10-11T01:20:09.379Z
---

Since 2026-10-10 the laptop runs `claude-assistant.service` (systemd user unit, enabled, linger on) which starts `~/.local/bin/claude-assistant start`: a dedicated tmux server (socket `claude`, session `assistant`) running `claude remote-control --name "$(hostname)-assistant" --permission-mode bypassPermissions` in a restart loop, home folder `~/assistant` (own CLAUDE.md: short phone-friendly replies). Shows in the app as `yuji-nitro-assistant`; Giovanni confirmed it works from his phone.

tmux is a user-space install (no sudo): wrapper `~/.local/bin/tmux` + `~/.local/lib/tmux/` (Ubuntu noble 3.4 package and its libs extracted). Replace with `sudo apt install tmux` and delete those two paths if a system install is wanted.

Boot race (2026-10-11): it starts before Wi-Fi, so the run loop now waits for DNS (`getent hosts api.anthropic.com`) before each launch; claude-daily.service likewise waits via ExecStartPre (tools/install.sh, C-0006).

Visible window (2026-10-11): KDE autostart `~/.config/autostart/claude-assistant-window.desktop` opens Konsole running `claude-assistant window` (waits for the session, then attaches). Closing the window only detaches; delete that file to stop it.

**Why:** Giovanni wanted to reach Claude Code from the Claude app when away from the laptop.
**How to apply:** for problems with remote access, check `systemctl --user status claude-assistant` and `tmux -L claude capture-pane -p -t assistant`. bypassPermissions was set by Giovanni himself (the auto-mode classifier blocked Claude from doing it); don't change the mode without asking.
