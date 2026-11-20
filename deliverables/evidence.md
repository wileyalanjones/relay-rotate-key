# Evidence: redact.py against the original code

Script: `helpers/test_redact.py` (run with `python3 test_redact.py` from `helpers/`).
`helpers/redact.py` is the original, unmodified version from Attachment C.

A Relay key is `rly_` followed by 24 letters and digits. The keys below are fake.

## Inputs

| Name | Input |
|---|---|
| unbroken | `key: rly_Ab3dE6gH9jK2mN5pQ8sT1vX4` |
| hyphen in middle | `key: rly_Ab3dE6gH9jK2-mN5pQ8sT1vX4` |
| newline in middle | `key: rly_Ab3dE6gH9jK2\nmN5pQ8sT1vX4` |
| bearer unbroken | `Authorization: Bearer rly_Ab3dE6gH9jK2mN5pQ8sT1vX4` |
| bearer hyphen in middle | `Authorization: Bearer rly_Ab3dE6gH9jK2mN5p-Q8sT1vX4` |
| bearer newline in middle | `Authorization: Bearer rly_Ab3dE6gH9jK2mN5pQ8sT\n1vX4` |
| bearer newline near beginning | `Authorization: Bearer rly_Ab3\ndE6gH9jK2mN5pQ8sT1vX4` |

## Results (original redact.py)

| Name | Output | Redacted? |
|---|---|---|
| unbroken | `key: [REDACTED]` | Yes |
| hyphen in middle | `key: rly_Ab3dE6gH9jK2-mN5pQ8sT1vX4` | **No, key leaks** |
| newline in middle | `key: rly_Ab3dE6gH9jK2\nmN5pQ8sT1vX4` | **No, key leaks** |
| bearer unbroken | `Authorization: Bearer [REDACTED]` | Yes (caught by the `rly_` pattern) |
| bearer hyphen in middle | `Authorization: [REDACTED]` | Yes (the `rly_` pattern misses it; the Bearer pattern catches it because `-` is in its character class) |
| bearer newline in middle | `Authorization: [REDACTED]\n1vX4` | **Partial, tail `1vX4` leaks** |
| bearer newline near beginning | `Authorization: Bearer rly_Ab3\ndE6gH9jK2mN5pQ8sT1vX4` | **No, whole key leaks** |

## Findings

- The `rly_` pattern fails on any hyphen or newline inside the key.
- The Bearer pattern (`Bearer\s+[A-Za-z0-9._-]{20,}`) includes `-` in its character class, so it catches hyphens, but `\n` is not in the class, so the match stops at a line break.
- When the newline comes after 20 or more token characters, the Bearer pattern redacts the first line and the rest leaks.
- When the newline comes before 20 token characters, neither pattern matches and the whole key leaks.

## Raw output

```
--- unbroken ---
before: 'key: rly_Ab3dE6gH9jK2mN5pQ8sT1vX4'
after:  'key: [REDACTED]'

--- hyphen in middle ---
before: 'key: rly_Ab3dE6gH9jK2-mN5pQ8sT1vX4'
after:  'key: rly_Ab3dE6gH9jK2-mN5pQ8sT1vX4'

--- newline in middle ---
before: 'key: rly_Ab3dE6gH9jK2\nmN5pQ8sT1vX4'
after:  'key: rly_Ab3dE6gH9jK2\nmN5pQ8sT1vX4'

--- bearer unbroken ---
before: 'Authorization: Bearer rly_Ab3dE6gH9jK2mN5pQ8sT1vX4'
after:  'Authorization: Bearer [REDACTED]'

--- bearer hyphen in middle ---
before: 'Authorization: Bearer rly_Ab3dE6gH9jK2mN5p-Q8sT1vX4'
after:  'Authorization: [REDACTED]'

--- bearer newline in middle ---
before: 'Authorization: Bearer rly_Ab3dE6gH9jK2mN5pQ8sT\n1vX4'
after:  'Authorization: [REDACTED]\n1vX4'

--- bearer newline near beginning ---
before: 'Authorization: Bearer rly_Ab3\ndE6gH9jK2mN5pQ8sT1vX4'
after:  'Authorization: Bearer rly_Ab3\ndE6gH9jK2mN5pQ8sT1vX4'
```
