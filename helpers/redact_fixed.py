import re

# Hyphens and line breaks (\n, \r\n, \r) that a chat bot may insert into a key.
# They do not count towards the 24 characters of the key.
NOISE = r"(?:-|\r\n|\n|\r)*"

# "rly_" followed by 24 letters/digits, with optional noise between every character.
RLY_KEY = NOISE.join(["r", "l", "y", "_"] + ["[A-Za-z0-9]"] * 24)

PATTERNS = [
    re.compile(RLY_KEY),
    # Original was Bearer\s+[A-Za-z0-9._-]{20,}. Now a line break may follow any
    # token character, and line breaks do not count towards the 20 characters.
    re.compile(r"Bearer\s+(?:[A-Za-z0-9._-](?:\r\n|\n|\r)?){19,}[A-Za-z0-9._-]"),
]


def redact(text):
    for p in PATTERNS:
        text = p.sub("[REDACTED]", text)
    return text
