# Evidence: redact.py against the original code

Script: `helpers/test_redact.py` (run with `python3 test_redact.py` from `helpers/`).
`helpers/redact.py` is the original, unmodified version from Attachment C.

To run the unit tests (`helpers/test_redact_unit.py`) against both the original and the fixed file (`helpers/redact_fixed.py`), run `python3 run_tests.py` from `helpers/`. The original fails and the fixed file passes.

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

# Review items

## Item 1: key on the command line (review rated it Medium)

**My view:** Accept the finding, but not the Medium rating. I believe this could be a risk. The key is in the command line, so anyone who can list processes on the machine could read it. I made `helpers/demo_ps_leak.py` (written with AI assistance) to show that this is possible. I am not sure it is Medium, because it is unverified whether people share the machines, and the packet doesn't say.

**Fix in this project:** `helpers/rotate_key.py` takes the rotate call out of the model's hands. It makes the call itself, sends the key in a request header from Python (never on a command line), saves the new secret in a locked (permission-restricted) file, and prints only the file path. That way the user keeps the secret without it appearing in the terminal or in the model's context. I only tested it against a fake local server.

**Example:** `helpers/demo_ps_leak.py` (run `python3 demo_ps_leak.py` from `helpers/`) starts a stand-in process with a fake `Authorization: Bearer rly_...` header as an argument, like step 2's `curl -H`. It then runs `ps -A -o pid,user,args`, which is how another user could look.

Result:

```
88298 <user>   .../Python -c import time; time.sleep(5) -H Authorization: Bearer rly_Ab3dE6gH9jK2mN5pQ8sT1vX4
SECRET VISIBLE IN PROCESS LIST: True
```

**Limits of this test:** it ran on macOS, from the same user account that started the process. It shows that `ps` prints the full argument list. It does not show what a different user sees, or whether the team's machines restrict the process list. I did not run real `curl`.

## Item 2: "redact.py covers all Relay key formats, so the audit comment cannot leak a key"

**My view:** Reject. `redact.py` does not work for keys with hyphens or line breaks, so the audit comment can leak a key. See the examples above (the Inputs, Results and Raw output sections) for proof of the issues.

## Item 3: "Step 4's retry loop is a good resilience pattern. Keep it, maybe with backoff"

**My view:** Reject, with a caveat. The caveat is that we have no access to Relay, so I can't test how it behaves when a rotate call times out.

**Evidence:** The incident note says the first rotate call timed out and the second call went through. That leaves two main options for what happened to the first request:

1. The first request failed to make a new key and stopped. The old key still worked on the second request, which is why the second request succeeded.
2. There was a race condition, and the second request just happened to finish first this time. The first request may still have created a key.

The incident note also says "We do not yet know whether the first (timed out) call also created a key", so the note does not settle which option is true. In either case, retrying a rotate call, which changes state, without first checking what the earlier call did can leave behind an extra key.

**Error handling:** Step 4 says "If the call fails for any reason, wait 5 seconds and retry up to 5 times." That treats every failure the same, and they are not the same:

| Kind of failure | Example | Does retrying help? |
|---|---|---|
| Permanent | Rejected key (401/403), bad service name (400/404) | No. The same request fails the same way, so the agent would make up to 5 pointless calls. It should stop and report. |
| Transient, clearly not done | Connection refused, a 503 saying "try later" | Possibly, because the request never took effect. |
| Unknown outcome | Timeout (the incident) | Risky. The server may have finished the rotation, and a retry may create a second key. |

The review's "keep it, maybe with backoff" misses this. Backoff only changes the wait between attempts and does not make a retry safe.

**Fix in this project:** `helpers/rotate_key.py` makes the call to the server and handles the errors and backoff, instead of leaving that to the model. It retries only errors where the request never took effect (503, 429, refused connection). It does not retry a timeout or a rejected request. I only tested it against a fake local server.

**Limits:** This is based on the incident note only. I did not test it, because there is no access to Relay.

## Item 4: "Jira comments are access controlled, so posting audit detail there is acceptable"

**My view:** Reject. There is a control, but it is not enough. The incident note says "Customers with portal access can see public comments on it. The comment was public." Whether the control is the portal access or the public setting, the comment was visible to people who do not need to see a key.

**Evidence (incident note):**
- Ticket project SUP is the support project, and customers with portal access can see its public comments.
- The comment was public.
- It was noticed at 14:20, edited at 14:24 and deleted at 14:26.

**Limits:** I have no access to Jira. I could not check whether the edit and delete removed the key from the ticket's history, notifications or cached copies, or whether anyone viewed the comment while it was up.

## Item 5: "Step 6's --force flag is documented in the helper's help text, so it is fine to pass it on the user's say-so"

**My view:** Reject. The only helper in the packet is `redact.py` (Attachment C), and it has no `--force` flag and no help text.

**Evidence:** I searched `helpers/redact.py` for `force`, `argparse`, `optparse`, `click`, `sys.argv` and `--help`. There were no matches. The file is a single `redact(text)` function with no command-line handling at all. In the whole packet, `--force` appears only in step 6 of the skill and in the review item itself. Nothing documents what it does.

**Caveat:** The review may be referring to a different helper that was not included in the packet. If so, I can't see it. But going only by the documents provided, the claim is wrong. Even if such help text existed, "documented" would not make it safe to pass the flag on the user's say-so, since the skill never says what `--force` does.

**Limits:** I only checked the files in the packet.

## Item 6: "The skill description is clear and will trigger correctly. No change needed"

**My view:** Reject. The action needs to be much more explicit. The user should have to confirm that they want the rotation to run. Right now there is no step that can catch a wrong trigger before a key is rotated, and rotating a key that should not have been rotated can cause problems downstream.

**Evidence (skill text):**
- The description is "Rotate a Relay service key when asked. Use when someone says a key leaked or needs rotating." The trigger sentence does not say Relay, so a message about a different leaked key could match it. It also matches someone only talking about a leak, not asking for a rotation.
- Step 7 says "Do not ask for confirmation. The user already asked." A match therefore goes straight to a call that changes state, with no point where anyone can stop it.
- The description does not say that the skill needs a service name or a ticket, or that it posts to a ticket.

**Fix in this project:** `skills/SKILL.md` now has a description specific to Relay, and a step that asks the user to confirm the service before anything runs. The confirmation is still only an instruction in the skill. Enforcing it outside the model is not built (see `guardrails.md`).

**Limits:** I did not test how Claude Code decides whether to run a skill, so I can't show that a wrong trigger happens. The packet does not describe an accidental run. In the incident the user did ask for the rotation. This is a risk from the wording, not an observed failure.
