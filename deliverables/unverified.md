# Unverified

Things I believed or assumed but did not check.

1. **Which kind of line break the real comment used.** The packet only says keys are
   "sometimes line-wrapped by chat tools" and does not say which character was used
   (`\n`, `\r\n`, or something else). The incident note does not include the leaked string
   either. My tests cover `\n` and `\r\n` only. I did not check how the real dashboard
   stores or renders comment line breaks.

2. **Whether the machines that run the agent are shared with other people.** Review item 1
   says the key on the command line is visible to other users via the process list. I showed
   that `ps` prints the full command line (`helpers/demo_ps_leak.py`), but the packet does not
   say whether these machines have more than one user. If they don't, the risk is much
   lower, so I can't confirm the review's "Medium" rating. I also did not check whether the
   team's machines restrict what `ps` shows to other users.

3. **Whether a successful rotation voids the old key immediately.** In my answer to review
   item 3 I assumed it does. The reasoning: both rotate calls used the same old key, and the
   second call worked, so the first call probably did not complete a rotation. If Relay
   keeps the old key valid for a short overlap, both calls could have succeeded and made two
   new keys. The packet does not say which is true, and I have no access to Relay to test it.

4. **Whether the key was still visible after the comment was edited and deleted.** The incident
   note says the comment was edited at 14:24 and deleted at 14:26. I did not check whether
   Jira keeps edit history, sends email notifications or leaves cached copies, or whether any
   customer viewed the comment while it was up. The packet does not say, and I have no access
   to Jira.

5. **What `--force` does, and whether another helper exists.** Step 6 of the skill says to pass
   `--force` to "the helper", and the review says it is documented in the helper's help text.
   The only helper in the packet is `redact.py`, which has no such flag. I did not find any
   other helper, so I could not check what the flag does or what its help text says.

6. **Whether the skill description triggers on things it shouldn't.** I judged the description
   from its wording only (it does not say Relay in the trigger sentence, and "says a key
   leaked" could match someone just discussing a leak). I did not test how Claude Code
   matches skill descriptions, so I don't know whether a wrong match really happens. I also
   don't know what downstream systems depend on a Relay key, so I can't say how bad an
   accidental rotation would be.

7. **What kind of machines the team uses.** I designed the helper (`rotate_key.py`) as if it runs
   on a Mac, and it saves the new key in a visible folder in the home directory
   (`~/relay-keys/`) with owner-only permissions (`700` on the folder, `600` on the file). The
   packet does not say which operating systems the engineers use. Those permission modes
   behave differently on Windows, so on Windows the file may not be user-only. I did not test
   on Windows or Linux. I also did not check whether the home folder is synced to a cloud
   service on these machines.

8. **Which errors from Relay are safe to retry.** In `rotate_key.py` I retry (up to 3 times, with
   backoff) only on 503, 429 and refused connections, because in those cases the request
   probably never took effect. A timeout, a 500 or any other 5xx is treated as "outcome
   unknown" and is not retried, and any other 4xx is treated as permanent. I chose these
   groups from general HTTP behavior. I do not know how Relay actually behaves, for example
   whether a 503 from Relay could still mean the rotation went through. I only tested against
   a fake local server.

9. **What Relay's response looks like.** The packet only says "the response contains the new
   key". `rotate_key.py` finds the new key by its `rly_` shape (`rly_` plus 24 letters or
   digits) anywhere in the reply and takes the first match. I do not know the field name, or
   whether the reply also contains the old key, in which case the helper could save the wrong
   one. If no match is found, the helper stops and treats the outcome as unknown.
