# Decision memo

## Decision

After reviewing the skill, helper files, incident documents, and the reviewer's analysis, I recommend blocking v0.3 and shipping a corrected version to a pilot group for further testing. The main reason for this decision is that the skill automatically posts a comment to the SUP public dashboard that contains the newly generated key and relies solely on a filter program to remove it. As the incident showed, this filter is not robust enough to prevent keys from being posted on the site. Luckily, a reviewer noticed the string and rotated it relatively quickly, but we can't guarantee we will be as fortunate next time. That is why I recommend immediately blocking the skill and running a temporary manual key rotation process while my corrected version is sent to a pilot group for testing. The old skill cannot remain in use, as it has proven unreliable. I have included my new version of the skill in the attached documents.

## What I need from you

- Approve pulling v0.3 from production now.
- Approve manual key rotation for real keys until the new skill passes a pilot.
- Approve a pilot of the new skill on a test service, run by the development team or reviewers who know the systems.
- Name an owner for the manual rotation process.

## What went wrong

- A request that timed out was retried automatically. It is unknown whether the first attempt created an extra key.
- The agent posted the full request and response to a public support ticket. The filter meant to remove keys missed one. My tests show it misses keys that contain hyphens or line breaks.
- The skill also passed the key through the model and the command line, and never asked the user to confirm.

## What I changed

- Pulled v0.3, with manual rotation for real keys in the meantime.
- A new helper script makes the call itself, saves the new key to a file only the user can read, and removes keys from what the agent sees. A fixed filter handles hyphens and line breaks.
- The new skill asks the user to confirm and only applies to Relay keys. The tests fail on the original filter and pass on the fix.

## What I chose not to change

- Extra key formats beyond hyphens and line breaks, such as spaces or encoded keys.
- The fixed filter sometimes removes a few extra words after a wrapped key. I accepted this as the safer side.

## The six review items at a glance

| # | Review item | My call | Why |
|---|---|---|---|
| 1 | Key on the command line | Accept, severity unconfirmed | `ps` shows it. Whether machines are shared is unknown. |
| 2 | `redact.py` covers all formats | Reject | It leaks keys with hyphens or line breaks. |
| 3 | Retry loop is good | Reject | It retries on any error, and after a timeout a key may already exist. |
| 4 | Jira is access controlled | Reject | The comment was public to customers with portal access. |
| 5 | `--force` is documented | Reject | The only helper provided has no such flag. |
| 6 | Description triggers correctly | Reject | It is too broad, and nothing asks the user to confirm. |

## What I couldn't verify

- Everything was tested against a fake local server, not Relay.
- Whether the machines are shared, and what Relay's response looks like.
- **What I would check first:** whether the old key is void immediately after a rotation, and whether the incident's timeout was a failed request or a race condition.

## Where to find more details

- `deliverables/evidence.md`: the test inputs and results, and my view on each review item.
- `deliverables/guardrails.md`: what the tool enforces and what it can't catch.
- `deliverables/rollout.md`: the pilot, the stress test and the rollback.
- `deliverables/unverified.md`: everything I believed but did not check.
- `helpers/` and `skills/`: the code and the new skill.
