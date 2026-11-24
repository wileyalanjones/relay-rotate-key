# Additional Question Answers

## 1. Redactor: which inputs would still get through?

My redactor (`helpers/redact_fixed.py`) only skips hyphens and line breaks (`\n`, `\r\n`, `\r`) inside a key, because those are the cases the instruction sheet mentioned. Any other character placed inside the key stops the match, so the key comes through unredacted.

I tried a key with one odd character in the middle (`helpers/test_redact_gaps.py`). All of these leaked:

| Character inserted | Result |
|---|---|
| space, tab, non-breaking space (NBSP) | leaked |
| Unicode hyphen (U+2010), en dash (U+2013) | leaked |
| zero-width space, soft hyphen, line separator (U+2028) | leaked |

Example: `rly_Ab3dE6gH9jK2‐mN5pQ8sT1vX4` (with a Unicode hyphen) comes out unchanged. The Unicode hyphen is the one I think is most likely in real use, because chat tools often swap `-` for a look-alike. Other things I didn't demo would also get through: a `+` or `**` inside the key, uppercase `RLY_`, and encoded or reversed keys.

**What I would change:**
- Widen the characters the pattern skips to all whitespace, all Unicode dashes and the invisible characters, and make it case-insensitive.
- Add one test per case above so they stay fixed.
- Accept that a regex can't catch encoded or deliberately obfuscated keys (base64, reversed). It is only a backstop.

**Why this is lower risk in my design:** the key never goes to the agent. `rotate_key.py` handles it, so the redactor only matters if a key leaks by accident, for example in an error message. The main protection is that structure. The redactor is a second layer.
