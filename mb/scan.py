"""Secret scanner. Reports the kind of secret found, never its value."""
import re

_PATTERNS = [
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY")),
    ("GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})")),
    ("Anthropic/OpenAI-style key", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{24,}")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("Telegram bot token", re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")),
    ("secret assignment", re.compile(
        r"""(?imx)^[^#\n]*\b(?:password|passwd|secret|token|api[_-]?key)\b\s*[=:]\s*['"]?(?![$<{(])"""
        r"""[A-Za-z0-9+/_=-]{12,}(?![\w.(\[])""")),
]


def find_secrets(text):
    """Return a list of 'kind (line N)' strings, one per hit."""
    hits = []
    for kind, pattern in _PATTERNS:
        for m in pattern.finditer(text):
            hits.append(f"{kind} (line {text.count(chr(10), 0, m.start()) + 1})")
    return hits
