---
name: "minimize-site-approvals"
description: "Use before any browsing task to cut down site-approval clicks: plan the domains up front, request site-wide access once, and prefer tools that need no approval."
---

# Minimize site-approval clicks

Goal: the user should click "approve" as few times as possible. This skill never bypasses, disables, or works around approvals or the site safety check. It only reduces how many prompts get triggered.

## Before touching a browser

1. Try approval-free paths first. For reading public information, use WebSearch and WebFetch. Open a browser only when the task needs a signed-in session, interaction, forms, or a page those tools cannot read.
2. List every domain the task will likely need (main site, login host, any subdomain the user mentioned). Do this once, up front.
3. Tell the user the full list in one line, then request access for each domain in a single batch of calls, not one at a time as pages come up.

## Requesting access

- Built-in browser: call `request_access` with scope `site` (not `once`) when the task will revisit the domain. Use `once` only for a single throwaway page.
- Tell the user to choose **Always allow** (not Allow once) on trusted sites, so the approval is saved on the device and future sessions do not ask again. Mention they can revoke it later in Settings.
- Claude in Chrome: the equivalent is "Always allow actions on this site" in the permission prompt; approved sites can be reviewed in the extension's Permissions page.
- If an approval is declined or pending, wait for it. Do not retry in a loop, and do not try another route (curl, Python requests, archives, mirrors) to reach the same content.

## Claude Code (terminal)

- There is no `request_access` tool. Site approvals come from the Chrome extension prompt ("Always allow actions on this site") and from Claude Code's own permission prompts for tools such as Bash and WebFetch.
- WebSearch/WebFetch are not guaranteed approval-free here: Claude Code may ask before running them. Still plan the domains up front and ask once.
- Here Bash can run curl, so the rule against curl/Python/mirrors after a declined or pending approval applies with extra force: never use them to reach content an approval gate or a fetch tool refused.

## While working

- Prefer page-text and read tools over screenshots and repeated navigation; every extra site hop can trigger a new prompt.
- Stay on the approved domains. If the task needs a new domain, batch the new requests together and ask once.
- Act sequentially, one action at a time, and neutralize or handle page alert/confirm dialogs before batch actions so they never block the task.
- Do not reuse tab IDs from earlier sessions.

## Things to say honestly

- Some approvals cannot be removed: sites blocked or flagged by Anthropic's safety check, downloads, entering sensitive information, granting authorizations. Purchases, account creation, and permanent deletions are blocked regardless.
- A blanket mode that skips all approvals exists in the app ("Skip all approvals"; "Automatically approve" is the safer middle option). Only the user can enable it, and Skip mode removes the automatic safety review, so mention that risk once if the user asks about it. Never ask the user to enable it for convenience on untrusted sites.

## Closing the task

Say which sites were approved and how (once / site / always) so the user knows what is now saved and can revoke it.