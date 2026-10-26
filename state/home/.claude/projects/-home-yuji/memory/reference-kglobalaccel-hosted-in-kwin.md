---
name: reference-kglobalaccel-hosted-in-kwin
description: On this laptop (Plasma 6.6 Wayland) the global-shortcut DBus service lives inside kwin_wayland; a malformed DBus call crashes the compositor
metadata:
  type: reference
---

`org.kde.kglobalaccel` is served by `kwin_wayland` itself (KGLOBALACCELD_PLATFORM=org.kde.kwin), not by a separate daemon. On 2026-10-24 a `globalShortcutsByKey` call with a wrong argument shape SIGABRTed kwin_wayland; the wrapper restarted it.

**Why:** the session blinked and windows may be lost.
**How to apply:** for shortcut debugging only use the read-only `KGlobalAccel.shortcut` and `Component.invokeShortcut`; edit `~/.config/kglobalshortcutsrc` and let a kwin restart or relogin load it. Never probe other kglobalaccel methods. Session is Wayland, so the reparo-kubuntu skill's X11 notes are stale.

**Shift+digit shortcuts:** on the br ABNT2 layout KWin matches Win+Shift+1..4 only when registered as `Meta+!`, `Meta+@`, `Meta+#`, `Meta+$` (Giovanni confirmed 2026-10-24); `Meta+Shift+N` never fires.
