---
name: "click-protocol"
description: "Use before multi-step clicking in web UIs with menus, dialogs, search results or media (YouTube Music, Spotify web): click by element ref, verify each step, avoid accidental playback."
---

# Click protocol (ref-first, verify every step)

Interop: role = cross-cutting; owns = click/verify protocol and YouTube Music add-to-playlist recipe; defers to = browser-automacao-segura (alerts, loops, destructive actions), minimize-site-approvals (domains and approvals), domain skills (formats); honors = reply-language rule, depth flags.

Origin: YouTube Music playlist build, 2026-10-10. Misclicks started music, a stale toast looked like success, coordinates broke between layouts.

## Rules, in order
1. Plan first: domains once (minimize-site-approvals); use a connector or API if one exists instead of the UI.
2. No raw coordinates when `find` or `read_page` can return a ref. Coordinates only for canvas-like pages: wait about 3 s for the window size to settle, screenshot, click immediately, verify. Layouts move targets (for example the side panel "Mehr von YouTube" present or absent).
3. Ref lifecycle: look up a ref only after the page settled, and confirm its description names the intended item (title), because `find` can describe the previous page right after a search. Refs are single-use: re-find after any navigation, search, menu open or dialog open. Several matches: pick by role (menuitem/button/link), visible, inside the open popup; never the first hit.
4. Actionability gate before every click (Playwright checks): exactly one match, visible, stable (wait 1.5 s after a menu or dialog opens), not covered, enabled.
5. One action, one verification. Cheapest proof first: new element via `find`, URL/title, text via JS or get_page_text; screenshot (scale 0.4) only when doubtful. No blind chains. Batches: at most 4 actions, only harmless steps, end with a check. Do not put `navigate` inside `browser_batch` (it failed here).
6. After typing in a search box and Return, wait until the first result title matches the query. If the first click seems ignored, click an empty toolbar area or use a ref; do not repeat the same click.
7. Success needs fresh evidence. A toast can be stale. Proof = re-read the target (playlist page text, header count) after the action. A "already in playlist" toast means the add had worked earlier, not an error.
8. Media guard before any session on a player site: `setInterval(()=>{const v=document.querySelector('video');if(v&&!v.paused)v.pause()},300)`. Reinstall after a full page load. Never JS-click the first `button` of a result card (it is Play). If the user says stop the audio, pause at once.
9. Privacy defaults: new playlists default to Public on YouTube Music; set Privat/Private before Create unless the user asked for public.
10. Navigation fails ("failed in the extension"): do not retry blindly. Check tabs_context, then use the in-page search box or a link click. `location.href` from JS did not navigate here.
11. Lazy lists: JS scrolling does not load more in a background tab; use real scroll actions (about 100 items per load) or sample, and say it is partial. For large libraries tell the user the count read vs total.
12. Downloads land on the user's computer, not in the cloud workspace: say so before clicking Download and ask for the file or use the live site instead. (Claude Code on the laptop) Downloads land in ~/Downloads and can be read directly; still name the file you expect and confirm it exists there before relying on it.
13. Stop rule: two failed tries on the same step -> screenshot, report, ask. Do not guess coordinates.
14. Finish with a reload and recount (browser-automacao-segura, item 6).

## Recipe: add a song to a YouTube Music playlist (German labels; English: Action menu, Add to playlist)
1. Search box: select text, type query, Return, wait for result card whose title matches.
2. `find` "Aktionsmenü button in the top result card titled <title>"; check the subtitle says Titel/Song, not artist or video; click the ref.
3. `find` the menuitem "Zu Playlist hinzufügen" (role menuitem, in the open popup); click it.
4. `find` the link with the playlist name in the dialog; click it. Toast "Gespeichert in <name>" is a hint, not proof.
5. Every 5 songs and at the end: open the playlist and read the header "N Titel" via get_page_text. The DOM list also mixes suggestion rows, so trust the header and page text.
Create playlist: dialog -> "Neue Playlist" -> title -> Sichtbarkeit = Privat -> Erstellen.