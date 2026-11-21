# Relay rotate-key take-home

## Run the tests

From the `helpers/` folder (Python 3, nothing to install):

```
python3 run_tests.py
```

This runs the same unit tests (`helpers/test_redact_unit.py`) against the original filter (`helpers/redact.py`) and the fixed one (`helpers/redact_fixed.py`), then prints a summary. The original fails (7 of 7 tests) and the fix passes.

To also run your own inputs:

```
python3 run_tests.py --inputs my_inputs.json
```

The file is a JSON list of cases like `{"name": "...", "text": "...", "secret": "..."}`. `text` is what goes through the filter and `secret` is the unbroken key hidden in it. A case fails if any 4-character piece of the secret is still in the output. A case with no `secret` must come back unchanged. See `helpers/example_inputs.json` for examples.

## Where each deliverable is

| # | Deliverable | Where |
|---|---|---|
| 1 | Decision memo | `deliverables/decision_memo.md` |
| 2 | Corrected skill | `skills/SKILL.md` (the original draft is kept as `skills/SKILL-v0.3.md`) |
| 2 | Replacement helpers | `helpers/rotate_key.py` (makes the call, saves the key) and `helpers/redact_fixed.py` (fixed filter) |
| 3 | Evidence: inputs, results, the six review items | `deliverables/evidence.md` |
| 3 | Tests that fail today and pass after the fix | `helpers/test_redact_unit.py`, run with `helpers/run_tests.py` |
| 3 | Other evidence scripts | `helpers/test_redact.py` (prints the before and after for each input) and `helpers/demo_ps_leak.py` (shows a key on a command line is visible in the process list) |
| 4 | Guardrail design | `deliverables/guardrails.md` |
| 5 | Rollout plan | `deliverables/rollout.md` |
| 6 | Unverified list | `deliverables/unverified.md` |
| 7 | AI-use note and transcripts | *to be added* |
| 8 | Decision log | `deliverables/decision_log.md` |
| 9 | Screen recording | *to be added* |

The packet and its attachments are in `documents/`.

## Notes

- `helpers/redact.py` is the original filter and is unchanged, so the tests can show it failing.
- `helpers/rotate_key.py` was only tried against a fake local server. Its tests are not part of the repo.
