---
name: "minimize-site-approvals"
description: "Use before any browsing task to cut down site-approval clicks: plan the domains up front, request site-wide access once, and prefer tools that need no approval."
---

# Minimize site-approval clicks

Lineage: origin=gui; base=52547cd8127647409f6397067c9e7af5e903aa4c

Code version: adapted for Claude Code on the laptop from `gui/skills/minimize-site-approvals`. Edited only by Claude Code; the app keeps its own version.

Goal: the user should click "approve" as few times as possible. This skill never bypasses, disables, or works around approvals or the site safety check. It only reduces how many prompts get triggered.

## Before touching a browser

1. Prefer the cheapest path. For public pages, WebSearch and WebFetch avoid the browser, but in Claude Code they can still trigger a permission prompt, so they are not approval-free. Open Chrome only when the task needs a signed-in session, interaction, forms, or a page those tools cannot read.
2. List every domain the task will likely need (main site, login host, any subdomain the user mentioned). Do this once, up front.
3. Tell the user the full list in one line, so the approvals come in one go instead of one by one as pages come up.

## Approvals in Claude Code

- There is no `request_access` tool. Site access comes from the Claude in Chrome extension prompt: ask the user to choose "Always allow actions on this site" for trusted sites. Approved sites can be reviewed and revoked on the extension's Permissions page.
- Tool prompts (Bash, WebFetch, MCP tools) come from Claude Code's permission system. For repeated safe calls, offer to add an allow rule in settings (the `update-config` skill, or `/permissions`); never add one without the user's yes.
- If an approval is declined or pending, wait for it. Do not retry in a loop, and do not try another route to the same content. Bash can run curl, Python, wget or git here, so this rule matters more than in the app: never use them to reach a page that an approval prompt, the extension or a fetch tool refused.

## While working

- Prefer page-text and read tools over screenshots and repeated navigation; every extra site hop can trigger a new prompt.
- Stay on the approved domains. If the task needs a new domain, batch the new requests together and ask once.
- Act sequentially, one action at a time, and neutralize or handle page alert/confirm dialogs before batch actions so they never block the task (browser-automacao-segura).
- Do not reuse tab IDs from earlier sessions; call tabs_context_mcp first.

## Things to say honestly

- Some approvals cannot be removed: sites blocked or flagged by the extension's safety check, downloads, entering sensitive information, granting authorizations. Purchases, account creation, and permanent deletions stay with the user.
- Claude Code permission modes (for example auto mode, or broad allow rules) reduce prompts but also reduce review. Only the user changes them; mention the trade-off once if asked, and never push for it to save clicks on untrusted sites.

## Closing the task

Say which sites and tools were approved and how (once, always, or a settings rule) so the user knows what is now saved and can revoke it.
