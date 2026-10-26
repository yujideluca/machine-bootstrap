# ADR-0005: Keys and logins in one passphrase-encrypted archive, stored in two places

- **Status:** accepted
- **Date:** 2026-10-25
- **Type (ISO/IEC/IEEE 14764):** initial
- **Decided by:** Giovanni (SSD plus Google Drive for keys and settings, 2026-10-25)

## Context

Some things cannot be rebuilt from a recipe: the SSH and GPG keys, the GitHub, Claude, Codex and Telegram logins and,
above all, the Android release key `german-quiz-release.jks` with its password file (ADR-0004 of QuizApp: losing
the key means installed copies of the app can never be updated in place).

## Decision

- `mb secrets-backup` packs the files listed under `[secrets]` in `mb.toml` into a tar archive in memory and encrypts
  it with `gpg --symmetric` (AES-256, strong key derivation). The passphrase is typed by Giovanni at that moment
  (at least 12 characters, asked twice); it is never stored, never in an argument list or an environment variable.
- The archive is written to the SSD (found by its filesystem UUID, not a path) and uploaded to Google Drive with
  `rclone`. Right after writing, the archive is decrypted again and compared file by file with the originals; the
  copies are compared with each other and, for Drive, with `rclone check`.
- `secrets-restore` refuses to overwrite existing files unless told to (then it keeps `.mb-bak` copies) and
  forces owner-only permissions.

## Alternatives considered

- **Public-key encryption (`gpg` key pair or `age`)** — the private key would itself need a safe place; the passphrase
  lives in Giovanni's head.
- **A password manager export** — not scriptable, and not available on a bare machine.
- **Plain copy on the SSD** — a lost or stolen drive would expose every login.

## Consequences

If the passphrase is forgotten, the archive is unrecoverable: the passphrase must be kept somewhere safe that is not
this computer (written on paper). The archive must be refreshed after a key or login changes; `docs/RESTORE.md`
lists when. Google Drive holds only ciphertext.
