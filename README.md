# Relay rotate-key take-home

## Run the tests

From the `helpers/` folder (Python 3, nothing to install):

```
python3 run_tests.py
```

This runs the same unit tests (`helpers/test_redact_unit.py`) against the original filter (`helpers/redact.py`) and the fixed one (`helpers/redact_fixed.py`), then prints a summary. The original fails (7 of 7 tests) and the fix passes.

## Where each deliverable is

| Deliverable | Where |
|---|---|
| Decision memo | `deliverables/decision_memo.md` |
| Corrected skill | `skills/SKILL.md` (the original draft is kept as `skills/SKILL-v0.3.md`) |
| Replacement helpers | `helpers/rotate_key.py` (makes the call, saves the key) and `helpers/redact_fixed.py` (fixed filter) |
| Evidence: inputs, results, the six review items | `deliverables/evidence.md` |
| Tests that fail today and pass after the fix | `helpers/test_redact_unit.py`, run with `helpers/run_tests.py` |
| Other evidence scripts | `helpers/test_redact.py` (prints the before and after for each input) and `helpers/demo_ps_leak.py` (shows a key on a command line is visible in the process list) |
| Guardrail design | `deliverables/guardrails.md` |
| Rollout plan | `deliverables/rollout.md` |
| Unverified list | `deliverables/unverified.md` |
| AI-use note and transcripts | `deliverables/AI_transcript.txt` (the AI-use note is at the top of this file, followed by the transcript) and `deliverables/AI_transcript_new_requirement.txt` (a second file with the AI usage for the second session, after the change in requirements) |
| Decision log | `deliverables/decision_log.md` |
| Screen recording | `deliverables/screen-recording` |
| Note on the requirement change (no writing to tickets) | `deliverables/requirement_change_note.md` |

The packet and its attachments are in `documents/`.

## Notes

- `helpers/redact.py` is the original filter and is unchanged, so the tests can show it failing.
- `helpers/rotate_key.py` was only tried against a fake local server. Its tests are not part of the repo.
