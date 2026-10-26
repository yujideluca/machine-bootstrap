# Architecture decision records

One short file per structural decision (format: [MADR](https://adr.github.io/madr/), trimmed). Copy
`0000-template.md`, take the next number, link it from the decision log in `DESIGN.md`. An accepted ADR is never
rewritten: a new decision supersedes it.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-record-decisions.md) | Record architecture decisions as ADRs | accepted |
| [0003](0003-program-measures-skill-judges.md) | A program measures and blocks, a skill judges and proposes | accepted |
| [0002](0002-python-stdlib-and-bash.md) | Write the tool in Python (standard library only) with a small Bash starter | accepted |
| [0004](0004-allow-list-and-scanner.md) | Capture by allow-list, and refuse anything the secret scanner flags | accepted |
| [0005](0005-secrets-passphrase-two-places.md) | Keys and logins in one passphrase-encrypted archive, stored in two places | accepted |
