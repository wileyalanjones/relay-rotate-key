from redact_fixed import redact

# Fake key: "rly_" followed by 24 letters/digits, with one odd character in the middle.
# Each of these should be redacted. The ones marked LEAKED are not.
A, B = "rly_Ab3dE6gH9jK2", "mN5pQ8sT1vX4"

examples = {
    "space": " ",
    "tab": "\t",
    "non-breaking space (NBSP)": " ",
    "unicode hyphen (U+2010)": "‐",
    "en dash (U+2013)": "–",
    "zero-width space (U+200B)": "​",
    "soft hyphen (U+00AD)": "­",
    "line separator (U+2028)": " ",
}

for name, odd in examples.items():
    text = f"key: {A}{odd}{B}"
    out = redact(text)
    status = "redacted" if "rly_" not in out else "LEAKED"
    print(f"--- {name}: {status} ---")
    print("before:", repr(text))
    print("after: ", repr(out))
    print()
